"""
Unit tests for TaskDecomposer.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Any

from backend.services.meta_orchestrator.core.task_decomposer import TaskDecomposer, DecompositionStrategy
from backend.services.meta_orchestrator.plugins.base import Task, TaskPriority

@pytest.mark.asyncio
async def test_needs_decomposition():
    decomposer = TaskDecomposer()
    
    # Simple task
    task1 = Task(task_id="1", type="test", description="Simple task", context={})
    assert not decomposer._needs_decomposition(task1)
    
    # Complex task
    task2 = Task(task_id="2", type="test", description="Do this and then do that", context={})
    assert decomposer._needs_decomposition(task2)
    
    # Critical task
    task3 = Task(task_id="3", type="test", description="Simple", context={}, priority=TaskPriority.CRITICAL)
    assert decomposer._needs_decomposition(task3)

@pytest.mark.asyncio
async def test_rule_based_decompose():
    decomposer = TaskDecomposer()
    task = Task(task_id="1", type="infrastructure", description="Fix server", context={})
    
    subtasks = decomposer._rule_based_decompose(task)
    assert len(subtasks) == 4
    assert subtasks[0].type == "monitoring"
    assert subtasks[3].is_atomic is True

@pytest.mark.asyncio
async def test_llm_decompose():
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = """
    ```json
    [
        {
            "type": "analysis",
            "description": "Analyze logs",
            "priority": "high",
            "dependencies": []
        },
        {
            "type": "execution",
            "description": "Fix issue",
            "priority": "high",
            "dependencies": [0]
        }
    ]
    ```
    """
    mock_gemini.generate_content = AsyncMock(return_value=mock_response)
    
    decomposer = TaskDecomposer(gemini_client=mock_gemini)
    task = Task(task_id="1", type="test", description="Complex task", context={})
    
    subtasks = await decomposer._llm_decompose(task)
    assert len(subtasks) == 2
    assert subtasks[0].description == "Analyze logs"
    assert subtasks[1].dependencies == ["1.1"]
