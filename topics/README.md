# Complete FastAPI Learning Roadmap (Based on Handwritten Notes PDF)

This repository contains runnable, standalone demos covering all **30 pages** of [FastAPI handwritten notes .pdf](file:///Users/bytes-milan/Documents/FastAPI_Demo/FastAPI%20handwritten%20notes%20.pdf).

---

## 📚 Complete Topic & Demo Index

| Topic # | Module / Subject | Demo File | PDF Pages | Key Concepts Covered |
|:---|:---|:---|:---|:---|
| **01** | **What & Why FastAPI** | [`01_what_is_fastapi.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/01_what_is_fastapi.py) | pp. 2–3 | Sebastián Ramírez, Starlette + Pydantic, auto Swagger UI (`/docs`), ReDoc (`/redoc`) |
| **02** | **Application Structure** | [`02_app_structure.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/02_app_structure.py) | p. 2 | `FastAPI()` instance, metadata, entry point, lifespan startup/shutdown hooks |
| **03** | **Routes & HTTP Methods** | [`03_routes_and_http_methods.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/03_routes_and_http_methods.py) | pp. 2–3 | `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`, CRUD operations |
| **04** | **Endpoints & Inputs** | [`04_endpoints_and_inputs.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/04_endpoints_and_inputs.py) | p. 3 | Path parameters, Query parameters, and Request Body parsing |
| **05** | **AI & RAG Endpoints** | [`05_ai_and_rag_endpoints.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/05_ai_and_rag_endpoints.py) | pp. 17–19 | Chat completions, RAG vector retrieval, document upload |
| **06** | **APIRouter & Modules** | [`06_apirouter_modular_apps.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/06_apirouter_modular_apps.py) | p. 4 | `APIRouter`, modular file structure, prefixes, tags, `include_router` |
| **07** | **Pydantic Validation & Schemas** | [`07_pydantic_validation_schemas.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/07_pydantic_validation_schemas.py) | pp. 5–7 | Request/Response models (`response_model`), hiding passwords, `Field(...)` validation, nested models |
| **08** | **Dependency Injection & Auth** | [`08_dependency_injection_auth.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/08_dependency_injection_auth.py) | pp. 8–10 | `Depends()`, OAuth2 with JWT tokens, RBAC roles, `APIKeyHeader` |
| **09** | **Async & SSE Streaming** | [`09_async_streaming_sse.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/09_async_streaming_sse.py) | pp. 11–13 | `async/await`, `asyncio.gather`, `StreamingResponse`, Server-Sent Events (SSE), LLM token streaming |
| **10** | **Database & SQLAlchemy CRUD** | [`10_database_sqlalchemy_crud.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/10_database_sqlalchemy_crud.py) | pp. 14–16 | SQLAlchemy ORM, `SessionLocal`, `get_db` dependency, CRUD, transactions & rollbacks |
| **11** | **Error Handling & Resilience** | [`11_error_handling_exceptions.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/11_error_handling_exceptions.py) | pp. 20–21 | `HTTPException`, custom exceptions, custom `@app.exception_handler`, clean 422 errors, retry with backoff |
| **12** | **Middleware & Observability** | [`12_middleware_and_observability.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/12_middleware_and_observability.py) | pp. 23–26 | `@app.middleware("http")`, `X-Request-ID`, `X-Process-Time`, `/health` & `/health/ready` |
| **13** | **Testing with TestClient** | [`13_testing_testclient.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/13_testing_testclient.py) | pp. 21–22 | `pytest`, `TestClient` in-memory testing, status assertions, `dependency_overrides` mocking |
| **14** | **Production Research AI Agent** | [`14_production_research_agent.py`](file:///Users/bytes-milan/Documents/FastAPI_Demo/topics/14_production_research_agent.py) | pp. 27–29 | Complete Capstone: Asynchronous agent with `BackgroundTasks`, UUID job ID generation, status polling |

---

## 🚀 How to Run Any Topic

Run directly in terminal using `uv`:

```bash
# Example: Run Topic 8 (OAuth2 & JWT Auth)
uv run python topics/08_dependency_injection_auth.py

# Example: Run Topic 10 (SQLAlchemy Database CRUD)
uv run python topics/10_database_sqlalchemy_crud.py

# Example: Run Topic 13 (Automated Tests)
uv run python topics/13_testing_testclient.py
# or with pytest:
uv run pytest -v topics/13_testing_testclient.py

# Example: Run Topic 14 (Production Research AI Agent)
uv run python topics/14_production_research_agent.py
```

After starting any server, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to interact with the endpoints.
