"""
Topic 14: Production Research AI Agent API (Capstone Project)
=============================================================
(Reference: Pages 27, 28, and 29 of the Notes)

Key Concepts Explained:
-----------------------
This is the complete end-to-end production architecture taught in the PDF:
1. Long-Running AI Tasks:
   - Deep research, web scraping, and multi-step reasoning take time (10s to minutes).
   - NEVER keep the HTTP request hanging while the agent thinks; the client will time out!

2. The Production Background Pattern:
   Step 1: Client submits research query (`POST /research`).
   Step 2: Server creates a unique `job_id = uuid.uuid4()`, marks status="running",
           and spawns the agent in `BackgroundTasks`.
   Step 3: Server returns `202 Accepted` immediately with the `job_id`.
   Step 4: Client polls `GET /research/{job_id}` to check progress until status="completed".

3. Clean Layered Architecture:
   - Route Layer: FastAPI endpoint definitions.
   - Schema Layer: Pydantic models for request & structured report.
   - Service Layer: Business orchestration & job storage.
   - Agent Layer: Multi-step reasoning (Plan, Search, Synthesize).

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/14_production_research_agent.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import asyncio
from datetime import datetime, timezone
import uuid
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Topic 14: Production Research AI Agent API",
    description="Full asynchronous Research Agent architecture with BackgroundTasks & Job ID status polling.",
    version="1.0.0",
)


# ===================================================================
# 1. Schemas (Data Layer)
# ===================================================================
class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, example="Latest Advancements in Agentic AI")
    depth: str = Field(default="medium", example="medium", description="'quick', 'medium', or 'deep'")


class SourceCitation(BaseModel):
    title: str
    url: str


class ResearchResult(BaseModel):
    topic: str
    summary: str
    sources: list[SourceCitation]
    completed_at: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # "queued", "running", "completed", "failed"
    topic: str
    created_at: str
    result: ResearchResult | None = None


# In-memory Job Database (In production, use Redis or PostgreSQL)
jobs_db: dict[str, dict] = {}


# ===================================================================
# 2. Agent Layer (Simulating Autonomous Research Agent)
# ===================================================================
class ResearchAgent:
    """Autonomous agent that performs web search, analysis, and report generation."""

    async def execute_research(self, topic: str, depth: str) -> ResearchResult:
        print(f"🤖 [Agent]: Starting research on '{topic}' (depth: {depth})...")

        # Step 1: Query analysis & plan
        await asyncio.sleep(1.0)
        print(f"🤖 [Agent]: Step 1/3 - Searching academic papers and technical blogs...")

        # Step 2: Information extraction
        await asyncio.sleep(1.5)
        print(f"🤖 [Agent]: Step 2/3 - Synthesizing key findings and cross-checking facts...")

        # Step 3: Final report synthesis
        await asyncio.sleep(1.0)
        print(f"🤖 [Agent]: Step 3/3 - Generating final research summary.")

        return ResearchResult(
            topic=topic,
            summary=(
                f"Comprehensive analysis on '{topic}': Modern systems leverage modular FastAPI "
                f"backends combined with asynchronous background workers, structured Pydantic schemas, "
                f"and vector retrieval (RAG) to build production-grade agentic workflows."
            ),
            sources=[
                SourceCitation(title="FastAPI Official Architecture", url="https://fastapi.tiangolo.com"),
                SourceCitation(title="Autonomous AI Agents Survey", url="https://arxiv.org/abs/2308.11432"),
            ],
            completed_at=datetime.now(timezone.utc).isoformat(),
        )


# ===================================================================
# 3. Service Layer (Background Task Orchestration)
# ===================================================================
agent_instance = ResearchAgent()


async def background_agent_worker(job_id: str, topic: str, depth: str):
    """Executes the agent workflow in the background and updates the job record."""
    jobs_db[job_id]["status"] = "running"
    try:
        report = await agent_instance.execute_research(topic, depth)
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["result"] = report.model_dump()
        print(f"✅ [Agent]: Job {job_id} successfully completed!")
    except Exception as exc:
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(exc)
        print(f"❌ [Agent]: Job {job_id} failed: {exc}")


# ===================================================================
# 4. API Endpoints
# ===================================================================
@app.post(
    "/research",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Research Agent"],
    summary="Submit a research task (Non-blocking)",
)
def start_research_task(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    1. Generates a unique Job ID.
    2. Registers the job in the database.
    3. Offloads the heavy research task to `BackgroundTasks`.
    4. Immediately returns HTTP 202 Accepted with the job_id.
    """
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    job_entry = {
        "job_id": job_id,
        "status": "queued",
        "topic": request.topic,
        "created_at": now,
        "result": None,
    }
    jobs_db[job_id] = job_entry

    # Launch background worker
    background_tasks.add_task(background_agent_worker, job_id, request.topic, request.depth)

    return job_entry


@app.get(
    "/research/{job_id}",
    response_model=JobStatusResponse,
    tags=["Research Agent"],
    summary="Poll research task status and retrieve final report",
)
def get_research_status(job_id: str):
    """Allows client to check whether research is still running or finished."""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail=f"Job ID '{job_id}' not found")
    return jobs_db[job_id]


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 14: Production Research AI Agent Server Starting!")
    print("👉 Open Swagger UI: http://127.0.0.1:8000/docs")
    print("👉 Workflow:")
    print("   1. Call POST /research to start a job (returns job_id immediately)")
    print("   2. Call GET /research/{job_id} to poll status until 'completed'")
    print("=" * 60 + "\n")
    uvicorn.run("14_production_research_agent:app", host="127.0.0.1", port=8000, reload=True)
