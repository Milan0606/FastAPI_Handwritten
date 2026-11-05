"""
Topic 3: Routes & HTTP Methods
==============================

Key Concepts Explained:
-----------------------
1. What is a Route?
   - A Route maps a URL path (like "/users") + an HTTP method (like GET or POST)
     to a specific Python function.
   - You declare routes using Python decorators:
     * @app.get("/path")     -> Read / Retrieve data
     * @app.post("/path")    -> Create new data
     * @app.put("/path")     -> Update / Replace existing data
     * @app.patch("/path")   -> Partially update existing data
     * @app.delete("/path")  -> Delete data

2. Why Different HTTP Methods?
   - Standard RESTful conventions allow the SAME path ("/users/1") to perform
     different actions based on the HTTP verb used:
     - GET /users/1    -> Fetch user 1
     - PUT /users/1    -> Overwrite user 1
     - PATCH /users/1  -> Update only user 1's email
     - DELETE /users/1 -> Delete user 1

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/03_routes_and_http_methods.py

Then visit Swagger UI to interact with all HTTP methods:
    http://127.0.0.1:8000/docs
"""

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="Topic 3: Routes & HTTP Methods Demo",
    description="Learn GET, POST, PUT, PATCH, and DELETE HTTP methods in FastAPI.",
    version="1.0.0",
)

# Simulated in-memory database
fake_users_db: dict[int, dict] = {
    1: {"name": "Alice", "role": "AI Engineer", "active": True},
    2: {"name": "Bob", "role": "Data Scientist", "active": True},
}


# Pydantic Schemas for Request Data
class UserCreate(BaseModel):
    name: str
    role: str
    active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    active: bool | None = None


# -------------------------------------------------------------------
# 1. GET Route: Fetch all users or a specific user
# -------------------------------------------------------------------
@app.get("/users", tags=["Users"], summary="GET: Retrieve all users")
def get_all_users():
    """Retrieve all users stored in the database."""
    return {"users": fake_users_db}


@app.get("/users/{user_id}", tags=["Users"], summary="GET: Retrieve user by ID")
def get_user_by_id(user_id: int):
    """Retrieve a single user by their ID."""
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return {"user_id": user_id, "data": fake_users_db[user_id]}


# -------------------------------------------------------------------
# 2. POST Route: Create a new user
# -------------------------------------------------------------------
@app.post(
    "/users",
    tags=["Users"],
    summary="POST: Create a new user",
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate):
    """Create a new user and add them to the database."""
    new_id = max(fake_users_db.keys(), default=0) + 1
    fake_users_db[new_id] = user.model_dump()
    return {
        "message": "User created successfully!",
        "user_id": new_id,
        "data": fake_users_db[new_id],
    }


# -------------------------------------------------------------------
# 3. PUT Route: Complete update/replacement of an existing user
# -------------------------------------------------------------------
@app.put("/users/{user_id}", tags=["Users"], summary="PUT: Replace existing user")
def replace_user(user_id: int, user: UserCreate):
    """Replace an existing user's complete data with new data."""
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    fake_users_db[user_id] = user.model_dump()
    return {"message": f"User {user_id} updated completely", "data": fake_users_db[user_id]}


# -------------------------------------------------------------------
# 4. PATCH Route: Partial update of a user
# -------------------------------------------------------------------
@app.patch("/users/{user_id}", tags=["Users"], summary="PATCH: Partially update user")
def partial_update_user(user_id: int, user_update: UserUpdate):
    """Update only the fields that were provided (e.g. change just role or active status)."""
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    stored_user = fake_users_db[user_id]
    # Update only fields provided by user
    update_data = user_update.model_dump(exclude_unset=True)
    stored_user.update(update_data)
    return {"message": f"User {user_id} partially updated", "data": stored_user}


# -------------------------------------------------------------------
# 5. DELETE Route: Delete a user
# -------------------------------------------------------------------
@app.delete("/users/{user_id}", tags=["Users"], summary="DELETE: Remove user")
def delete_user(user_id: int):
    """Delete a user by ID."""
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    deleted_user = fake_users_db.pop(user_id)
    return {"message": f"User {user_id} deleted successfully", "deleted": deleted_user}


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 3 Demo Server Starting!")
    print("👉 Test GET, POST, PUT, PATCH, and DELETE in Swagger UI:")
    print("   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("03_routes_and_http_methods:app", host="127.0.0.1", port=8000, reload=True)
