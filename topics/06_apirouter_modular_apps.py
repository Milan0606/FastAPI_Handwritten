"""
Topic 6: APIRouter & Modular API Architecture
==============================================
(Reference: Page 4, Section 14 of the Notes)

Key Concepts Explained:
-----------------------
1. Why APIRouter?
   - In production applications, keeping all routes inside a single `main.py`
     makes code unmaintainable and cluttered.
   - `APIRouter` allows you to split routes into clean, modular files or modules
     (e.g., users router, chat router, items router).

2. Key Features of APIRouter:
   - `prefix`: Define a common base path (e.g. prefix="/users").
   - `tags`: Group endpoints together in Swagger UI documentation.
   - `dependencies`: Apply authentication or validation to all routes in a router at once.
   - `app.include_router(...)`: Mount routers cleanly onto the main FastAPI instance.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/06_apirouter_modular_apps.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException

# ===================================================================
# 1. Users Router (simulating a separate routers/users.py file)
# ===================================================================
users_router = APIRouter(
    prefix="/users",
    tags=["Users Module"],
)

fake_users_db = {
    1: {"id": 1, "name": "Alice", "role": "admin"},
    2: {"id": 2, "name": "Bob", "role": "user"},
}


@users_router.get("/", summary="List all users")
def list_users():
    return list(fake_users_db.values())


@users_router.get("/{user_id}", summary="Get user by ID")
def get_user(user_id: int):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_users_db[user_id]


# ===================================================================
# 2. Chat Router (simulating a separate routers/chat.py file)
# ===================================================================
chat_router = APIRouter(
    prefix="/chat",
    tags=["AI Chat Module"],
)


@chat_router.post("/", summary="Send message to AI")
def send_chat(message: str):
    return {
        "status": "success",
        "user_message": message,
        "ai_response": f"AI processed: '{message}'",
    }


# ===================================================================
# 3. Main FastAPI Application (simulating main.py)
# ===================================================================
app = FastAPI(
    title="Topic 6: APIRouter & Modular Architecture",
    description="Shows how to break an API into modular routers using APIRouter.",
    version="1.0.0",
)

# Mount the sub-routers onto the main app!
app.include_router(users_router)
app.include_router(chat_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Main App running with 2 modular sub-routers mounted (/users and /chat).",
        "docs": "Check http://127.0.0.1:8000/docs to see grouped tags!",
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 6: APIRouter Demo Starting!")
    print("👉 Notice how /users and /chat are organized into clean Swagger tags:")
    print("   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("06_apirouter_modular_apps:app", host="127.0.0.1", port=8000, reload=True)
