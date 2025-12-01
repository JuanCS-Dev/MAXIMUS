"""
Meta-Orchestrator FastAPI Application
======================================

REST API for mission execution and agent management.

Endpoints:
- POST /v1/missions - Execute a mission
- GET /v1/agents - List registered agents
- GET /v1/agents/{name}/health - Agent health check
- GET /health - Service health
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.orchestrator import Orchestrator  # pylint: disable=relative-beyond-top-level
from ..core.agent_registry import AgentRegistry  # pylint: disable=relative-beyond-top-level
from ..core.task_decomposer import TaskDecomposer  # pylint: disable=relative-beyond-top-level
from ..plugins.base import Task, TaskPriority  # pylint: disable=relative-beyond-top-level


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models
class MissionRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Request to execute a mission"""
    type: str = Field(..., description="Task type (e.g., 'infrastructure', 'intelligence')")
    description: str = Field(..., description="Mission description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Mission context")
    priority: str = Field(default="medium", description="Priority: low, medium, high, critical")

    class Config:
        schema_extra = {
            "example": {
                "type": "infrastructure",
                "description": "Optimize system performance",
                "context": {"target": "production"},
                "priority": "high"
            }
        }


class MissionResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Response from mission execution"""
    mission_id: str
    status: str
    output: Dict[str, Any]
    reasoning: str
    confidence: float
    execution_time_ms: int
    errors: List[str]


class AgentInfo(BaseModel):
    """Agent information"""
    name: str
    version: str
    enabled: bool
    capabilities: List[str]
    description: str
    stats: Dict[str, Any]


# Initialize FastAPI app
app = FastAPI(
    title="Maximus 2.0 Meta-Orchestrator",
    description="Hierarchical multi-agent orchestration API",
    version="2.0.0"
)

# Global state (will be initialized on startup)
orchestrator: Optional[Orchestrator] = None
registry: Optional[AgentRegistry] = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize orchestrator on startup"""
    global orchestrator, registry  # pylint: disable=global-statement

    logger.info("Initializing Meta-Orchestrator...")

    # Create registry
    registry = AgentRegistry()

    # Create decomposer (without LLM for now)
    decomposer = TaskDecomposer()

    # Create orchestrator
    orchestrator = Orchestrator(
        registry=registry,
        decomposer=decomposer
    )

    logger.info("Meta-Orchestrator ready")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Service health check"""
    return {
        "status": "healthy",
        "service": "meta-orchestrator",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/v1/missions", response_model=MissionResponse)
async def execute_mission(request: MissionRequest) -> MissionResponse:
    """
    Execute a mission via meta-orchestrator.

    The orchestrator will:
    1. Decompose complex missions into subtasks
    2. Route tasks to specialist agents
    3. Execute with dependency resolution
    4. Synthesize results
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Parse priority
    priority_map = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
        "critical": TaskPriority.CRITICAL
    }
    priority = priority_map.get(request.priority.lower(), TaskPriority.MEDIUM)

    # Create mission task
    mission = Task(
        task_id=f"mission_{datetime.now().timestamp()}",
        type=request.type,
        description=request.description,
        context=request.context,
        priority=priority
    )

    # Execute mission
    try:
        result = await orchestrator.execute_mission(mission)

        return MissionResponse(
            mission_id=result.task_id,
            status=result.status.value,
            output=result.output,
            reasoning=result.reasoning,
            confidence=result.confidence,
            execution_time_ms=result.execution_time_ms,
            errors=result.errors
        )

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Mission execution failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/agents", response_model=List[AgentInfo])
async def list_agents(enabled_only: bool = False) -> List[Dict[str, Any]]:
    """List all registered agents"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    agents = await registry.list_agents(enabled_only=enabled_only)
    return agents


@app.get("/v1/agents/{agent_name}/health")
async def agent_health(agent_name: str) -> Dict[str, Any]:
    """Check specific agent's health"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    agent = await registry.get_agent(agent_name)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

    try:
        health = await agent.health_check()
        return health
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "healthy": False,
            "error": str(e)
        }


@app.get("/v1/agents/health/all")
async def all_agents_health() -> Dict[str, Dict[str, Any]]:
    """Check health of all agents"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    health_results = await registry.health_check_all()
    return health_results


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(_: Any, exc: Exception) -> JSONResponse:
    """Global exception handler"""
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
    uvicorn.run(app, host="0.0.0.0", port=8100)
