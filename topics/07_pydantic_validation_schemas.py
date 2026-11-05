"""
Topic 7: Pydantic Validation, Schemas & response_model
======================================================
(Reference: Pages 5, 6, and 7 of the Notes)

Key Concepts Explained:
-----------------------
1. Pydantic BaseModel:
   - Defines the exact structure and types of incoming and outgoing data.
   - Automatically validates types, converts string numbers ("25" -> 25), and catches errors.

2. Request Schemas vs. Response Schemas (`response_model`):
   - Request Schema: What the client sends (e.g. `UserCreate` includes password).
   - Response Schema: What the client receives back (e.g. `UserResponse` hides the password!).
   - Using `response_model=UserResponse` guarantees sensitive data like passwords or internal hashes
     are NEVER leaked to the client.

3. Field Validation:
   - Use `Field(...)` to enforce constraints:
     * `min_length`, `max_length` for strings
     * `ge` (greater or equal), `le` (less or equal) for numbers
     * `pattern` (regular expression) for formats like phone numbers
     * `EmailStr` for valid email format

4. Nested Models & Serialization:
   - Embed sub-models (e.g., `Address` inside `UserProfile`).
   - `.model_dump()` converts Pydantic model to a standard Python dictionary.
   - `.model_dump_json()` converts to a JSON string.
   - `.model_validate(dict_data)` parses and validates raw dictionary into a model.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/07_pydantic_validation_schemas.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import uvicorn
from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="Topic 7: Pydantic Schemas & Data Validation",
    description="Demonstrating request validation, response filtering (response_model), and nested models.",
    version="1.0.0",
)


# ===================================================================
# 1. Nested Sub-Model
# ===================================================================
class Address(BaseModel):
    street: str = Field(..., example="100 Tech Blvd")
    city: str = Field(..., example="San Francisco")
    pincode: str = Field(..., pattern=r"^\d{5,6}$", example="94107")


# ===================================================================
# 2. Request Schema (Client sends this, including password)
# ===================================================================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, example="John Doe")
    age: int = Field(..., ge=18, le=100, description="Age must be between 18 and 100", example=25)
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=6, example="SuperSecret123!")
    role: str = Field(default="user", example="user")  # Default field
    address: Address | None = None  # Optional Nested Model


# ===================================================================
# 3. Response Schema (Hides the password, adds system ID & timestamps)
# ===================================================================
class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr
    role: str
    address: Address | None = None
    # NOTICE: 'password' is intentionally omitted here!


# Simulated Database
db_users: dict[int, dict] = {}


# ===================================================================
# 4. Route using Request and Response Schemas
# ===================================================================
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user (hides password in response)",
)
def register_user(user: UserCreate):
    """
    1. FastAPI parses incoming JSON and validates against `UserCreate`.
    2. If validation fails (e.g. age < 18 or invalid email), returns 422 immediately.
    3. We store the user (including password).
    4. FastAPI filters the returned object through `response_model=UserResponse`,
       stripping the sensitive password!
    """
    user_id = len(db_users) + 1
    user_record = {"id": user_id, **user.model_dump()}

    # Save to mock database
    db_users[user_id] = user_record

    # Return full record - FastAPI's response_model will automatically filter out 'password'
    return user_record


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Fetch user by ID (safe response)",
)
def get_user(user_id: int):
    if user_id not in db_users:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return db_users[user_id]


# ===================================================================
# 5. Serialization & Deserialization Utility Endpoint
# ===================================================================
@app.post("/demo/serialization", tags=["Serialization Demo"])
def demo_serialization(user: UserCreate):
    """
    Demonstrates Pydantic v2 core conversion methods:
    - model_dump(): model -> dict
    - model_dump_json(): model -> json string
    """
    as_dict = user.model_dump()
    as_json = user.model_dump_json()

    # Deserializing back into a model from dictionary:
    reconstructed_model = UserCreate.model_validate(as_dict)

    return {
        "as_dict_type": str(type(as_dict)),
        "as_json_string": as_json,
        "reconstructed_name": reconstructed_model.name,
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 7: Pydantic & response_model Demo Starting!")
    print("👉 Open Swagger UI: http://127.0.0.1:8000/docs")
    print("👉 Try submitting invalid data (like age: 10 or bad email) to see auto 422 errors!")
    print("=" * 60 + "\n")
    uvicorn.run("07_pydantic_validation_schemas:app", host="127.0.0.1", port=8000, reload=True)
