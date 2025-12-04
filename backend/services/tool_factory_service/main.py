"""
Tool Factory Service: Entry Point
==================================

FastAPI service for dynamic tool generation and execution.
"""

from __future__ import annotations

import uvicorn
from api.routes import app
from config import get_config

if __name__ == "__main__":
    config = get_config()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.service_port,
        log_level=config.log_level.lower(),
    )
