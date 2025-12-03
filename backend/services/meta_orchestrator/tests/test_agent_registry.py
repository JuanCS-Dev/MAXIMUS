"""
Unit tests for AgentRegistry.
"""

from __future__ import annotations

import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock, patch

from core.agent_registry import AgentRegistry
from plugins.base import AgentPlugin, AgentPluginMetadata, Task, TaskResult, TaskStatus


class MockAgent(AgentPlugin):
    """Mock agent for testing."""

    def __init__(
        self,
        name: str,
        capabilities: List[str],
        healthy: bool = True,
        can_handle_result: bool = True,
    ):
        self._name = name
        self._capabilities = capabilities
        self._healthy = healthy
        self._can_handle_result = can_handle_result
        self._shutdown_called = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def capabilities(self) -> List[str]:
        return self._capabilities

    @property
    def description(self) -> str:
        return "Mock agent"

    async def can_handle(self, task: Task) -> bool:
        if not self._can_handle_result:
            return False
        return task.type in self._capabilities

    async def estimate_effort(self, task: Task) -> float:
        return 0.5

    async def execute(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.task_id, status=TaskStatus.COMPLETED, output={"result": "success"}
        )

    async def health_check(self) -> Dict[str, Any]:
        return {"healthy": self._healthy, "status": "operational"}

    async def shutdown(self) -> None:
        self._shutdown_called = True


