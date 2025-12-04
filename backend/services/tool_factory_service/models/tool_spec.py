"""
Tool Specification Models
==========================

Data models for tool generation and execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolGenerateRequest(BaseModel):
    """Request to generate a new tool.

    Attributes:
        name: Tool name (snake_case)
        description: What the tool does
        parameters: Parameter specifications {name: {type, description, required}}
        return_type: Return type description
        examples: List of example usages with expected outputs
    """

    name: str = Field(..., pattern=r"^[a-z_][a-z0-9_]*$")
    description: str = Field(..., min_length=10)
    parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    return_type: str = Field(default="Any")
    examples: List[Dict[str, Any]] = Field(default_factory=list)


@dataclass
class ToolSpec:
    """Specification for a generated tool.

    Attributes:
        name: Tool name
        description: Tool description
        parameters: Parameter specifications
        return_type: Return type
        code: Generated Python code
        examples: Example usages
        success_rate: Test success rate (0.0-1.0)
        usage_count: Number of times tool has been used
        version: Tool version number
        created_at: Creation timestamp
        last_used: Last usage timestamp
    """

    name: str
    description: str
    parameters: Dict[str, Dict[str, Any]]
    return_type: str
    code: str
    examples: List[Dict[str, Any]]
    success_rate: float = 0.0
    usage_count: int = 0
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None

    def get_signature(self) -> str:
        """Get function signature with type hints.

        Returns:
            Function signature string
        """
        params = []
        for name, spec in self.parameters.items():
            param_type = spec.get("type", "Any")
            default = spec.get("default")

            if default is not None:
                params.append(f"{name}: {param_type} = {default!r}")
            else:
                params.append(f"{name}: {param_type}")

        params_str = ", ".join(params)
        return f"def {self.name}({params_str}) -> {self.return_type}:"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "code": self.code,
            "examples": self.examples,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }


class ExecutionResult(BaseModel):
    """Result of tool execution.

    Attributes:
        success: Whether execution succeeded
        output: Tool output (if success)
        error: Error message (if failure)
        execution_time_ms: Execution time in milliseconds
    """

    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float
