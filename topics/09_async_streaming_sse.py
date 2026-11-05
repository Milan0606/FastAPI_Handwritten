"""
Topic 9: Async, Streaming & Server-Sent Events (SSE)
====================================================
(Reference: Pages 11, 12, and 13 of the Notes)

Key Concepts Explained:
-----------------------
1. Async vs Sync:
   - Synchronous (`def`): Code runs one task at a time. Blocking tasks freeze worker threads.
   - Asynchronous (`async def`): Non-blocking coroutines. When waiting for I/O (database, external LLM API),
     the event loop switches to handle other user requests!

2. Concurrent Calls with `asyncio.gather()`:
   - Run multiple async tasks in parallel instead of one-after-another.
   - Example: Fetching user info + order history simultaneously saves 50% or more latency.

3. StreamingResponse:
   - Instead of waiting for a 1,000-word LLM reply or a 1GB file to complete, stream chunks
     immediately to the client as they become available.

4. Server-Sent Events (SSE):
   - Standard HTTP protocol using `media_type="text/event-stream"`.
   - Each message follows the format: `data: <content>\n\n`.
   - Essential for AI Chatbots, ChatGPT-like typing effects, and live Agent execution logs!

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/09_async_streaming_sse.py

Then visit:
    http://127.0.0.1:8000/docs
"""

import asyncio
import time
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(
    title="Topic 9: Async & Streaming (SSE, LLM Tokens & Agent Steps)",
    description="Learn non-blocking async execution, StreamingResponse, and Server-Sent Events (SSE).",
    version="1.0.0",
)


# ===================================================================
# 1. Sync vs. Async Comparison
# ===================================================================
@app.get("/demo/sync-delay", tags=["Sync vs Async"])
def sync_delay():
    """BLOCKING: Uses time.sleep(1). Blocks the worker thread from serving other requests!"""
    time.sleep(1.0)
    return {"mode": "sync", "slept": "1 second", "note": "Thread was blocked"}


@app.get("/demo/async-delay", tags=["Sync vs Async"])
async def async_delay():
    """NON-BLOCKING: Uses await asyncio.sleep(1). Frees the event loop to serve others!"""
    await asyncio.sleep(1.0)
    return {"mode": "async", "slept": "1 second", "note": "Event loop remained free"}


# ===================================================================
# 2. Parallel API Execution with asyncio.gather()
# ===================================================================
async def fetch_user_profile():
    await asyncio.sleep(0.3)  # Simulating external auth/user service
    return {"user_id": 42, "name": "Milan", "tier": "Pro"}


async def fetch_user_orders():
    await asyncio.sleep(0.3)  # Simulating orders database lookup
    return [{"order_id": 101, "total": 49.99}, {"order_id": 102, "total": 120.00}]


@app.get("/demo/parallel-fetch", tags=["Async Concurrency"])
async def parallel_fetch():
    """Runs user profile and order queries in parallel using asyncio.gather()."""
    start_time = time.perf_counter()
    user_data, orders_data = await asyncio.gather(
        fetch_user_profile(),
        fetch_user_orders(),
    )
    duration = round(time.perf_counter() - start_time, 3)

    return {
        "duration_seconds": duration,
        "note": "Both tasks took ~0.3s combined because they ran concurrently!",
        "user": user_data,
        "orders": orders_data,
    }


# ===================================================================
# 3. LLM Token Streaming (Real-time Word-by-Word Typing)
# ===================================================================
async def llm_token_generator(prompt: str):
    tokens = [
        "FastAPI ", "is ", "the ", "premier ", "Python ", "framework ",
        "for ", "serving ", "AI ", "Agents ", "and ", "LLMs. ",
        "Streaming ", "delivers ", "an ", "instant ", "user ", "experience!"
    ]
    for token in tokens:
        await asyncio.sleep(0.1)  # Simulate LLM generation latency
        yield f"data: {token}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/api/stream/llm", tags=["Streaming"])
async def stream_llm(prompt: str = "Explain FastAPI"):
    """Streams simulated LLM tokens one-by-one via Server-Sent Events (SSE)."""
    return StreamingResponse(
        llm_token_generator(prompt),
        media_type="text/event-stream",
    )


# ===================================================================
# 4. Agent Event Streaming (Thoughts, Tool Calls & Observations)
# ===================================================================
async def agent_event_generator():
    events = [
        "Thought: User asked for current weather in San Francisco.",
        "Tool Call: Executing weather_api(location='San Francisco')",
        "Observation: Weather service returned '68°F, Sunny'.",
        "Thought: Synthesizing final response for user.",
        "Final Answer: The current weather in San Francisco is 68°F and Sunny!",
    ]
    for event in events:
        await asyncio.sleep(0.5)
        yield f"event: agent_update\ndata: {event}\n\n"
    yield "event: agent_complete\ndata: [WORKFLOW_FINISHED]\n\n"


@app.get("/api/stream/agent", tags=["Streaming"])
async def stream_agent_steps():
    """Streams real-time multi-step agent reasoning steps as Server-Sent Events."""
    return StreamingResponse(
        agent_event_generator(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 9: Async & SSE Streaming Demo Starting!")
    print("👉 Test token streaming and SSE in browser:")
    print("   • LLM Stream:    http://127.0.0.1:8000/api/stream/llm?prompt=hi")
    print("   • Agent Stream:  http://127.0.0.1:8000/api/stream/agent")
    print("   • Swagger UI:    http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("09_async_streaming_sse:app", host="127.0.0.1", port=8000, reload=True)
