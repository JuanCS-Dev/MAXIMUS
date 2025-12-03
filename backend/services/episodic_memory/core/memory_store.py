"""
Episodic Memory: Memory Store
=============================

Core logic for storing and retrieving memories.
Currently implements an in-memory store, designed to be extensible
to Vector DBs (e.g., Chroma, Qdrant) in the future.
"""

from __future__ import annotations

import logging
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime

from models.memory import Memory, MemoryQuery, MemorySearchResult, MemoryType


logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Storage engine for episodic memories.

    Manages persistence and retrieval of memory objects.
    """

    def __init__(self) -> None:
        """Initialize the memory store."""
        # In-memory storage for now
        self._storage: Dict[str, Memory] = {}
        logger.info("MemoryStore initialized (in-memory)")

    async def store(
        self,
        content: str,
        memory_type: MemoryType,
        context: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """
        Store a new memory.

        Args:
            content: The memory content
            memory_type: Type of memory
            context: Optional metadata

        Returns:
            The created Memory object
        """
        memory_id = str(uuid.uuid4())
        memory = Memory(
            memory_id=memory_id,
            type=memory_type,
            content=content,
            context=context or {},
            timestamp=datetime.now()
        )

        self._storage[memory_id] = memory
        logger.info("Stored memory: %s (type=%s)", memory_id, memory_type)
        return memory

    async def retrieve(self, query: MemoryQuery) -> MemorySearchResult:
        """
        Retrieve memories based on a query.

        Args:
            query: Search criteria

        Returns:
            Search results
        """
        results: List[Memory] = []

        # Simple keyword search for now
        query_terms = query.query_text.lower().split()

        for memory in self._storage.values():
            # Filter by type if specified
            if query.type and memory.type != query.type:
                continue

            # Filter by importance
            if memory.importance < query.min_importance:
                continue

            # Check content match
            content_lower = memory.content.lower()
            if any(term in content_lower for term in query_terms):
                results.append(memory)

        # Sort by timestamp (newest first) as a simple heuristic
        results.sort(key=lambda x: x.timestamp, reverse=True)

        # Apply limit
        limited_results = results[:query.limit]

        return MemorySearchResult(
            memories=limited_results,
            total_found=len(results)
        )

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Get a specific memory by ID.

        Args:
            memory_id: ID to look up

        Returns:
            Memory object or None
        """
        return self._storage.get(memory_id)

    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: ID to delete

        Returns:
            True if deleted, False if not found
        """
        if memory_id in self._storage:
            del self._storage[memory_id]
            logger.info("Deleted memory: %s", memory_id)
            return True
        return False
