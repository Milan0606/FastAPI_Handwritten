"""
Topic 11: Error Handling, Custom Exceptions & Resilient Retries
==============================================================
(Reference: Pages 20 and 21 of the Notes)

Key Concepts Explained:
-----------------------
1. Standard HTTPException:
   - Raised directly inside endpoints to stop processing and return standard HTTP errors (400, 404, 403, etc.).

2. Custom Business Exceptions & Exception Handlers:
   - Create custom Python exception classes (e.g. `InsufficientCreditsError`, `LLMQuotaExceededError`).
   - Use `@app.exception_handler(...)` to catch them globally and return uniform, branded error JSON.

3. Customizing Request Validation Errors (422):
   - By default, Pydantic 422 responses can be very verbose.
   - You can intercept `RequestValidationError` to format errors cleanly for frontend clients.

4. LLM & External Tool Failures (Timeouts & Retries):
   - External APIs (OpenAI, Anthropic, Weather API) can time out or rate-limit.
   - Using try/except blocks with exponential backoff retries and clear 504/503 status codes.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/11_error_handling_exceptions.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Topic 11: Error Handling & Resilience",
    description="Learn custom exceptions, global exception handlers, and retry policies for AI tools.",
    version="1.0.0",
)


# ===================================================================
# 1. Custom Exception Class
# ===================================================================
class InsufficientCreditsError(Exception):
    def __init__(self, required_credits: int, available_credits: int):
        self.required = required_credits
        self.available = available_credits
        self.message = f"Insufficient credits: Required {required_credits}, but you only have {available_credits}."
        super().__init__(self.message)


# ===================================================================
# 2. Custom Global Exception Handler
# ===================================================================
@app.exception_handler(InsufficientCreditsError)
async def insufficient_credits_handler(request: Request, exc: InsufficientCreditsError):
    """Intercepts InsufficientCreditsError across the entire app and formats standard JSON."""
    return JSONResponse(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        content={
            "error_code": "INSUFFICIENT_CREDITS",
            "message": exc.message,
            "details": {
                "required": exc.required,
                "available": exc.available,
                "recharge_url": "https://example.com/billing",
            },
        },
    )


# ===================================================================
# 3. Customizing Pydantic Validation Errors (422)
# ===================================================================
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Simplifies the default complex Pydantic validation error into a clean list."""
    clean_errors = []
    for err in exc.errors():
        field_name = " -> ".join(str(loc) for loc in err["loc"] if loc != "body")
        clean_errors.append({"field": field_name, "issue": err["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_type": "VALIDATION_ERROR",
            "message": "Input validation failed. Please correct the fields listed below.",
            "errors": clean_errors,
        },
    )


# ===================================================================
# 4. Schema and Endpoints
# ===================================================================
class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=5, example="Write an essay on AI")
    credits_to_use: int = Field(..., gt=0, example=10)


USER_CREDIT_BALANCE = 5  # User only has 5 credits


@app.post("/api/generate", tags=["Business Logic Errors"])
def generate_ai_content(req: GenerationRequest):
    """Endpoint that raises custom InsufficientCreditsError if user lacks funds."""
    if req.credits_to_use > USER_CREDIT_BALANCE:
        raise InsufficientCreditsError(
            required_credits=req.credits_to_use,
            available_credits=USER_CREDIT_BALANCE,
        )
    return {"status": "success", "result": f"Generated output for '{req.prompt}'"}


# ===================================================================
# 5. LLM Call with Exponential Backoff Retry & Timeout
# ===================================================================
@app.post("/api/llm/resilient-call", tags=["AI Tool Resilience"])
async def call_external_llm_with_retry(max_retries: int = 3):
    """
    Demonstrates handling flaky AI tool/API calls using exponential backoff retry.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            attempt += 1
            print(f"🔄 Attempt {attempt} to call LLM...")

            # Simulate network or rate-limit failure on first 2 attempts
            if attempt < 3:
                await asyncio.sleep(0.1)
                raise ConnectionError("Temporary upstream LLM 503 Overloaded")

            # Success on attempt 3
            return {"status": "success", "attempts": attempt, "response": "LLM responded successfully!"}

        except ConnectionError as err:
            if attempt >= max_retries:
                # All retries failed
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Upstream AI service unavailable after {max_retries} attempts: {str(err)}",
                )
            # Exponential backoff: sleep 2^attempt * 0.1s
            backoff_delay = (2 ** attempt) * 0.1
            await asyncio.sleep(backoff_delay)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 11: Error Handling & Resilience Demo Starting!")
    print("👉 Test custom 402 error, clean 422 error, and retry in Swagger UI:")
    print("   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("11_error_handling_exceptions:app", host="127.0.0.1", port=8000, reload=True)
