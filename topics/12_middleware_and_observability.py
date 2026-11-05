"""
Topic 12: Middleware, Request Tracing & Observability
=====================================================
(Reference: Pages 23, 24, 25, and 26 of the Notes)

Key Concepts Explained:
-----------------------
1. What is Middleware?
   - A function that runs BEFORE every request reaches your route, and AFTER the route returns its response.
   - Ideal for cross-cutting concerns: Request Timing, Logging, CORS, Security headers, and Tracing.

2. Request ID & Correlation ID:
   - `X-Request-ID`: Unique UUID generated for each individual request. Essential for debugging log streams.
   - `X-Correlation-ID`: Tracks a transaction across multiple microservices or distributed AI agents.

3. Performance Timing (`X-Process-Time`):
   - Computes execution duration (in seconds/ms) and attaches it to response headers.

4. Health-Check Endpoints:
   - `/health`: Liveness probe for Docker/Kubernetes/load balancers to ensure the web process is alive.
   - `/health/ready`: Readiness probe verifying downstream dependencies (Database, Redis, AI model servers).

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/12_middleware_and_observability.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import logging
import time
import uuid
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

# Setup standard logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [ReqID: %(name)s] %(message)s",
)
logger = logging.getLogger("api")

app = FastAPI(
    title="Topic 12: Middleware & Observability",
    description="Learn HTTP middleware, request tracing, execution timing, and health check endpoints.",
    version="1.0.0",
)


# ===================================================================
# 1. Custom HTTP Middleware: Tracing, Logging & Execution Timing
# ===================================================================
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    # A. Generate or extract Request ID and Correlation ID
    request_id = str(uuid.uuid4())
    correlation_id = request.headers.get("X-Correlation-ID", request_id)

    # Store in request state so any endpoint can access it
    request.state.request_id = request_id
    request.state.correlation_id = correlation_id

    # B. Record start time
    start_time = time.perf_counter()
    logger.info(f"➡️ Incoming Request: {request.method} {request.url.path} (ID: {request_id[:8]}...)")

    try:
        # C. Call the actual endpoint
        response: Response = await call_next(request)

        # D. Calculate execution duration
        process_time = time.perf_counter() - start_time
        logger.info(
            f"⬅️ Completed {request.method} {request.url.path} - Status: {response.status_code} in {process_time:.4f}s"
        )

        # E. Attach tracing headers to the response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        return response

    except Exception as exc:
        process_time = time.perf_counter() - start_time
        logger.error(f"❌ Unhandled Exception on {request.url.path} in {process_time:.4f}s: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error", "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )


# ===================================================================
# 2. Production Health Check Endpoints (Liveness & Readiness)
# ===================================================================
@app.get("/health", tags=["Health Checks"], summary="Liveness probe")
def liveness_check():
    """Lightweight check used by load balancers / Kubernetes to verify server is responding."""
    return {"status": "healthy", "service": "fastapi-demo"}


@app.get("/health/ready", tags=["Health Checks"], summary="Readiness probe")
def readiness_check():
    """Verifies that external resources (Database, AI providers, Cache) are reachable."""
    # Simulated dependency check
    database_ok = True
    ai_service_ok = True

    if not (database_ok and ai_service_ok):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": database_ok, "ai_service": ai_service_ok},
        )

    return {
        "status": "ready",
        "dependencies": {"database": "connected", "ai_models": "loaded"},
    }


# ===================================================================
# 3. Sample Business Route
# ===================================================================
@app.get("/demo/slow-computation", tags=["Demo"])
async def slow_computation(request: Request):
    """Inspect your browser network tab or curl response headers to see X-Process-Time and X-Request-ID!"""
    import asyncio
    await asyncio.sleep(0.2)
    return {
        "message": "Computation completed",
        "assigned_request_id": request.state.request_id,
        "correlation_id": request.state.correlation_id,
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 12: Middleware & Observability Demo Starting!")
    print("👉 Check response headers (X-Request-ID, X-Process-Time):")
    print("   curl -I http://127.0.0.1:8000/demo/slow-computation")
    print("👉 Swagger UI: http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("12_middleware_and_observability:app", host="127.0.0.1", port=8000, reload=True)
