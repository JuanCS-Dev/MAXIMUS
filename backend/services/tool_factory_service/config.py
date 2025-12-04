"""
Tool Factory Service Configuration
===================================

Pydantic-based configuration following CODE_CONSTITUTION standards.
"""

from __future__ import annotations

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class ToolFactoryConfig(BaseSettings):
    """Configuration for Tool Factory Service.

    Attributes:
        service_name: Service identifier
        service_port: Port to run the service on
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        gemini_api_key: API key for Gemini LLM
        gemini_model: Model to use for code generation
        max_output_tokens: Maximum tokens for LLM generation
        sandbox_timeout: Timeout for sandbox execution (seconds)
        sandbox_max_memory_mb: Maximum memory for sandbox (MB)
        max_tool_size_lines: Maximum lines per generated tool
        allowed_imports: Python imports allowed in generated tools
        blocked_imports: Python imports blocked in generated tools
        success_rate_threshold: Minimum success rate for tool registration
        max_generation_attempts: Maximum attempts to generate/fix a tool
    """

    # Service configuration
    service_name: str = Field(default="tool-factory-service")
    service_port: int = Field(default=8105)
    log_level: str = Field(default="INFO")

    # LLM configuration
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-3-pro-preview")
    max_output_tokens: int = Field(default=8192)

    # Sandbox configuration
    sandbox_timeout: float = Field(default=30.0)
    sandbox_max_memory_mb: int = Field(default=512)
    max_output_size: int = Field(default=100000)
    max_tool_size_lines: int = Field(default=100)

    # Safety configuration
    allowed_imports: List[str] = Field(default_factory=lambda: [
        "json", "re", "math", "random", "datetime", "collections",
        "itertools", "functools", "pathlib", "hashlib", "base64",
        "urllib.parse", "uuid", "typing", "dataclasses"
    ])

    blocked_imports: List[str] = Field(default_factory=lambda: [
        "subprocess", "shutil", "socket", "http", "ctypes", "os",
        "sys", "eval", "exec", "compile", "__import__"
    ])

    # Quality configuration
    success_rate_threshold: float = Field(default=0.8)
    max_generation_attempts: int = Field(default=3)

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_config() -> ToolFactoryConfig:
    """Get singleton configuration instance.

    Returns:
        ToolFactoryConfig instance
    """
    return ToolFactoryConfig()
