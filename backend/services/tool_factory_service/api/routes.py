"""
Tool Factory Service API Routes
================================

FastAPI endpoints for dynamic tool generation.

Endpoints:
- POST /v1/tools/generate - Generate new tool
- GET /v1/tools - List all tools
- GET /v1/tools/{name} - Get tool specification
- DELETE /v1/tools/{name} - Remove tool
- POST /v1/tools/export - Export all tools
- POST /v1/tools/import - Import tools
- GET /v1/stats - Get statistics
- GET /health - Health check

Follows CODE_CONSTITUTION: Safety First, Clarity Over Cleverness
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import get_config
from core import ToolFactory, ToolGenerationError
from models.tool_spec import ToolGenerateRequest, ToolSpec

# Initialize FastAPI app
app = FastAPI(
    title="Tool Factory Service",
    description="Dynamic tool generation service for MAXIMUS 2.0",
    version="1.0.0",
)

# Initialize factory (singleton pattern)
_factory: ToolFactory | None = None


def get_factory() -> ToolFactory:
    """Get or create tool factory instance.

    Returns:
        Initialized ToolFactory
    """
    global _factory
    if _factory is None:
        config = get_config()
        _factory = ToolFactory(config)
    return _factory


# Response Models


class ToolGenerateResponse(BaseModel):
    """Response for tool generation."""

    name: str = Field(..., description="Generated tool name")
    description: str = Field(..., description="Tool description")
    success_rate: float = Field(..., description="Test success rate")
    version: int = Field(..., description="Tool version")


class ToolListItem(BaseModel):
    """Tool list item."""

    name: str
    description: str
    success_rate: float
    usage_count: int
    version: int
    parameters: List[str]


class StatsResponse(BaseModel):
    """Statistics response."""

    generated_tools: int
    total_generations: int
    successful_generations: int
    total_tool_uses: int
    average_success_rate: float


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


# Routes


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Service health status
    """
    return HealthResponse(
        status="healthy",
        service="tool-factory-service",
        version="1.0.0",
    )


@app.post(
    "/v1/tools/generate",
    response_model=ToolGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tools"],
)
async def generate_tool(request: ToolGenerateRequest) -> ToolGenerateResponse:
    """Generate a new tool from description and examples.

    Args:
        request: Tool generation request

    Returns:
        Generated tool information

    Raises:
        HTTPException: If generation fails
    """
    factory = get_factory()

    try:
        spec = await factory.generate_tool(request, max_attempts=3)

        return ToolGenerateResponse(
            name=spec.name,
            description=spec.description,
            success_rate=spec.success_rate,
            version=spec.version,
        )

    except ToolGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool generation failed: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}",
        )


@app.get("/v1/tools", response_model=List[ToolListItem], tags=["Tools"])
async def list_tools() -> List[ToolListItem]:
    """List all generated tools.

    Returns:
        List of tool summaries
    """
    factory = get_factory()
    tools = factory.list_tools()

    return [
        ToolListItem(
            name=tool["name"],
            description=tool["description"],
            success_rate=tool["success_rate"],
            usage_count=tool["usage_count"],
            version=tool["version"],
            parameters=tool["parameters"],
        )
        for tool in tools
    ]


@app.get("/v1/tools/{name}", response_model=ToolSpec, tags=["Tools"])
async def get_tool(name: str) -> ToolSpec:
    """Get tool specification by name.

    Args:
        name: Tool name

    Returns:
        Complete tool specification

    Raises:
        HTTPException: If tool not found
    """
    factory = get_factory()
    spec = factory.get_tool_spec(name)

    if spec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{name}' not found",
        )

    return spec


@app.delete("/v1/tools/{name}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tools"])
async def delete_tool(name: str) -> None:
    """Remove a tool from registry.

    Args:
        name: Tool name

    Raises:
        HTTPException: If tool not found
    """
    factory = get_factory()
    removed = factory.remove_tool(name)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{name}' not found",
        )


@app.get("/v1/tools/export", response_model=Dict[str, Any], tags=["Tools"])
async def export_tools() -> Dict[str, Any]:
    """Export all generated tools.

    Returns:
        Dictionary of all tools with full specifications
    """
    factory = get_factory()
    return factory.export_tools()


@app.post("/v1/tools/import", status_code=status.HTTP_200_OK, tags=["Tools"])
async def import_tools(data: Dict[str, Any]) -> JSONResponse:
    """Import previously exported tools.

    Args:
        data: Exported tools dictionary

    Returns:
        Import status
    """
    factory = get_factory()

    try:
        factory.import_tools(data)
        return JSONResponse(
            content={
                "status": "success",
                "imported_count": len(data),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Import failed: {str(e)}",
        )


@app.get("/v1/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats() -> StatsResponse:
    """Get tool factory statistics.

    Returns:
        Statistics about tool generation and usage
    """
    factory = get_factory()
    stats = factory.get_stats()

    return StatsResponse(
        generated_tools=stats["generated_tools"],
        total_generations=stats["total_generations"],
        successful_generations=stats["successful_generations"],
        total_tool_uses=stats["total_tool_uses"],
        average_success_rate=stats["average_success_rate"],
    )


# Error handlers


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions.

    Args:
        request: Request object
        exc: ValueError exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle general exceptions.

    Args:
        request: Request object
        exc: Exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
