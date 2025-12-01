"""
Metacognitive Reflector - Main Application
==========================================

Entry point for the Metacognitive Reflector service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .api.dependencies import initialize_service
from .api.routes import router as api_router
from .config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifespan.
    """
    # Startup
    initialize_service()

    yield

    # Shutdown
    pass


app = FastAPI(
    title=settings.service.name,
    description="Metacognitive Reflector - The Conscience of Maximus 2.0",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint.
    """
    return {
        "message": "Metacognitive Reflector Operational",
        "service": settings.service.name,
        "motto": "Verdade, Sabedoria, Justiça"
    }
