"""
Topic 1: What is FastAPI & Why FastAPI?
=======================================

Key Concepts Explained:
-----------------------
1. What is FastAPI?
   - A modern, high-performance web framework for building APIs in Python.
   - Created by Sebastián Ramírez.
   - Built on top of two battle-tested libraries:
     * Starlette: Handles web routing, requests, responses, WebSockets.
     * Pydantic: Handles data validation, serialization, and type conversion.

2. Why FastAPI?
   - Extremely Fast: Performance on par with NodeJS and Go (via Starlette & ASGI).
   - Easy to learn & write: Minimal boilerplate code.
   - Automatic Interactive Documentation:
     * Swagger UI at: http://127.0.0.1:8000/docs
     * ReDoc at:      http://127.0.0.1:8000/redoc
   - Python Type Hints: Autocompletion, error detection before running, and auto-validation.
   - The Go-To framework for AI/ML: Industry standard for serving LLMs, LangChain/LlamaIndex agents, and RAG pipelines.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/01_what_is_fastapi.py

Then visit:
    - Root URL:     http://127.0.0.1:8000/
    - Interactive Docs (Swagger UI): http://127.0.0.1:8000/docs
    - Alternate Docs (ReDoc):        http://127.0.0.1:8000/redoc
"""

import uvicorn
from fastapi import FastAPI

# 1. Create the FastAPI app instance
app = FastAPI(
    title="Topic 1: What & Why FastAPI Demo",
    description="Demo showing the core purpose of FastAPI and automatic documentation.",
    version="1.0.0",
)


# 2. Define a simple GET route
@app.get("/", summary="Welcome Endpoint", tags=["General"])
def read_root():
    """
    Root endpoint demonstrating a simple JSON response.
    Notice how FastAPI automatically converts Python dictionaries into JSON!
    """
    return {
        "framework": "FastAPI",
        "creator": "Sebastián Ramírez",
        "built_on": ["Starlette", "Pydantic"],
        "message": "Welcome to FastAPI! Visit /docs to test this interactively in your browser.",
    }


# 3. Example demonstrating automatic type hints & validation
@app.get("/greet/{name}", summary="Type Hints & Input Demo", tags=["General"])
def greet_user(name: str, age: int | None = None):
    """
    FastAPI reads Python type annotations:
    - `name: str` -> Must be a string.
    - `age: int | None = None` -> Optional integer.
    If you pass age='abc', FastAPI automatically returns a 422 Validation Error!
    """
    response = {"greeting": f"Hello, {name}!"}
    if age is not None:
        response["age"] = age
        response["message"] = f"You are {age} years old."
    return response


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 1 Demo Server Starting!")
    print("👉 Open in your browser:")
    print("   • API Root:     http://127.0.0.1:8000/")
    print("   • Swagger UI:   http://127.0.0.1:8000/docs")
    print("   • ReDoc:        http://127.0.0.1:8000/redoc")
    print("=" * 60 + "\n")
    uvicorn.run("01_what_is_fastapi:app", host="127.0.0.1", port=8000, reload=True)
