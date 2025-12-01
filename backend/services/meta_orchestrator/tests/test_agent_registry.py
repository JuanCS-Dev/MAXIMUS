"""
Unit tests for AgentRegistry.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock

from backend.services.meta_orchestrator.core.agent_registry import AgentRegistry
from backend.services.meta_orchestrator.plugins.base import AgentPlugin, Task, TaskResult, TaskStatus

class MockAgent(AgentPlugin):
    """Mock agent for testing"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self._name = name
        self._capabilities = capabilities
        
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
        return task.type in self._capabilities
        
    async def estimate_effort(self, task: Task) -> float:
        return 0.5
        
    async def execute(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            output={"result": "success"}
        )
        
    async def health_check(self) -> Dict[str, Any]:
        return {"healthy": True, "status": "operational"}

@pytest.mark.asyncio
async def test_register_unregister():
    registry = AgentRegistry()
    agent = MockAgent("test_agent", ["test"])
    
    await registry.register(agent)
    agents = await registry.list_agents()
    assert len(agents) == 1
    assert agents[0]["name"] == "test_agent"
    
    await registry.unregister("test_agent")
    agents = await registry.list_agents()
    assert len(agents) == 0

@pytest.mark.asyncio
async def test_select_agent():
    registry = AgentRegistry()
    agent1 = MockAgent("agent1", ["type1"])
    agent2 = MockAgent("agent2", ["type2"])
    
    await registry.register(agent1)
    await registry.register(agent2)
    
    task1 = Task(task_id="1", type="type1", description="test", context={})
    selected = await registry.select_agent(task1)
    assert selected is not None
    assert selected.name == "agent1"
    
    task2 = Task(task_id="2", type="type2", description="test", context={})
    selected = await registry.select_agent(task2)
    assert selected is not None
    assert selected.name == "agent2"
    
    task3 = Task(task_id="3", type="type3", description="test", context={})
    selected = await registry.select_agent(task3)
    assert selected is None

@pytest.mark.asyncio
async def test_health_check_all():
    registry = AgentRegistry()
    agent = MockAgent("test_agent", ["test"])
    await registry.register(agent)
    
    health = await registry.health_check_all()
    assert "test_agent" in health
    assert health["test_agent"]["healthy"] is True
