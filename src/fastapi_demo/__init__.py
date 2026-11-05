import uvicorn
from fastapi import FastAPI

app = FastAPI(title="FastAPI Demo")

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


def main() -> None:
    uvicorn.run("fastapi_demo:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
