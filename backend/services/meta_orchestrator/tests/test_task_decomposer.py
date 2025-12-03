"""
Unit tests for TaskDecomposer.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Any

from core.task_decomposer import TaskDecomposer, DecompositionStrategy
from plugins.base import Task, TaskPriority


class TestDecompositionStrategy:
    """Tests for DecompositionStrategy."""

    def test_default_strategy(self):
        """Test default strategy values."""
        strategy = DecompositionStrategy()

        assert strategy.max_depth == 3
        assert strategy.max_children == 5
        assert strategy.use_llm is True
        assert strategy.parallel_execution is True

    def test_custom_strategy(self):
        """Test custom strategy values."""
        strategy = DecompositionStrategy(
            max_depth=5,
            max_children=10,
            use_llm=False,
            parallel_execution=False,
        )

        assert strategy.max_depth == 5
        assert strategy.max_children == 10
        assert strategy.use_llm is False
        assert strategy.parallel_execution is False


class TestTaskDecomposer:
    """Tests for TaskDecomposer."""

    def test_init_default(self):
        """Test default initialization."""
        decomposer = TaskDecomposer()

        assert decomposer.strategy is not None
        assert decomposer.gemini is None
        assert decomposer._task_counter == 0

    def test_init_with_strategy(self):
        """Test initialization with custom strategy."""
        strategy = DecompositionStrategy(max_depth=5)
        decomposer = TaskDecomposer(strategy=strategy)

        assert decomposer.strategy.max_depth == 5

    def test_init_with_gemini(self):
        """Test initialization with Gemini client."""
        mock_gemini = MagicMock()
        decomposer = TaskDecomposer(gemini_client=mock_gemini)

        assert decomposer.gemini is mock_gemini

    @pytest.mark.asyncio
    async def test_decompose_atomic_task(self):
        """Test decompose returns atomic task unchanged."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Simple task",
            context={},
            is_atomic=True,
        )

        result = await decomposer.decompose(task)

        assert len(result) == 1
        assert result[0].task_id == "1"
        assert result[0].is_atomic is True

    @pytest.mark.asyncio
    async def test_decompose_max_depth(self):
        """Test decompose respects max depth."""
        strategy = DecompositionStrategy(max_depth=0)
        decomposer = TaskDecomposer(strategy=strategy)
        task = Task(
            task_id="1",
            type="test",
            description="Do this and then do that",
            context={},
        )

        result = await decomposer.decompose(task, depth=0)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_decompose_simple_task_becomes_atomic(self):
        """Test simple task becomes atomic."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Simple task",
            context={},
        )

        result = await decomposer.decompose(task)

        assert len(result) == 1
        assert result[0].is_atomic is True

    @pytest.mark.asyncio
    async def test_decompose_complex_task_rule_based(self):
        """Test complex task decomposition with rules."""
        strategy = DecompositionStrategy(use_llm=False)
        decomposer = TaskDecomposer(strategy=strategy)
        task = Task(
            task_id="1",
            type="infrastructure",
            description="Fix server and restart",
            context={},
        )

        result = await decomposer.decompose(task)

        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_decompose_with_llm(self):
        """Test decomposition with LLM."""
        mock_gemini = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """```json
[
    {"type": "analysis", "description": "Analyze", "priority": "high", "dependencies": []},
    {"type": "execute", "description": "Execute", "priority": "high", "dependencies": [0]}
]
```"""
        mock_gemini.generate_content = AsyncMock(return_value=mock_response)

        strategy = DecompositionStrategy(use_llm=True)
        decomposer = TaskDecomposer(strategy=strategy, gemini_client=mock_gemini)
        task = Task(
            task_id="1",
            type="test",
            description="Complex task and subtasks",
            context={},
        )

        result = await decomposer.decompose(task)

        assert len(result) >= 2
        mock_gemini.generate_content.assert_called()

    @pytest.mark.asyncio
    async def test_decompose_recursive(self):
        """Test recursive decomposition."""
        strategy = DecompositionStrategy(use_llm=False, max_depth=2)
        decomposer = TaskDecomposer(strategy=strategy)
        task = Task(
            task_id="1",
            type="infrastructure",
            description="Complex task and subtasks",
            context={},
        )

        result = await decomposer.decompose(task)

        # Should have multiple subtasks from recursive decomposition
        assert len(result) >= 4  # Infrastructure decomposes to 4 subtasks

    def test_needs_decomposition_simple(self):
        """Test simple task does not need decomposition."""
        decomposer = TaskDecomposer()
        task = Task(task_id="1", type="test", description="Simple task", context={})

        assert not decomposer._needs_decomposition(task)

    def test_needs_decomposition_with_and(self):
        """Test task with 'and' needs decomposition."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Do this and then that",
            context={},
        )

        assert decomposer._needs_decomposition(task)

    def test_needs_decomposition_with_then(self):
        """Test task with 'then' needs decomposition."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="First do this then do that",
            context={},
        )

        assert decomposer._needs_decomposition(task)

    def test_needs_decomposition_with_after(self):
        """Test task with 'after' needs decomposition."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Do this after completing setup",
            context={},
        )

        assert decomposer._needs_decomposition(task)

    def test_needs_decomposition_with_before(self):
        """Test task with 'before' needs decomposition."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Check before deploying",
            context={},
        )

        assert decomposer._needs_decomposition(task)

    def test_needs_decomposition_with_while(self):
        """Test task with 'while' needs decomposition."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Monitor while deploying",
            context={},
        )

        assert decomposer._needs_decomposition(task)

    def test_needs_decomposition_critical_priority(self):
        """Test critical priority task needs decomposition."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Simple",
            context={},
            priority=TaskPriority.CRITICAL,
        )

        assert decomposer._needs_decomposition(task)

    def test_needs_decomposition_high_priority(self):
        """Test high priority task doesn't automatically need decomposition."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="test",
            description="Simple",
            context={},
            priority=TaskPriority.HIGH,
        )

        assert not decomposer._needs_decomposition(task)

    @pytest.mark.asyncio
    async def test_llm_decompose_success(self):
        """Test successful LLM decomposition."""
        mock_gemini = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """```json
[
    {"type": "analysis", "description": "Analyze logs", "priority": "high", "dependencies": []},
    {"type": "execution", "description": "Fix issue", "priority": "high", "dependencies": [0]}
]
```"""
        mock_gemini.generate_content = AsyncMock(return_value=mock_response)

        decomposer = TaskDecomposer(gemini_client=mock_gemini)
        task = Task(task_id="1", type="test", description="Complex task", context={})

        subtasks = await decomposer._llm_decompose(task)

        assert len(subtasks) == 2
        assert subtasks[0].description == "Analyze logs"
        assert subtasks[0].priority == TaskPriority.HIGH
        assert subtasks[1].dependencies == ["1.1"]

    @pytest.mark.asyncio
    async def test_llm_decompose_no_gemini_client(self):
        """Test LLM decomposition without client falls back to rules."""
        decomposer = TaskDecomposer()
        task = Task(task_id="1", type="test", description="Complex task", context={})

        subtasks = await decomposer._llm_decompose(task)

        # Should fall back to rule-based
        assert len(subtasks) >= 1

    @pytest.mark.asyncio
    async def test_llm_decompose_api_error_fallback(self):
        """Test LLM decomposition falls back on API error."""
        mock_gemini = MagicMock()
        mock_gemini.generate_content = AsyncMock(side_effect=Exception("API Error"))

        decomposer = TaskDecomposer(gemini_client=mock_gemini)
        task = Task(task_id="1", type="test", description="Complex task", context={})

        subtasks = await decomposer._llm_decompose(task)

        # Should fall back to rule-based
        assert len(subtasks) >= 1

    @pytest.mark.asyncio
    async def test_llm_decompose_with_dependencies(self):
        """Test LLM decomposition handles dependencies."""
        mock_gemini = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """```json
[
    {"type": "step1", "description": "First", "priority": "medium", "dependencies": []},
    {"type": "step2", "description": "Second", "priority": "medium", "dependencies": [0]},
    {"type": "step3", "description": "Third", "priority": "medium", "dependencies": [0, 1]}
]
```"""
        mock_gemini.generate_content = AsyncMock(return_value=mock_response)

        decomposer = TaskDecomposer(gemini_client=mock_gemini)
        task = Task(task_id="parent", type="test", description="Task", context={})

        subtasks = await decomposer._llm_decompose(task)

        assert len(subtasks) == 3
        assert subtasks[0].dependencies == []
        assert subtasks[1].dependencies == ["parent.1"]
        assert subtasks[2].dependencies == ["parent.1", "parent.2"]

    def test_rule_based_decompose_infrastructure(self):
        """Test rule-based decomposition for infrastructure task."""
        decomposer = TaskDecomposer()
        task = Task(task_id="1", type="infrastructure", description="Fix server", context={})

        subtasks = decomposer._rule_based_decompose(task)

        assert len(subtasks) == 4
        assert subtasks[0].type == "monitoring"
        assert subtasks[1].type == "analysis"
        assert subtasks[2].type == "planning"
        assert subtasks[3].type == "execution"
        assert subtasks[3].is_atomic is True

    def test_rule_based_decompose_intelligence(self):
        """Test rule-based decomposition for intelligence task."""
        decomposer = TaskDecomposer()
        task = Task(task_id="1", type="intelligence", description="Gather intel", context={})

        subtasks = decomposer._rule_based_decompose(task)

        assert len(subtasks) == 2
        assert subtasks[0].type == "collection"
        assert subtasks[1].type == "analysis"
        assert subtasks[1].is_atomic is True

    def test_rule_based_decompose_generic(self):
        """Test rule-based decomposition for generic task."""
        decomposer = TaskDecomposer()
        task = Task(task_id="1", type="custom", description="Custom task", context={})

        subtasks = decomposer._rule_based_decompose(task)

        assert len(subtasks) == 2
        assert "Analyze:" in subtasks[0].description
        assert "Execute:" in subtasks[1].description
        assert subtasks[1].dependencies == ["1.1"]

    def test_generate_task_id(self):
        """Test task ID generation."""
        decomposer = TaskDecomposer()

        assert decomposer._generate_task_id("parent", 0) == "parent.1"
        assert decomposer._generate_task_id("parent", 1) == "parent.2"
        assert decomposer._generate_task_id("1.1", 0) == "1.1.1"

    def test_parse_priority(self):
        """Test priority parsing."""
        decomposer = TaskDecomposer()

        assert decomposer._parse_priority("low") == TaskPriority.LOW
        assert decomposer._parse_priority("medium") == TaskPriority.MEDIUM
        assert decomposer._parse_priority("high") == TaskPriority.HIGH
        assert decomposer._parse_priority("critical") == TaskPriority.CRITICAL
        assert decomposer._parse_priority("unknown") == TaskPriority.MEDIUM
        assert decomposer._parse_priority("HIGH") == TaskPriority.HIGH

    def test_parse_llm_response_dict_format(self):
        """Test parsing dict format response."""
        decomposer = TaskDecomposer()
        response = MagicMock()
        response.text = '[{"type": "test", "description": "Test"}]'

        result = decomposer._parse_llm_response({"text": '[{"type": "test", "description": "Test"}]'})

        assert len(result) == 1
        assert result[0]["type"] == "test"

    def test_parse_llm_response_object_format(self):
        """Test parsing object with text attribute."""
        decomposer = TaskDecomposer()
        response = MagicMock()
        response.text = '[{"type": "test", "description": "Test"}]'

        result = decomposer._parse_llm_response(response)

        assert len(result) == 1

    def test_parse_llm_response_markdown_wrapped(self):
        """Test parsing markdown-wrapped JSON."""
        decomposer = TaskDecomposer()
        response = MagicMock()
        response.text = """```json
[{"type": "test", "description": "Test"}]
```"""

        result = decomposer._parse_llm_response(response)

        assert len(result) == 1
        assert result[0]["type"] == "test"

    def test_parse_llm_response_invalid_json(self):
        """Test parsing invalid JSON returns empty list."""
        decomposer = TaskDecomposer()
        response = MagicMock()
        response.text = "not valid json"

        result = decomposer._parse_llm_response(response)

        assert result == []

    def test_parse_llm_response_string_format(self):
        """Test parsing string format."""
        decomposer = TaskDecomposer()

        result = decomposer._parse_llm_response('[{"type": "test", "description": "Test"}]')

        assert len(result) == 1

    def test_decompose_infrastructure_task_dependencies(self):
        """Test infrastructure task has correct dependencies."""
        decomposer = TaskDecomposer()
        task = Task(task_id="main", type="infrastructure", description="Fix", context={})

        subtasks = decomposer._decompose_infrastructure_task(task)

        assert subtasks[1].dependencies == ["main.1"]
        assert subtasks[2].dependencies == ["main.2"]
        assert subtasks[3].dependencies == ["main.3"]

    def test_decompose_intelligence_task_dependencies(self):
        """Test intelligence task has correct dependencies."""
        decomposer = TaskDecomposer()
        task = Task(task_id="main", type="intelligence", description="Gather", context={})

        subtasks = decomposer._decompose_intelligence_task(task)

        assert subtasks[0].dependencies == []
        assert subtasks[1].dependencies == ["main.1"]

    def test_decompose_preserves_context(self):
        """Test decomposition preserves task context."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="infrastructure",
            description="Fix",
            context={"env": "production", "region": "us-east-1"},
        )

        subtasks = decomposer._rule_based_decompose(task)

        for subtask in subtasks:
            assert subtask.context == task.context

    def test_decompose_preserves_priority(self):
        """Test decomposition preserves task priority."""
        decomposer = TaskDecomposer()
        task = Task(
            task_id="1",
            type="infrastructure",
            description="Fix",
            context={},
            priority=TaskPriority.HIGH,
        )

        subtasks = decomposer._rule_based_decompose(task)

        for subtask in subtasks:
            assert subtask.priority == TaskPriority.HIGH
