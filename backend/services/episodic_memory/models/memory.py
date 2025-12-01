"""
Episodic Memory: Memory Models
==============================

Data models for the episodic memory service.
Defines the structure for storing and retrieving agent memories.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memories"""
    EXPERIENCE = "experience"  # Record of an event or task execution
    FACT = "fact"             # Static knowledge
    PROCEDURE = "procedure"   # How-to knowledge
    REFLECTION = "reflection" # Insight from metacognition


class Memory(BaseModel):
    """
    A single unit of memory.

    Attributes:
        memory_id: Unique identifier
        type: Type of memory
        content: The actual memory content (text or structured)
        context: Metadata about the memory (tags, source, etc.)
        embedding: Vector embedding (optional, for future use)
        importance: Importance score (0.0-1.0)
        timestamp: When the memory was created
    """
    memory_id: str
    type: MemoryType
    content: str
    context: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    importance: float = 0.5
    timestamp: datetime = Field(default_factory=datetime.now)


class MemoryQuery(BaseModel):
    """
    Query to search for memories.

    Attributes:
        query_text: Natural language query
        type: Filter by memory type
        limit: Max number of results
        min_importance: Filter by importance
    """
    query_text: str
    type: Optional[MemoryType] = None
    limit: int = 5
    min_importance: float = 0.0


class MemorySearchResult(BaseModel):
    """
    Result of a memory search.

    Attributes:
        memories: List of matching memories
        total_found: Total number of matches
    """
    memories: List[Memory]
    total_found: int
