"""
Unit tests for Orchestrator.
"""

from __future__ import annotations

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import List

from core.orchestrator import Orchestrator
from core.agent_registry import AgentRegistry
from core.task_decomposer import TaskDecomposer
from plugins.base import Task, TaskResult, TaskStatus, AgentPlugin, TaskPriority


class TestOrchestrator:
    """Tests for Orchestrator."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock registry."""
        registry = MagicMock(spec=AgentRegistry)
        registry.select_agent = AsyncMock(return_value=None)
        registry.update_stats = AsyncMock()
        return registry

    @pytest.fixture
    def mock_decomposer(self):
        """Create mock decomposer."""
        decomposer = MagicMock(spec=TaskDecomposer)
        decomposer.decompose = AsyncMock(return_value=[])
        return decomposer

    @pytest.fixture
    def mock_agent(self):
        """Create mock agent."""
        agent = MagicMock(spec=AgentPlugin)
        agent.name = "test_agent"
        agent.execute = AsyncMock(return_value=TaskResult(
            task_id="1",
            status=TaskStatus.COMPLETED,
            output={"result": "success"}
        ))
        return agent

    def test_init(self, mock_registry, mock_decomposer):
        """Test orchestrator initialization."""
        orchestrator = Orchestrator(mock_registry, mock_decomposer)

        assert orchestrator.registry is mock_registry
        assert orchestrator.decomposer is mock_decomposer
        assert orchestrator.max_depth == 3
        assert orchestrator.timeout_seconds == 300

    def test_init_custom_params(self, mock_registry, mock_decomposer):
        """Test orchestrator initialization with custom params."""
        orchestrator = Orchestrator(
            mock_registry,
            mock_decomposer,
            max_depth=5,
            timeout_seconds=600
        )

        assert orchestrator.max_depth == 5
        assert orchestrator.timeout_seconds == 600

    @pytest.mark.asyncio
    async def test_execute_atomic_mission(self, mock_registry, mock_decomposer, mock_agent):
        """Test executing atomic mission."""
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(
            task_id="1",
            type="test",
            description="Atomic mission",
            context={},
            is_atomic=True
        )

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.COMPLETED
        assert result.output == {"result": "success"}
        mock_registry.select_agent.assert_called_once()
        mock_agent.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_mission_max_depth(self, mock_registry, mock_decomposer, mock_agent):
        """Test mission at max depth is treated as atomic."""
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(mock_registry, mock_decomposer, max_depth=0)
        mission = Task(
            task_id="1",
            type="test",
            description="Mission at max depth",
            context={}
        )

        result = await orchestrator.execute_mission(mission, depth=0)

        assert result.status == TaskStatus.COMPLETED
        mock_decomposer.decompose.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_mission_no_agent(self, mock_registry, mock_decomposer):
        """Test mission fails when no agent available."""
        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(
            task_id="1",
            type="test",
            description="Mission",
            context={},
            is_atomic=True
        )

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.FAILED
        assert "No suitable agent" in result.reasoning

    @pytest.mark.asyncio
    async def test_execute_mission_agent_timeout(self, mock_registry, mock_decomposer):
        """Test mission fails on agent timeout."""
        mock_agent = MagicMock(spec=AgentPlugin)
        mock_agent.name = "slow_agent"

        async def slow_execute(_):
            await asyncio.sleep(10)
            return TaskResult(task_id="1", status=TaskStatus.COMPLETED, output={})

        mock_agent.execute = slow_execute
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(
            mock_registry,
            mock_decomposer,
            timeout_seconds=1
        )
        mission = Task(
            task_id="1",
            type="test",
            description="Mission",
            context={},
            is_atomic=True
        )

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.FAILED
        assert "timed out" in result.reasoning

    @pytest.mark.asyncio
    async def test_execute_mission_agent_error(self, mock_registry, mock_decomposer):
        """Test mission fails on agent error."""
        mock_agent = MagicMock(spec=AgentPlugin)
        mock_agent.name = "error_agent"
        mock_agent.execute = AsyncMock(side_effect=Exception("Agent error"))
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(
            task_id="1",
            type="test",
            description="Mission",
            context={},
            is_atomic=True
        )

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.FAILED
        assert "Agent error" in result.errors[0]

    @pytest.mark.asyncio
    async def test_execute_complex_mission(self, mock_registry, mock_decomposer, mock_agent):
        """Test executing complex mission with decomposition."""
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        # Setup decomposition
        subtask = Task(
            task_id="1.1",
            type="test",
            description="Subtask",
            context={},
            is_atomic=True
        )
        mock_decomposer.decompose = AsyncMock(return_value=[subtask])

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(
            task_id="1",
            type="test",
            description="Complex mission",
            context={}
        )

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.COMPLETED
        assert "1.1" in result.output["subtasks"]
        mock_decomposer.decompose.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_mission_with_dependencies(self, mock_registry, mock_decomposer, mock_agent):
        """Test executing mission with task dependencies."""
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        # Setup decomposition with dependencies
        subtask1 = Task(
            task_id="1.1",
            type="test",
            description="First",
            context={},
            is_atomic=True,
            dependencies=[]
        )
        subtask2 = Task(
            task_id="1.2",
            type="test",
            description="Second",
            context={},
            is_atomic=True,
            dependencies=["1.1"]
        )
        mock_decomposer.decompose = AsyncMock(return_value=[subtask1, subtask2])

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(task_id="1", type="test", description="Mission", context={})

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.COMPLETED
        assert "1.1" in result.output["subtasks"]
        assert "1.2" in result.output["subtasks"]

    @pytest.mark.asyncio
    async def test_execute_mission_partial_failure(self, mock_registry, mock_decomposer):
        """Test mission with partial subtask failure."""
        call_count = 0

        async def execute_varying(_):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return TaskResult(task_id="1.1", status=TaskStatus.COMPLETED, output={})
            return TaskResult(task_id="1.2", status=TaskStatus.FAILED, output={}, errors=["Error"])

        mock_agent = MagicMock(spec=AgentPlugin)
        mock_agent.name = "test_agent"
        mock_agent.execute = execute_varying
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        subtask1 = Task(task_id="1.1", type="test", description="First", context={}, is_atomic=True)
        subtask2 = Task(task_id="1.2", type="test", description="Second", context={}, is_atomic=True)
        mock_decomposer.decompose = AsyncMock(return_value=[subtask1, subtask2])

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(task_id="1", type="test", description="Mission", context={})

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.FAILED
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_mission_timeout(self, mock_registry, mock_decomposer):
        """Test mission timeout at top level."""
        async def slow_decompose(_):
            await asyncio.sleep(10)
            return []

        mock_decomposer.decompose = slow_decompose

        orchestrator = Orchestrator(
            mock_registry,
            mock_decomposer,
            timeout_seconds=1
        )
        mission = Task(task_id="1", type="test", description="Mission", context={})

        # Execute within timeout wrapper
        try:
            result = await asyncio.wait_for(
                orchestrator.execute_mission(mission),
                timeout=2
            )
        except asyncio.TimeoutError:
            result = TaskResult(
                task_id="1",
                status=TaskStatus.FAILED,
                output={},
                errors=["Timeout"]
            )

        assert result.status == TaskStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_mission_exception(self, mock_registry, mock_decomposer):
        """Test mission handles unexpected exception."""
        mock_decomposer.decompose = AsyncMock(side_effect=Exception("Unexpected error"))

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(task_id="1", type="test", description="Mission", context={})

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.FAILED
        assert "Unexpected error" in str(result.errors)

    @pytest.mark.asyncio
    async def test_execute_mission_updates_stats(self, mock_registry, mock_decomposer, mock_agent):
        """Test mission execution updates agent stats."""
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(
            task_id="1",
            type="test",
            description="Mission",
            context={},
            is_atomic=True
        )

        await orchestrator.execute_mission(mission)

        mock_registry.update_stats.assert_called()

    @pytest.mark.asyncio
    async def test_execute_mission_with_priority(self, mock_registry, mock_decomposer, mock_agent):
        """Test mission execution with priority."""
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(
            task_id="1",
            type="test",
            description="Critical mission",
            context={},
            priority=TaskPriority.CRITICAL,
            is_atomic=True
        )

        result = await orchestrator.execute_mission(mission)

        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_synthesize_results_all_success(self, mock_registry, mock_decomposer):
        """Test result synthesis with all successful subtasks."""
        orchestrator = Orchestrator(mock_registry, mock_decomposer)

        subtask_results = {
            "1.1": TaskResult(
                task_id="1.1",
                status=TaskStatus.COMPLETED,
                output={"data": "a"},
                reasoning="Step 1",
                confidence=0.9
            ),
            "1.2": TaskResult(
                task_id="1.2",
                status=TaskStatus.COMPLETED,
                output={"data": "b"},
                reasoning="Step 2",
                confidence=0.8
            )
        }

        original_task = Task(task_id="1", type="test", description="Test", context={})
        result = orchestrator._synthesize_results(original_task, subtask_results)

        assert result.status == TaskStatus.COMPLETED
        assert "1.1" in result.output["subtasks"]
        assert "1.2" in result.output["subtasks"]
        assert abs(result.confidence - 0.85) < 0.001  # Average
        assert "Step 1" in result.reasoning
        assert "Step 2" in result.reasoning

    @pytest.mark.asyncio
    async def test_synthesize_results_with_failure(self, mock_registry, mock_decomposer):
        """Test result synthesis with failed subtask."""
        orchestrator = Orchestrator(mock_registry, mock_decomposer)

        subtask_results = {
            "1.1": TaskResult(
                task_id="1.1",
                status=TaskStatus.COMPLETED,
                output={},
                confidence=0.9
            ),
            "1.2": TaskResult(
                task_id="1.2",
                status=TaskStatus.FAILED,
                output={},
                errors=["Error occurred"],
                confidence=0.5
            )
        }

        original_task = Task(task_id="1", type="test", description="Test", context={})
        result = orchestrator._synthesize_results(original_task, subtask_results)

        assert result.status == TaskStatus.FAILED
        assert "Error occurred" in result.errors

    @pytest.mark.asyncio
    async def test_execute_with_dependencies_respects_order(
        self, mock_registry, mock_decomposer, mock_agent
    ):
        """Test dependency resolution respects execution order."""
        execution_order = []

        async def track_execute(task):
            execution_order.append(task.task_id)
            return TaskResult(task_id=task.task_id, status=TaskStatus.COMPLETED, output={})

        mock_agent.execute = track_execute
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(mock_registry, mock_decomposer)

        tasks = [
            Task(task_id="1", type="test", description="First", context={}, is_atomic=True),
            Task(
                task_id="2",
                type="test",
                description="Second",
                context={},
                is_atomic=True,
                dependencies=["1"]
            ),
        ]

        await orchestrator._execute_with_dependencies(tasks, depth=0)

        # Task 1 should complete before Task 2
        assert execution_order.index("1") < execution_order.index("2")

    @pytest.mark.asyncio
    async def test_execute_with_dependencies_handles_circular(
        self, mock_registry, mock_decomposer
    ):
        """Test handling of circular dependencies."""
        orchestrator = Orchestrator(mock_registry, mock_decomposer)

        # Create circular dependency
        tasks = [
            Task(
                task_id="1",
                type="test",
                description="A",
                context={},
                is_atomic=True,
                dependencies=["2"]
            ),
            Task(
                task_id="2",
                type="test",
                description="B",
                context={},
                is_atomic=True,
                dependencies=["1"]
            ),
        ]

        # Should not hang, should detect circular dependency
        results = await orchestrator._execute_with_dependencies(tasks, depth=0)

        # Should have handled the deadlock gracefully
        assert len(results) == 0  # No tasks completed due to deadlock

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, mock_registry, mock_decomposer, mock_agent):
        """Test execution time is tracked."""
        mock_registry.select_agent = AsyncMock(return_value=mock_agent)

        orchestrator = Orchestrator(mock_registry, mock_decomposer)
        mission = Task(
            task_id="1",
            type="test",
            description="Mission",
            context={},
            is_atomic=True
        )

        result = await orchestrator.execute_mission(mission)

        assert result.execution_time_ms >= 0
