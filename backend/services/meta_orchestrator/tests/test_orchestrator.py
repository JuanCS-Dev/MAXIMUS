"""
Unit tests for Orchestrator.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List

from backend.services.meta_orchestrator.core.orchestrator import Orchestrator
from backend.services.meta_orchestrator.core.agent_registry import AgentRegistry
from backend.services.meta_orchestrator.core.task_decomposer import TaskDecomposer
from backend.services.meta_orchestrator.plugins.base import Task, TaskResult, TaskStatus, AgentPlugin

@pytest.mark.asyncio
async def test_execute_atomic_mission():
    mock_registry = MagicMock(spec=AgentRegistry)
    mock_decomposer = MagicMock(spec=TaskDecomposer)
    mock_agent = MagicMock(spec=AgentPlugin)
    mock_agent.name = "test_agent"
    
    # Setup mock agent execution
    mock_result = TaskResult(
        task_id="1",
        status=TaskStatus.COMPLETED,
        output={"result": "success"}
    )
    mock_agent.execute = AsyncMock(return_value=mock_result)
    
    # Setup registry
    mock_registry.select_agent = AsyncMock(return_value=mock_agent)
    mock_registry.update_stats = AsyncMock()
    
    orchestrator = Orchestrator(mock_registry, mock_decomposer)
    mission = Task(task_id="1", type="test", description="Atomic mission", context={}, is_atomic=True)
    
    result = await orchestrator.execute_mission(mission)
    
    assert result.status == TaskStatus.COMPLETED
    assert result.output == {"result": "success"}
    mock_registry.select_agent.assert_called_once()
    mock_agent.execute.assert_called_once()

@pytest.mark.asyncio
async def test_execute_complex_mission():
    mock_registry = MagicMock(spec=AgentRegistry)
    mock_decomposer = MagicMock(spec=TaskDecomposer)
    mock_agent = MagicMock(spec=AgentPlugin)
    mock_agent.name = "test_agent"
    
    # Setup mock agent execution
    mock_result = TaskResult(
        task_id="subtask",
        status=TaskStatus.COMPLETED,
        output={"result": "success"}
    )
    mock_agent.execute = AsyncMock(return_value=mock_result)
    mock_registry.select_agent = AsyncMock(return_value=mock_agent)
    mock_registry.update_stats = AsyncMock()
    
    # Setup decomposition
    subtask = Task(task_id="1.1", type="test", description="Subtask", context={}, is_atomic=True)
    mock_decomposer.decompose = AsyncMock(return_value=[subtask])
    
    orchestrator = Orchestrator(mock_registry, mock_decomposer)
    mission = Task(task_id="1", type="test", description="Complex mission", context={})
    
    result = await orchestrator.execute_mission(mission)
    
    assert result.status == TaskStatus.COMPLETED
    assert "1.1" in result.output["subtasks"]
    mock_decomposer.decompose.assert_called_once()
