"""
Episodic Memory: API Routes
===========================

FastAPI application for the Episodic Memory service.
Exposes endpoints for storing, retrieving, and managing memories.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.memory_store import MemoryStore
from models.memory import Memory, MemoryQuery, MemorySearchResult, MemoryType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="Episodic Memory Service",
    description="Service for long-term agent memory storage and retrieval",
    version="1.0.0"
)


# Global state
store: MemoryStore = MemoryStore()


class StoreMemoryRequest(BaseModel):
    """Request to store a memory"""
    content: str
    type: MemoryType
    context: Optional[Dict[str, Any]] = None


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Service health check.

    Returns:
        Status dictionary.
    """
    return {
        "status": "healthy",
        "service": "episodic_memory",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/v1/memories", response_model=Memory)
async def store_memory(request: StoreMemoryRequest) -> Memory:
    """
    Store a new memory.

    Args:
        request: Memory details

    Returns:
        Created memory object
    """
    try:
        memory = await store.store(request.content, request.type, request.context)
        return memory
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to store memory: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/v1/memories/search", response_model=MemorySearchResult)
async def search_memories(query: MemoryQuery) -> MemorySearchResult:
    """
    Search for memories.

    Args:
        query: Search criteria

    Returns:
        Search results
    """
    try:
        results = await store.retrieve(query)
        return results
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Search failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/memories/{memory_id}", response_model=Memory)
async def get_memory(
    memory_id: str = Path(..., description="ID of the memory to retrieve")
) -> Memory:
    """
    Get a specific memory by ID.

    Args:
        memory_id: ID to look up

    Returns:
        Memory object
    """
    memory = await store.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@app.delete("/v1/memories/{memory_id}")
async def delete_memory(
    memory_id: str = Path(..., description="ID of the memory to delete")
) -> Dict[str, bool]:
    """
    Delete a memory.

    Args:
        memory_id: ID to delete

    Returns:
        Success status
    """
    success = await store.delete(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True}


@app.exception_handler(Exception)
async def global_exception_handler(_: Any, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8102)
