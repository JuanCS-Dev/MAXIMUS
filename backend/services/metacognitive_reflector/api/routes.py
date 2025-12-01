"""
Metacognitive Reflector - API Routes
====================================

FastAPI endpoints for reflection and critique.
"""

from fastapi import APIRouter, Depends, HTTPException

from ..core.memory_client import MemoryClient
from ..core.reflector import Reflector
from ..models.reflection import ExecutionLog, ReflectionResponse
from .dependencies import get_memory_client, get_reflector

router = APIRouter()


@router.get("/health", response_model=dict)
async def health_check() -> dict[str, str]:
    """
    Service health check.
    """
    return {"status": "healthy", "service": "metacognitive-reflector"}


@router.post("/reflect", response_model=ReflectionResponse)
async def reflect_on_execution(
    log: ExecutionLog,
    reflector: Reflector = Depends(get_reflector),
    memory_client: MemoryClient = Depends(get_memory_client)
) -> ReflectionResponse:
    """
    Analyze an execution log and provide a critique.
    
    This endpoint:
    1. Analyzes the log using the Triad of Rationalization.
    2. Determines offense level and punishment.
    3. Generates memory updates.
    4. Applies updates to shared memory.
    """
    # 1. Analyze
    critique = await reflector.analyze_log(log)
    
    # 2. Generate Updates
    memory_updates = await reflector.generate_memory_updates(critique)
    
    # 3. Apply Punishment (if any)
    punishment = await reflector.apply_punishment(critique.offense_level)
    
    # 4. Apply Memory Updates
    if memory_updates:
        await memory_client.apply_updates(memory_updates)
        
    return ReflectionResponse(
        critique=critique,
        memory_updates=memory_updates,
        punishment_action=punishment
    )
