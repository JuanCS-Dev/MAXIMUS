"""
MAXIMUS MCP Server
==================

FastAPI + FastMCP dual protocol server following elite patterns.

Follows CODE_CONSTITUTION: All pillars.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config import get_config
from middleware.structured_logger import LoggingMiddleware, StructuredLogger

# Initialize config and logger
config = get_config()
logger = StructuredLogger(config.service_name, config.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initializes resources on startup, cleans up on shutdown.
    """
    logger.info("Starting MAXIMUS MCP Server", version="2.0.0")

    # Startup: Initialize clients, connections, etc.
    # (Clients are initialized per-request to avoid shared state)

    yield

    # Shutdown: Cleanup resources
    logger.info("Shutting down MAXIMUS MCP Server")


# Create FastAPI application
app = FastAPI(
    title="MAXIMUS MCP Server",
    description="Model Context Protocol server for MAXIMUS 2.0",
    version="2.0.0",
    lifespan=lifespan,
)

# Add logging middleware
app.add_middleware(LoggingMiddleware, logger=logger)


# REST API Endpoints (Traditional)
@app.get("/health")
async def health():
    """Health check for load balancers.

    Returns:
        Health status dict
    """
    return {"status": "ok", "version": "2.0.0", "service": config.service_name}


@app.get("/metrics")
async def metrics():
    """Get service metrics.

    Returns:
        Metrics dict with circuit breaker and rate limiter stats
    """
    from middleware.circuit_breaker import get_breaker_stats

    return {
        "circuit_breakers": get_breaker_stats(),
        # Rate limiter stats would go here
    }


# MCP Tool Registration
# Note: FastMCP integration would happen here, but we're creating
# a production-ready structure first. MCP tools from tools/ directory
# would be imported and registered with FastMCP instance.

# Example of how FastMCP would be integrated:
# from fastmcp import FastMCP
# mcp = FastMCP("maximus")
#
# # Register tools
# from tools.tribunal_tools import tribunal_evaluate, tribunal_health, tribunal_stats
# from tools.factory_tools import factory_generate, factory_execute, factory_list, factory_delete
# from tools.memory_tools import memory_store, memory_search, memory_consolidate, memory_context
#
# mcp.add_tool(tribunal_evaluate)
# mcp.add_tool(tribunal_health)
# mcp.add_tool(tribunal_stats)
# mcp.add_tool(factory_generate)
# mcp.add_tool(factory_execute)
# mcp.add_tool(factory_list)
# mcp.add_tool(factory_delete)
# mcp.add_tool(memory_store)
# mcp.add_tool(memory_search)
# mcp.add_tool(memory_consolidate)
# mcp.add_tool(memory_context)
#
# # Mount MCP app (dual protocol)
# mcp_app = mcp.get_app()
# app.mount("/mcp", mcp_app)


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for uncaught errors.

    Args:
        request: HTTP request
        exc: Exception raised

    Returns:
        JSON error response
    """
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.service_port,
        log_level=config.log_level.lower(),
        reload=False,  # Disable in production
    )
