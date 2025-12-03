"""
Unit tests for Episodic Memory Store.
"""

from __future__ import annotations

import pytest

from core.memory_store import MemoryStore
from models.memory import MemoryType, MemoryQuery

@pytest.mark.asyncio
async def test_store_and_retrieve():
    store = MemoryStore()
    
    # Store memory
    memory = await store.store(
        content="Test memory content",
        memory_type=MemoryType.FACT,
        context={"source": "test"}
    )
    
    assert memory.memory_id is not None
    assert memory.content == "Test memory content"
    assert memory.type == MemoryType.FACT
    
    # Retrieve memory
    query = MemoryQuery(query_text="test memory")
    results = await store.retrieve(query)
    
    assert results.total_found == 1
    assert results.memories[0].memory_id == memory.memory_id

@pytest.mark.asyncio
async def test_retrieve_filters():
    store = MemoryStore()
    
    await store.store("Memory 1", MemoryType.FACT)
    await store.store("Memory 2", MemoryType.EXPERIENCE)
    
    # Filter by type
    query = MemoryQuery(query_text="memory", type=MemoryType.FACT)
    results = await store.retrieve(query)
    
    assert results.total_found == 1
    assert results.memories[0].content == "Memory 1"

@pytest.mark.asyncio
async def test_delete():
    store = MemoryStore()
    memory = await store.store("To delete", MemoryType.FACT)
    
    # Verify exists
    retrieved = await store.get_memory(memory.memory_id)
    assert retrieved is not None
    
    # Delete
    success = await store.delete(memory.memory_id)
    assert success is True
    
    # Verify deleted
    retrieved = await store.get_memory(memory.memory_id)
    assert retrieved is None
    
    # Delete non-existent
    success = await store.delete("fake_id")
    assert success is False
