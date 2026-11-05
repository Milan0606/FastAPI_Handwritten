# FastAPI Demo

A demo FastAPI project managed with [uv](https://docs.astral.sh/uv/).

## How to Run

### Option 1: Using the configured project script (Recommended)
```bash
uv run fastapi-demo
```

### Option 2: Using Uvicorn directly
```bash
uv run uvicorn fastapi_demo:app --reload --port 8000
```

### Option 3: Running the Python script directly
```bash
uv run python src/fastapi_demo/__init__.py
```

## API Documentation
Once running, open your browser and navigate to:
- **API Root**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Docs**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
