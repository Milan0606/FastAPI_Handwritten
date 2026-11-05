"""
Topic 8: Dependency Injection & Authentication (OAuth2, JWT, RBAC & API Keys)
=============================================================================
(Reference: Pages 8, 9, and 10 of the Notes)

Key Concepts Explained:
-----------------------
1. What is Depends()?
   - FastAPI's powerful Dependency Injection system.
   - Allows functions (endpoints) to declare what they need (DB session, current user, API key).
   - FastAPI automatically runs the dependency function before your endpoint and injects the result.
   - Eliminates code duplication and separates concerns cleanly.

2. API Key Authentication:
   - Uses `APIKeyHeader(name="X-API-Key")`.
   - Validates service-to-service calls or internal microservice requests.

3. OAuth2 & JWT (JSON Web Tokens):
   - `OAuth2PasswordBearer(tokenUrl="/token")`: Tells Swagger UI where to obtain tokens.
   - JWT structure: Header.Payload.Signature.
   - Stateless authentication: The server doesn't need to store sessions; it cryptographically verifies the token!

4. RBAC (Role-Based Access Control):
   - Restricting endpoints based on user roles (e.g. "admin", "manager", "user").

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/08_dependency_injection_auth.py

Then visit:
    http://127.0.0.1:8000/docs
    - Use the green "Authorize" button in Swagger UI to test OAuth2 login!
"""

from datetime import datetime, timedelta, timezone
import jwt
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI(
    title="Topic 8: Dependency Injection & Authentication",
    description="Learn Depends(), API Keys, OAuth2 with JWT, and Role-Based Access Control (RBAC).",
    version="1.0.0",
)

# JWT Secret & Configuration
SECRET_KEY = "my_super_secret_jwt_signing_key_for_demo_purposes"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock User Database
fake_users_db = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Admin",
        "password": "secretpassword",
        "role": "admin",
    },
    "bob": {
        "username": "bob",
        "full_name": "Bob Normal",
        "password": "secretpassword",
        "role": "user",
    },
}

# Schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ===================================================================
# 1. JWT Helper Functions
# ===================================================================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ===================================================================
# 2. Dependency: Get Current Authenticated User from JWT
# ===================================================================
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise credentials_exception
        return fake_users_db[username]
    except jwt.PyJWTError:
        raise credentials_exception


# ===================================================================
# 3. Dependency Factory: Role-Based Access Control (RBAC)
# ===================================================================
def require_roles(allowed_roles: list[str]):
    """Returns a dependency function that enforces specific user roles."""
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of {allowed_roles} roles. Your role is '{current_user.get('role')}'.",
            )
        return current_user
    return role_checker


# ===================================================================
# 4. Dependency: API Key Header Validation
# ===================================================================
VALID_API_KEY = "sk-fastapi-demo-secret-key-12345"


def verify_api_key(api_key: str | None = Security(api_key_header)):
    if api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )
    return api_key


# ===================================================================
# 5. OAuth2 Login Route (Generates JWT)
# ===================================================================
@app.post("/token", tags=["Authentication"], summary="Login to get JWT access token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password. (Hint: Try user 'alice' or 'bob' with password 'secretpassword')",
        )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ===================================================================
# 6. Protected Routes using Depends()
# ===================================================================
@app.get("/users/me", tags=["Protected Endpoints"], summary="Get profile of logged-in user")
def read_current_user(current_user: dict = Depends(get_current_user)):
    """Any authenticated user (alice or bob) can access this."""
    return {"status": "authenticated", "user": current_user}


@app.get("/admin/dashboard", tags=["RBAC (Roles)"], summary="Admin-only endpoint")
def admin_dashboard(admin_user: dict = Depends(require_roles(["admin"]))):
    """Only users with role='admin' (alice) can access this! Bob will receive 403 Forbidden."""
    return {
        "message": f"Welcome to the Admin Portal, {admin_user['full_name']}!",
        "system_metrics": {"server_load": "12%", "active_llm_workers": 4},
    }


@app.get("/external/metrics", tags=["API Key Security"], summary="Service-to-service API Key endpoint")
def external_service_metrics(key: str = Depends(verify_api_key)):
    """Requires 'X-API-Key: sk-fastapi-demo-secret-key-12345' header."""
    return {"message": "API Key verified successfully", "service_status": "All systems operational"}


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 8: Auth, OAuth2, JWT & RBAC Demo Starting!")
    print("👉 Open Swagger UI: http://127.0.0.1:8000/docs")
    print("👉 Click 'Authorize' in Swagger UI and login with:")
    print("   • Username: alice (admin) OR bob (user)")
    print("   • Password: secretpassword")
    print("=" * 60 + "\n")
    uvicorn.run("08_dependency_injection_auth:app", host="127.0.0.1", port=8000, reload=True)