class MockAgentWithError(AgentPlugin):
    """Mock agent that raises errors."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def capabilities(self) -> List[str]:
        return ["error"]

    @property
    def description(self) -> str:
        return "Error agent"

    async def can_handle(self, task: Task) -> bool:
        raise Exception("can_handle error")

    async def estimate_effort(self, task: Task) -> float:
        return 0.5

    async def execute(self, task: Task) -> TaskResult:
        raise Exception("execute error")

    async def health_check(self) -> Dict[str, Any]:
        raise Exception("health_check error")

    async def shutdown(self) -> None:
        raise Exception("shutdown error")


class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def test_init(self):
        """Test registry initialization."""
        registry = AgentRegistry()

        assert registry._agents == {}
        assert registry._initialized is False

    @pytest.mark.asyncio
    async def test_register_agent(self):
        """Test registering an agent."""
        registry = AgentRegistry()
        agent = MockAgent("test_agent", ["test"])

        await registry.register(agent)

        agents = await registry.list_agents()
        assert len(agents) == 1
        assert agents[0]["name"] == "test_agent"
        assert agents[0]["version"] == "1.0.0"
        assert agents[0]["enabled"] is True

    @pytest.mark.asyncio
    async def test_register_agent_with_options(self):
        """Test registering agent with custom options."""
        registry = AgentRegistry()
        agent = MockAgent("test_agent", ["test"])

        await registry.register(
            agent, enabled=False, priority=50, tags=["critical", "infra"]
        )

        agents = await registry.list_agents()
        assert agents[0]["enabled"] is False
        assert agents[0]["priority"] == 50
        assert agents[0]["tags"] == ["critical", "infra"]

    @pytest.mark.asyncio
    async def test_register_duplicate_raises_error(self):
        """Test registering duplicate agent raises error."""
        registry = AgentRegistry()
        agent = MockAgent("test_agent", ["test"])

        await registry.register(agent)

        with pytest.raises(ValueError, match="already registered"):
            await registry.register(agent)

    @pytest.mark.asyncio
    async def test_unregister_agent(self):
        """Test unregistering an agent."""
        registry = AgentRegistry()
        agent = MockAgent("test_agent", ["test"])

        await registry.register(agent)
        await registry.unregister("test_agent")

        agents = await registry.list_agents()
        assert len(agents) == 0

    @pytest.mark.asyncio
    async def test_unregister_calls_shutdown(self):
        """Test unregister calls agent shutdown."""
        registry = AgentRegistry()
        agent = MockAgent("test_agent", ["test"])

        await registry.register(agent)
        await registry.unregister("test_agent")

        assert agent._shutdown_called is True

    @pytest.mark.asyncio
    async def test_unregister_nonexistent_raises_error(self):
        """Test unregistering nonexistent agent raises error."""
        registry = AgentRegistry()

        with pytest.raises(KeyError, match="not found"):
            await registry.unregister("nonexistent")

    @pytest.mark.asyncio
    async def test_unregister_handles_shutdown_error(self):
        """Test unregister handles shutdown errors gracefully."""
        registry = AgentRegistry()
        agent = MockAgentWithError("error_agent")

        await registry.register(agent)
        # Should not raise even if shutdown fails
        await registry.unregister("error_agent")

    @pytest.mark.asyncio
    async def test_select_agent_finds_capable(self):
        """Test selecting agent finds capable agent."""
        registry = AgentRegistry()
        agent1 = MockAgent("agent1", ["type1"])
        agent2 = MockAgent("agent2", ["type2"])

        await registry.register(agent1)
        await registry.register(agent2)

        task = Task(task_id="1", type="type1", description="test", context={})
        selected = await registry.select_agent(task)

        assert selected is not None
        assert selected.name == "agent1"

    @pytest.mark.asyncio
    async def test_select_agent_no_match(self):
        """Test selecting agent returns None when no match."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent)

        task = Task(task_id="1", type="unknown", description="test", context={})
        selected = await registry.select_agent(task)

        assert selected is None

    @pytest.mark.asyncio
    async def test_select_agent_skips_disabled(self):
        """Test selecting agent skips disabled agents."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent, enabled=False)

        task = Task(task_id="1", type="type1", description="test", context={})
        selected = await registry.select_agent(task)

        assert selected is None

    @pytest.mark.asyncio
    async def test_select_agent_skips_unhealthy(self):
        """Test selecting agent skips unhealthy agents."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"], healthy=False)

        await registry.register(agent)

        task = Task(task_id="1", type="type1", description="test", context={})
        selected = await registry.select_agent(task)

        assert selected is None

    @pytest.mark.asyncio
    async def test_select_agent_handles_can_handle_error(self):
        """Test selecting agent handles can_handle errors."""
        registry = AgentRegistry()
        agent = MockAgentWithError("error_agent")

        await registry.register(agent)

        task = Task(task_id="1", type="error", description="test", context={})
        selected = await registry.select_agent(task)

        assert selected is None

    @pytest.mark.asyncio
    async def test_select_agent_handles_health_check_error(self):
        """Test selecting agent handles health check errors."""
        registry = AgentRegistry()
        # Create a mock that passes can_handle but fails health check
        agent = MagicMock(spec=AgentPlugin)
        agent.name = "mock_agent"
        agent.version = "1.0.0"
        agent.capabilities = ["test"]
        agent.can_handle = AsyncMock(return_value=True)
        agent.health_check = AsyncMock(side_effect=Exception("health error"))

        await registry.register(agent)

        task = Task(task_id="1", type="test", description="test", context={})
        selected = await registry.select_agent(task)

        assert selected is None

    @pytest.mark.asyncio
    async def test_select_agent_by_priority(self):
        """Test selecting agent respects priority."""
        registry = AgentRegistry()
        agent1 = MockAgent("low_priority", ["test"])
        agent2 = MockAgent("high_priority", ["test"])

        await registry.register(agent1, priority=50)
        await registry.register(agent2, priority=200)

        task = Task(task_id="1", type="test", description="test", context={})
        selected = await registry.select_agent(task)

        assert selected is not None
        assert selected.name == "high_priority"

    @pytest.mark.asyncio
    async def test_get_agent(self):
        """Test getting agent by name."""
        registry = AgentRegistry()
        agent = MockAgent("test_agent", ["test"])

        await registry.register(agent)
        retrieved = await registry.get_agent("test_agent")

        assert retrieved is not None
        assert retrieved.name == "test_agent"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self):
        """Test getting nonexistent agent returns None."""
        registry = AgentRegistry()

        retrieved = await registry.get_agent("nonexistent")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_list_agents_all(self):
        """Test listing all agents."""
        registry = AgentRegistry()
        agent1 = MockAgent("agent1", ["type1"])
        agent2 = MockAgent("agent2", ["type2"])

        await registry.register(agent1)
        await registry.register(agent2, enabled=False)

        agents = await registry.list_agents()

        assert len(agents) == 2

    @pytest.mark.asyncio
    async def test_list_agents_enabled_only(self):
        """Test listing enabled agents only."""
        registry = AgentRegistry()
        agent1 = MockAgent("agent1", ["type1"])
        agent2 = MockAgent("agent2", ["type2"])

        await registry.register(agent1)
        await registry.register(agent2, enabled=False)

        agents = await registry.list_agents(enabled_only=True)

        assert len(agents) == 1
        assert agents[0]["name"] == "agent1"

    @pytest.mark.asyncio
    async def test_list_agents_by_tags(self):
        """Test listing agents by tags."""
        registry = AgentRegistry()
        agent1 = MockAgent("agent1", ["type1"])
        agent2 = MockAgent("agent2", ["type2"])

        await registry.register(agent1, tags=["infra"])
        await registry.register(agent2, tags=["data"])

        agents = await registry.list_agents(tags={"infra"})

        assert len(agents) == 1
        assert agents[0]["name"] == "agent1"

    @pytest.mark.asyncio
    async def test_list_agents_stats(self):
        """Test listing agents includes stats."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent)
        await registry.update_stats("agent1", True, 100)

        agents = await registry.list_agents()

        assert agents[0]["stats"]["total_executed"] == 1
        assert agents[0]["stats"]["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_update_stats_success(self):
        """Test updating stats for successful execution."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent)
        await registry.update_stats("agent1", True, 100)
        await registry.update_stats("agent1", True, 200)

        agents = await registry.list_agents()
        stats = agents[0]["stats"]

        assert stats["total_executed"] == 2
        assert stats["total_failed"] == 0
        assert stats["success_rate"] == 1.0
        assert stats["avg_exec_time_ms"] == 150.0

    @pytest.mark.asyncio
    async def test_update_stats_failure(self):
        """Test updating stats for failed execution."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent)
        await registry.update_stats("agent1", True, 100)
        await registry.update_stats("agent1", False, 200)

        agents = await registry.list_agents()
        stats = agents[0]["stats"]

        assert stats["total_executed"] == 1
        assert stats["total_failed"] == 1
        assert stats["success_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_update_stats_nonexistent_agent(self):
        """Test updating stats for nonexistent agent does nothing."""
        registry = AgentRegistry()

        # Should not raise
        await registry.update_stats("nonexistent", True, 100)

    @pytest.mark.asyncio
    async def test_enable_agent(self):
        """Test enabling an agent."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent, enabled=False)
        await registry.enable_agent("agent1")

        agents = await registry.list_agents()
        assert agents[0]["enabled"] is True

    @pytest.mark.asyncio
    async def test_enable_nonexistent_agent(self):
        """Test enabling nonexistent agent does nothing."""
        registry = AgentRegistry()

        # Should not raise
        await registry.enable_agent("nonexistent")

    @pytest.mark.asyncio
    async def test_disable_agent(self):
        """Test disabling an agent."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent)
        await registry.disable_agent("agent1")

        agents = await registry.list_agents()
        assert agents[0]["enabled"] is False

    @pytest.mark.asyncio
    async def test_disable_nonexistent_agent(self):
        """Test disabling nonexistent agent does nothing."""
        registry = AgentRegistry()

        # Should not raise
        await registry.disable_agent("nonexistent")

    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """Test health check for all agents."""
        registry = AgentRegistry()
        agent1 = MockAgent("agent1", ["type1"])
        agent2 = MockAgent("agent2", ["type2"])

        await registry.register(agent1)
        await registry.register(agent2)

        health = await registry.health_check_all()

        assert "agent1" in health
        assert "agent2" in health
        assert health["agent1"]["healthy"] is True
        assert health["agent2"]["healthy"] is True

    @pytest.mark.asyncio
    async def test_health_check_all_with_error(self):
        """Test health check handles errors."""
        registry = AgentRegistry()
        agent = MockAgentWithError("error_agent")

        await registry.register(agent)

        health = await registry.health_check_all()

        assert "error_agent" in health
        assert health["error_agent"]["healthy"] is False
        assert "error" in health["error_agent"]

    @pytest.mark.asyncio
    async def test_health_check_includes_enabled_status(self):
        """Test health check includes enabled status."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent, enabled=False)

        health = await registry.health_check_all()

        assert health["agent1"]["enabled"] is False

    @pytest.mark.asyncio
    async def test_concurrent_registration(self):
        """Test concurrent agent registration."""
        registry = AgentRegistry()

        agents = [MockAgent(f"agent{i}", [f"type{i}"]) for i in range(10)]

        # Register all concurrently
        await asyncio.gather(*[registry.register(agent) for agent in agents])

        listed = await registry.list_agents()
        assert len(listed) == 10

    @pytest.mark.asyncio
    async def test_agent_metadata_timestamps(self):
        """Test agent metadata has registration timestamp."""
        registry = AgentRegistry()
        agent = MockAgent("agent1", ["type1"])

        await registry.register(agent)

        # Access internal to check timestamp
        assert registry._agents["agent1"].registration_timestamp is not None
