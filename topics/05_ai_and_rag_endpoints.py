"""
Topic 5: FastAPI in AI, RAG, and Agentic Applications
=====================================================

Key Concepts Explained:
-----------------------
The slide highlighted:
"Widely used in AI/ML, RAG and Agentic AI projects to expose LLM/Agent
functionalities through APIs... endpoints are used for chat, document upload,
search, etc."

Why FastAPI is the #1 Choice for AI:
1. Async/Await: High concurrency when waiting for external LLM API responses (OpenAI, Anthropic, Gemini, Ollama).
2. Pydantic Models: Strongly typed prompt templates, structured outputs (JSON mode), and tool call schemas.
3. Automatic Swagger UI: Frontend developers and AI researchers can test prompt parameters immediately without writing UI code.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/05_ai_and_rag_endpoints.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import time
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Topic 5: AI, RAG & Agentic AI Endpoints",
    description="Real-world patterns showing how FastAPI powers LLMs, RAG, and AI Agents.",
    version="1.0.0",
)


# -------------------------------------------------------------------
# Schemas for AI & RAG
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., example="What is Retrieval-Augmented Generation?")
    model: str = Field(default="gemini-2.5-flash", example="gemini-2.5-flash")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    reply: str
    tokens_used: int
    model: str


class DocumentIngest(BaseModel):
    doc_id: str = Field(..., example="doc_101")
    title: str = Field(..., example="FastAPI Architecture Guide")
    content: str = Field(..., example="FastAPI uses Starlette and Pydantic for high performance.")


class RAGSearchRequest(BaseModel):
    query: str = Field(..., example="How does FastAPI validate data?")
    top_k: int = Field(default=2, ge=1, le=5)


# In-memory vector database mock
knowledge_base: list[dict] = [
    {
        "doc_id": "doc_001",
        "title": "FastAPI Validation",
        "content": "FastAPI uses Pydantic models for request validation and type safety.",
    },
    {
        "doc_id": "doc_002",
        "title": "FastAPI Performance",
        "content": "Built on Starlette and Uvicorn, FastAPI is one of the fastest Python frameworks.",
    },
]


# -------------------------------------------------------------------
# 1. Chat / LLM Endpoint
# -------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse, tags=["LLM Chat"])
async def chat_with_ai(request: ChatRequest):
    """
    Simulates calling an LLM (e.g. Gemini, OpenAI, Claude).
    Notice `async def` which prevents blocking the server during AI generation!
    """
    # In real applications, you would call: await client.chat.completions.create(...)
    user_prompt = request.message
    bot_reply = (
        f"[AI Assistant ({request.model})]: I received your prompt: '{user_prompt}'. "
        f"FastAPI makes it seamless to stream or serve AI responses!"
    )

    return ChatResponse(
        reply=bot_reply,
        tokens_used=len(user_prompt.split()) + 25,
        model=request.model,
    )


# -------------------------------------------------------------------
# 2. Document Ingestion for RAG
# -------------------------------------------------------------------
@app.post("/api/rag/documents", tags=["RAG Pipeline"])
def ingest_document(document: DocumentIngest):
    """
    Ingests text documents into the knowledge base (e.g., chunking & embedding storage).
    """
    knowledge_base.append(document.model_dump())
    return {
        "status": "success",
        "message": f"Document '{document.title}' indexed into knowledge base.",
        "total_documents": len(knowledge_base),
    }


# -------------------------------------------------------------------
# 3. Vector Similarity / RAG Search Endpoint
# -------------------------------------------------------------------
@app.post("/api/rag/search", tags=["RAG Pipeline"])
def search_knowledge_base(request: RAGSearchRequest):
    """
    Performs retrieval over stored documents relevant to the query.
    """
    query_words = set(request.query.lower().split())
    ranked_results = []

    for doc in knowledge_base:
        doc_words = set((doc["title"] + " " + doc["content"]).lower().split())
        match_score = len(query_words.intersection(doc_words))
        if match_score > 0:
            ranked_results.append({**doc, "score": match_score})

    ranked_results.sort(key=lambda x: x["score"], reverse=True)
    matches = ranked_results[: request.top_k]

    return {
        "query": request.query,
        "results_found": len(matches),
        "documents": matches,
    }


# -------------------------------------------------------------------
# 4. Agentic AI Task Status Endpoint
# -------------------------------------------------------------------
@app.get("/api/agent/task/{task_id}", tags=["Agentic AI"])
def get_agent_task_status(task_id: str):
    """
    Endpoints used by AI Agent frontends to poll or check long-running agent workflows.
    """
    return {
        "task_id": task_id,
        "status": "COMPLETED",
        "steps_executed": [
            "1. Analyzed user request",
            "2. Queried vector database",
            "3. Synthesized answer using LLM",
        ],
        "result": "Task finished successfully.",
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 5 Demo Server Starting!")
    print("👉 Test AI Chat, RAG Search & Document Ingestion in Swagger UI:")
    print("   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("05_ai_and_rag_endpoints:app", host="127.0.0.1", port=8000, reload=True)
