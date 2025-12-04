"""
Tests for Memory Client
========================

Scientific tests for Episodic Memory service client.

Follows CODE_CONSTITUTION: ≥85% coverage, clear test names.
"""

from __future__ import annotations

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from clients.memory_client import MemoryClient


class TestMemoryClientBasics:
    """Test basic memory client functionality."""

    def test_client_creation(self, config):
        """HYPOTHESIS: MemoryClient initializes with config."""
        client = MemoryClient(config)
        assert client.config == config
        assert client.client is not None

    def test_client_uses_memory_url(self, config):
        """HYPOTHESIS: Client uses memory_url from config."""
        config.memory_url = "http://custom-memory:9000"
        client = MemoryClient(config)
        assert client.client.base_url == "http://custom-memory:9000"


class TestMemoryClientStore:
    """Test memory storage."""

    @pytest.mark.asyncio
    async def test_store_memory_success(self, config):
        """HYPOTHESIS: store() saves memory."""
        client = MemoryClient(config)

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {
                "id": "mem_123",
                "content": "Test memory",
                "memory_type": "experience"
            }

            result = await client.store(
                content="Test memory",
                memory_type="experience",
                importance=0.8
            )

            assert result["id"] == "mem_123"
            assert result["memory_type"] == "experience"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_memory_with_tags(self, config):
        """HYPOTHESIS: store() accepts tags parameter."""
        client = MemoryClient(config)

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"id": "mem_123"}

            await client.store(
                content="Tagged memory",
                memory_type="fact",
                tags=["important", "project_x"]
            )

            call_json = mock_post.call_args[1]["json"]
            assert "tags" in call_json
            assert call_json["tags"] == ["important", "project_x"]


class TestMemoryClientSearch:
    """Test memory search."""

    @pytest.mark.asyncio
    async def test_search_memories_success(self, config):
        """HYPOTHESIS: search() finds relevant memories."""
        client = MemoryClient(config)

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {
                "memories": [
                    {"id": "mem_1", "content": "First memory"},
                    {"id": "mem_2", "content": "Second memory"}
                ],
                "count": 2
            }

            result = await client.search(query="test query", limit=10)

            assert result["count"] == 2
            assert len(result["memories"]) == 2
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_memory_type_filter(self, config):
        """HYPOTHESIS: search() filters by memory_type."""
        client = MemoryClient(config)

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"memories": [], "count": 0}

            await client.search(
                query="test",
                memory_type="experience",
                limit=5
            )

            call_json = mock_post.call_args[1]["json"]
            assert call_json["memory_type"] == "experience"


class TestMemoryClientConsolidate:
    """Test memory consolidation."""

    @pytest.mark.asyncio
    async def test_consolidate_success(self, config):
        """HYPOTHESIS: consolidate() moves memories to vault."""
        client = MemoryClient(config)

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {
                "consolidated": 15,
                "vault_size": 150
            }

            result = await client.consolidate(threshold=0.8)

            assert result["consolidated"] == 15
            assert result["vault_size"] == 150
            mock_post.assert_called_once()


class TestMemoryClientDecay:
    """Test importance decay."""

    @pytest.mark.asyncio
    async def test_decay_importance_success(self, config):
        """HYPOTHESIS: decay() reduces importance over time."""
        client = MemoryClient(config)

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {
                "affected": 50,
                "decay_rate": 0.1
            }

            result = await client.decay(decay_rate=0.1)

            assert result["affected"] == 50
            assert result["decay_rate"] == 0.1
            mock_post.assert_called_once()


class TestMemoryClientGet:
    """Test memory retrieval."""

    @pytest.mark.asyncio
    async def test_get_memory_by_id(self, config):
        """HYPOTHESIS: get() retrieves specific memory."""
        client = MemoryClient(config)

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "id": "mem_123",
                "content": "Specific memory",
                "importance": 0.9
            }

            result = await client.get("mem_123")

            assert result["id"] == "mem_123"
            assert result["content"] == "Specific memory"
            mock_get.assert_called_once()


class TestMemoryClientDelete:
    """Test memory deletion."""

    @pytest.mark.asyncio
    async def test_delete_memory_success(self, config):
        """HYPOTHESIS: delete() removes memory."""
        client = MemoryClient(config)

        with patch.object(client.client, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {"success": True}

            result = await client.delete("mem_123")

            assert result["success"] is True
            mock_delete.assert_called_once()


class TestMemoryClientLifecycle:
    """Test client lifecycle management."""

    @pytest.mark.asyncio
    async def test_close_client(self, config):
        """HYPOTHESIS: close() releases resources."""
        client = MemoryClient(config)

        with patch.object(client.client, 'close', new_callable=AsyncMock) as mock_close:
            await client.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, config):
        """HYPOTHESIS: Context manager auto-closes client."""
        async with MemoryClient(config) as client:
            assert client is not None
