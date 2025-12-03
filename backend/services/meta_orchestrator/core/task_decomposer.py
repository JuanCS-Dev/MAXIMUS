"""
Meta-Orchestrator: Task Decomposer
====================================

Implements ROMA (Recursive Open Meta-Agent) pattern for hierarchical task decomposition.
Breaks down complex missions into atomic, executable subtasks.

Based on research:
- ROMA paper (sentient.xyz, June 2025)
- Google's hierarchical planning systems
- Gemini 3 Pro multi-step reasoning
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, cast
from dataclasses import dataclass
import json
import logging

from plugins.base import Task, TaskPriority


logger = logging.getLogger(__name__)


@dataclass
class DecompositionStrategy:
    """Strategy for task decomposition"""
    max_depth: int = 3
    max_children: int = 5
    use_llm: bool = True  # Use Gemini for intelligent splitting
    parallel_execution: bool = True


class TaskDecomposer:  # pylint: disable=too-few-public-methods
    """
    Decomposes complex tasks into hierarchical subtasks.

    ROMA Pattern Implementation:
    1. Analyze task complexity
    2. If complex: split into subtasks
    3. Maintain dependency graph
    4. Recursively decompose until atomic

    Example:
        Mission: "Optimize infrastructure performance"
        ├── Task 1: "Analyze current metrics"
        ├── Task 2: "Identify bottlenecks" (depends on Task 1)
        ├── Task 3: "Generate optimization plan" (depends on Task 2)
        └── Task 4: "Execute optimizations" (depends on Task 3)
    """

    def __init__(
        self,
        strategy: Optional[DecompositionStrategy] = None,
        gemini_client: Optional[Any] = None
    ):
        """
        Initialize decomposer.

        Args:
            strategy: Decomposition strategy configuration
            gemini_client: Optional Gemini client for LLM-based decomposition
        """
        self.strategy = strategy or DecompositionStrategy()
        self.gemini = gemini_client
        self._task_counter = 0

    async def decompose(
        self,
        task: Task,
        depth: int = 0
    ) -> List[Task]:
        """
        Decompose a task into subtasks.

        Args:
            task: Task to decompose
            depth: Current recursion depth

        Returns:
            List of atomic subtasks (flattened tree)
        """
        # Base case: already atomic or max depth
        if task.is_atomic or depth >= self.strategy.max_depth:
            return [task]

        # Check if task needs decomposition
        if not self._needs_decomposition(task):
            task.is_atomic = True
            return [task]

        logger.info(
            "Decomposing task %s at depth %d",
            task.task_id, depth
        )

        # Generate subtasks
        if self.strategy.use_llm and self.gemini:
            subtasks = await self._llm_decompose(task)
        else:
            subtasks = self._rule_based_decompose(task)

        # Recursively decompose subtasks
        all_atomic_tasks = []
        for subtask in subtasks:
            atomic_tasks = await self.decompose(subtask, depth + 1)
            all_atomic_tasks.extend(atomic_tasks)

        return all_atomic_tasks

    def _needs_decomposition(self, task: Task) -> bool:
        """
        Determine if task needs decomposition.

        Simple heuristic: check description complexity
        """
        # Check for multi-step indicators
        indicators = ["and", "then", "after", "before", "while"]
        description_lower = task.description.lower()

        has_multiple_steps = any(
            indicator in description_lower for indicator in indicators
        )

        # Check priority (critical tasks get more decomposition)
        is_critical = task.priority == TaskPriority.CRITICAL

        return has_multiple_steps or is_critical

    async def _llm_decompose(self, task: Task) -> List[Task]:
        """
        Use Gemini 3 Pro to intelligently decompose task.

        Args:
            task: Task to decompose

        Returns:
            List of subtasks
        """
        prompt = f"""
        <task_decomposition>
        Decompose the following task into 2-5 concrete subtasks.
        Maintain logical dependencies.

        Original Task:
        Type: {task.type}
        Description: {task.description}
        Context: {task.context}

        Return JSON array of subtasks:
        [
            {{
                "type": "task_type",
                "description": "specific action",
                "priority": "low|medium|high|critical",
                "dependencies": []  // indices of tasks this depends on
            }}
        ]
        </task_decomposition>
        """

        try:
            # Call Gemini (placeholder - adapt to your client)
            if not self.gemini:
                raise ValueError("Gemini client not initialized")
            response = await self.gemini.generate_content(prompt)
            subtasks_data = self._parse_llm_response(response)

            # Convert to Task objects
            subtasks = []
            for i, data in enumerate(subtasks_data):
                subtask = Task(
                    task_id=self._generate_task_id(task.task_id, i),
                    type=data.get("type", task.type),
                    description=data["description"],
                    context=task.context.copy(),
                    priority=self._parse_priority(data.get("priority", "medium")),
                    dependencies=[
                        self._generate_task_id(task.task_id, dep_idx)
                        for dep_idx in data.get("dependencies", [])
                    ]
                )
                subtasks.append(subtask)

            return subtasks

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("LLM decomposition failed: %s, falling back to rules", e)
            return self._rule_based_decompose(task)

    def _rule_based_decompose(self, task: Task) -> List[Task]:
        """
        Simple rule-based decomposition (fallback).

        Args:
            task: Task to decompose

        Returns:
            List of subtasks
        """
        # Simple heuristic: split by task type
        if task.type == "infrastructure":
            return self._decompose_infrastructure_task(task)
        if task.type == "intelligence":
            return self._decompose_intelligence_task(task)

        # Generic split
        return [
            Task(
                task_id=self._generate_task_id(task.task_id, 0),
                type=task.type,
                description=f"Analyze: {task.description}",
                context=task.context,
                priority=task.priority
            ),
            Task(
                task_id=self._generate_task_id(task.task_id, 1),
                type=task.type,
                description=f"Execute: {task.description}",
                context=task.context,
                priority=task.priority,
                dependencies=[self._generate_task_id(task.task_id, 0)]
            )
        ]

    def _decompose_infrastructure_task(self, task: Task) -> List[Task]:
        """Decompose infrastructure-specific task"""
        base_id = task.task_id

        return [
            Task(
                task_id=f"{base_id}.1",
                type="monitoring",
                description="Monitor current system state",
                context=task.context,
                priority=task.priority
            ),
            Task(
                task_id=f"{base_id}.2",
                type="analysis",
                description="Analyze metrics and identify issues",
                context=task.context,
                priority=task.priority,
                dependencies=[f"{base_id}.1"]
            ),
            Task(
                task_id=f"{base_id}.3",
                type="planning",
                description="Generate action plan",
                context=task.context,
                priority=task.priority,
                dependencies=[f"{base_id}.2"]
            ),
            Task(
                task_id=f"{base_id}.4",
                type="execution",
                description="Execute infrastructure changes",
                context=task.context,
                priority=task.priority,
                dependencies=[f"{base_id}.3"],
                is_atomic=True
            )
        ]

    def _decompose_intelligence_task(self, task: Task) -> List[Task]:
        """Decompose intelligence-specific task"""
        base_id = task.task_id

        return [
            Task(
                task_id=f"{base_id}.1",
                type="collection",
                description="Collect intelligence data",
                context=task.context,
                priority=task.priority
            ),
            Task(
                task_id=f"{base_id}.2",
                type="analysis",
                description="Analyze collected data",
                context=task.context,
                priority=task.priority,
                dependencies=[f"{base_id}.1"],
                is_atomic=True
            )
        ]

    def _generate_task_id(self, parent_id: str, index: int) -> str:
        """Generate child task ID"""
        return f"{parent_id}.{index + 1}"

    def _parse_priority(self, priority_str: str) -> TaskPriority:
        """Parse priority string to enum"""
        mapping = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL
        }
        return mapping.get(priority_str.lower(), TaskPriority.MEDIUM)

    def _parse_llm_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parse LLM response to subtask data"""
        # Placeholder - adapt to your Gemini client
        # Should extract JSON array from response

        try:
            if isinstance(response, dict):
                text = response.get("text", "")
            elif hasattr(response, "text"):
                text = response.text
            else:
                text = str(response)

            # Clean markdown if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()

            return cast(List[Dict[str, Any]], json.loads(text))
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to parse LLM response: %s", e)
            return []
