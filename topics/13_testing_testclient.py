"""
Topic 13: API Testing with pytest, TestClient & Dependency Overrides
===================================================================
(Reference: Pages 21 and 22 of the Notes)

Key Concepts Explained:
-----------------------
1. What is TestClient?
   - Provided by FastAPI (powered by HTTPX).
   - Allows you to test all HTTP endpoints (GET, POST, PUT, DELETE) in memory WITHOUT needing
     to start a live server or manage port bindings!

2. Dependency Overrides:
   - In production, endpoints might connect to a paid LLM API, an external payment gateway, or a live database.
   - During automated tests, `app.dependency_overrides[dependency_function] = mock_function` allows you
     to replace real services with fast, free mocks.

3. Testing Edge Cases:
   - Verifying HTTP 200 OK responses.
   - Verifying HTTP 422 Unprocessable Entity on invalid inputs.
   - Verifying HTTP 404 Not Found.

How to Run This Demo:
---------------------
You can run this file directly with Python:
    uv run python topics/13_testing_testclient.py

OR run it with pytest:
    uv run pytest -v topics/13_testing_testclient.py
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

# ===================================================================
# 1. Mini FastAPI Application to Test
# ===================================================================
app = FastAPI(title="Testing Target App")


# External service dependency (e.g., LLM or Database)
def get_llm_response(prompt: str) -> str:
    # In real life, this calls OpenAI or Anthropic (expensive & slow)
    return "Real live expensive LLM response"


class Feedback(BaseModel):
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str


db_feedback: list[dict] = []


@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id == 999:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "name": f"Item {item_id}"}


@app.post("/feedback", status_code=201)
def submit_feedback(fb: Feedback):
    db_feedback.append(fb.model_dump())
    return {"status": "saved", "feedback": fb.model_dump()}


@app.get("/ask-ai")
def ask_ai(question: str, llm_engine=Depends(get_llm_response)):
    answer = llm_engine(question) if callable(llm_engine) else llm_engine
    return {"question": question, "answer": answer}


# ===================================================================
# 2. Test Suite Using TestClient
# ===================================================================
client = TestClient(app)


def test_read_item_success():
    """Test standard GET request with status 200."""
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "name": "Item 42"}
    print("  ✅ test_read_item_success passed!")


def test_read_item_not_found():
    """Test 404 error response handling."""
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
    print("  ✅ test_read_item_not_found passed!")


def test_submit_feedback_success():
    """Test POST request with valid payload and status 201."""
    payload = {"user_id": 1, "rating": 5, "comment": "FastAPI is fantastic!"}
    response = client.post("/feedback", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "saved"
    print("  ✅ test_submit_feedback_success passed!")


def test_submit_feedback_invalid():
    """Test automatic 422 error on invalid data (rating > 5)."""
    invalid_payload = {"user_id": 1, "rating": 10, "comment": "Too high!"}
    response = client.post("/feedback", json=invalid_payload)
    assert response.status_code == 422
    print("  ✅ test_submit_feedback_invalid (422) passed!")


def test_ask_ai_with_dependency_override():
    """Test mocking expensive external dependencies using app.dependency_overrides."""

    # Define mock replacement
    def mock_free_llm(prompt: str) -> str:
        return "MOCKED free test response without calling external API"

    # Override dependency
    app.dependency_overrides[get_llm_response] = lambda: mock_free_llm

    response = client.get("/ask-ai?question=Hello")
    assert response.status_code == 200
    assert response.json()["answer"] == "MOCKED free test response without calling external API"

    # Always clear overrides after testing
    app.dependency_overrides.clear()
    print("  ✅ test_ask_ai_with_dependency_override passed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 Running Topic 13 Automated API Tests...")
    print("=" * 60)
    test_read_item_success()
    test_read_item_not_found()
    test_submit_feedback_success()
    test_submit_feedback_invalid()
    test_ask_ai_with_dependency_override()
    print("=" * 60)
    print("🎉 All 5 API tests completed successfully!\n")
