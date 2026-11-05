"""
Topic 2: FastAPI Application Structure
======================================

Key Concepts Explained:
-----------------------
1. What is the FastAPI Application Instance?
   - In FastAPI, everything starts with: `app = FastAPI(...)`
   - This `app` object is the central registry for:
     * Routes & Endpoints
     * Application metadata (title, version, description)
     * Middleware (CORS, authentication, logging)
     * Lifespan events (startup & shutdown database connections or loading AI models)

2. The Entry Point:
   - When an HTTP request comes in from a client (Browser, Mobile App, AI Agent),
     the ASGI server (Uvicorn) forwards it to this `app` instance.
   - The `app` looks up matching route paths and executes the corresponding endpoint function.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/02_app_structure.py

Then visit:
    - Root URL:     http://127.0.0.1:8000/
    - Info URL:     http://127.0.0.1:8000/info
    - Swagger UI:   http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI


# 1. Lifespan context manager: Handles Startup and Shutdown logic
# (Commonly used in AI projects to load model weights on startup and unload on shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🟢 [STARTUP] Application is booting up... (e.g., connect DB, load ML models)")
    yield
    print("🔴 [SHUTDOWN] Application is shutting down... (e.g., disconnect DB, free memory)\n")


# 2. Main FastAPI Application Instance
# You can customize application-level metadata here:
app = FastAPI(
    title="Topic 2: Application Structure & Configuration",
    description="This demo illustrates how the FastAPI application instance acts as the main hub.",
    version="2.0.0",
    docs_url="/docs",  # Customize Swagger UI URL path
    redoc_url="/redoc",  # Customize ReDoc URL path
    lifespan=lifespan,  # Attach startup/shutdown lifecycle hooks
)


# 3. Defining routes directly on the application instance
@app.get("/", summary="Application Status")
def home():
    return {
        "status": "online",
        "app_instance": "FastAPI()",
        "role": "Central entry point for all incoming requests",
    }


@app.get("/info", summary="Application Metadata")
def app_info():
    """Returns metadata configured in the FastAPI() constructor."""
    return {
        "title": app.title,
        "version": app.version,
        "description": app.description,
        "docs_url": app.docs_url,
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 2 Demo Server Starting!")
    print("👉 Notice how FastAPI() configures the whole application.")
    print("👉 Open: http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("02_app_structure:app", host="127.0.0.1", port=8000, reload=True)
