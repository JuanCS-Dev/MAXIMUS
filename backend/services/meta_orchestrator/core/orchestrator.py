"""
Meta-Orchestrator: Core Orchestrator
=====================================

Main orchestration engine implementing ROMA hierarchical pattern.
Coordinates specialist agents to solve complex missions.

Pattern: Coordinator + Strategy
Inspiration: Kubernetes Controller, Google's agent orchestration
"""

import asyncio
import time
from typing import List, Dict
import logging


from .agent_registry import AgentRegistry
from .task_decomposer import TaskDecomposer
from plugins.base import Task, TaskStatus, TaskResult


logger = logging.getLogger(__name__)





class Orchestrator:  # pylint: disable=too-few-public-methods
    """
    Meta-orchestrator for Maximus 2.0.

    Coordinates specialist agents (HCL, OSINT, Memory, etc.) to execute
    complex missions through hierarchical task decomposition and parallel execution.

    Architecture:
        Mission → Decompose → Route → Execute → Synthesize

    Features:
        - ROMA-style recursive decomposition
        - Intelligent agent selection
        - Parallel execution with dependency resolution
        - Result synthesis
        - Error recovery
    """

    def __init__(
        self,
        registry: AgentRegistry,
        decomposer: TaskDecomposer,
        max_depth: int = 3,
        timeout_seconds: int = 300
    ):
        """
        Initialize orchestrator.

        Args:
            registry: Agent registry for plugin management
            decomposer: Task decomposer for hierarchical splitting
            max_depth: Maximum recursion depth
            timeout_seconds: Global timeout for mission execution
        """
        self.registry = registry
        self.decomposer = decomposer
        self.max_depth = max_depth
        self.timeout_seconds = timeout_seconds
        logger.info("Orchestrator initialized")

    async def execute_mission(
        self,
        mission: Task,
        depth: int = 0
    ) -> TaskResult:
        """
        Execute a mission by orchestrating specialist agents.

        Algorithm:
        1. Check if mission is atomic
        2. If atomic: route to best agent and execute
        3. If complex: decompose into subtasks
        4. Execute subtasks (respecting dependencies)
        5. Synthesize results

        Args:
            mission: High-level mission to execute
            depth: Current recursion depth (for tracking)

        Returns:
            Mission execution result
        """
        start_time = time.time()

        logger.info(
            "Executing mission: %s (type=%s, priority=%s, depth=%d)",
            mission.task_id, mission.type, mission.priority.name, depth
        )

        try:
            # Base case: atomic task or max depth reached
            if mission.is_atomic or depth >= self.max_depth:
                result = await self._execute_atomic_task(mission)

            else:
                # Recursive case: decompose and execute
                result = await self._execute_complex_task(mission, depth)

            # Update timing
            execution_time_ms = int((time.time() - start_time) * 1000)
            result.execution_time_ms = execution_time_ms

            logger.info(
                "Mission %s completed: status=%s, time=%dms",
                mission.task_id, result.status.value, execution_time_ms
            )

            return result

        except asyncio.TimeoutError:
            logger.error("Mission %s timed out", mission.task_id)
            return TaskResult(
                task_id=mission.task_id,
                status=TaskStatus.FAILED,
                output={},
                reasoning="Mission timed out",
                errors=["Execution exceeded timeout limit"]
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Mission %s failed: %s", mission.task_id, e, exc_info=True)
            return TaskResult(
                task_id=mission.task_id,
                status=TaskStatus.FAILED,
                output={},
                reasoning=f"Unexpected error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_atomic_task(self, task: Task) -> TaskResult:
        """
        Execute a single atomic task via the best agent.

        Args:
            task: Atomic task to execute

        Returns:
            Task execution result
        """
        # Select best agent
        agent = await self.registry.select_agent(task)

        if not agent:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                output={},
                reasoning="No suitable agent found for this task",
                errors=["Agent selection failed"]
            )

        logger.info("Task %s assigned to agent: %s", task.task_id, agent.name)

        # Execute via agent
        start_time = time.time()

        try:
            result = await asyncio.wait_for(
                agent.execute(task),
                timeout=self.timeout_seconds
            )

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Update agent stats
            success = result.status == TaskStatus.COMPLETED
            await self.registry.update_stats(
                agent.name,
                success,
                execution_time_ms
            )

            return result

        except asyncio.TimeoutError:
            logger.error("Agent %s timed out on task %s", agent.name, task.task_id)
            await self.registry.update_stats(agent.name, False, self.timeout_seconds * 1000)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                output={},
                reasoning=f"Agent {agent.name} timed out",
                errors=["Execution timeout"]
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Agent %s failed on task %s: %s", agent.name, task.task_id, e)
            await self.registry.update_stats(agent.name, False, 0)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                output={},
                reasoning=f"Agent execution failed: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_complex_task(
        self,
        task: Task,
        depth: int
    ) -> TaskResult:
        """
        Execute complex task via decomposition.

        Args:
            task: Complex task to decompose and execute
            depth: Current recursion depth

        Returns:
            Synthesized result
        """
        # Decompose into subtasks
        subtasks = await self.decomposer.decompose(task)

        logger.info(
            "Task %s decomposed into %d subtasks",
            task.task_id, len(subtasks)
        )

        # Execute subtasks with dependency resolution
        results = await self._execute_with_dependencies(subtasks, depth + 1)

        # Synthesize results
        synthesized = self._synthesize_results(task, results)

        return synthesized

    async def _execute_with_dependencies(
        self,
        tasks: List[Task],
        depth: int
    ) -> Dict[str, TaskResult]:
        """
        Execute tasks respecting dependency order.

        Args:
            tasks: List of tasks to execute
            depth: Current recursion depth

        Returns:
            Dictionary mapping task IDs to results
        """
        results: Dict[str, TaskResult] = {}
        pending_tasks = {task.task_id: task for task in tasks}

        while pending_tasks:
            # Find tasks with all dependencies satisfied
            ready_tasks = []
            for _, task in pending_tasks.items():
                deps_satisfied = all(
                    dep_id in results for dep_id in task.dependencies
                )
                if deps_satisfied:
                    ready_tasks.append(task)

            if not ready_tasks:
                # Circular dependency or deadlock
                logger.error("No ready tasks - possible circular dependency")
                break

            # Execute ready tasks in parallel
            task_futures = [
                self.execute_mission(task, depth)
                for task in ready_tasks
            ]

            task_results = await asyncio.gather(*task_futures)

            # Store results and remove from pending
            for task, result in zip(ready_tasks, task_results):
                results[task.task_id] = result
                del pending_tasks[task.task_id]

        return results

    def _synthesize_results(
        self,
        original_task: Task,
        subtask_results: Dict[str, TaskResult]
    ) -> TaskResult:
        """
        Synthesize subtask results into final result.

        Args:
            original_task: Original complex task
            subtask_results: Results from all subtasks

        Returns:
            Synthesized task result
        """
        # Check if all subtasks succeeded
        all_succeeded = all(
            result.status == TaskStatus.COMPLETED
            for result in subtask_results.values()
        )

        # Aggregate outputs
        aggregated_output = {
            "subtasks": {
                task_id: result.output
                for task_id, result in subtask_results.items()
            }
        }

        # Combine reasoning
        combined_reasoning = " → ".join([
            result.reasoning
            for result in subtask_results.values()
            if result.reasoning
        ])

        # Collect all errors
        all_errors = []
        for result in subtask_results.values():
            all_errors.extend(result.errors)

        # Calculate average confidence
        confidences = [r.confidence for r in subtask_results.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return TaskResult(
            task_id=original_task.task_id,
            status=TaskStatus.COMPLETED if all_succeeded else TaskStatus.FAILED,
            output=aggregated_output,
            reasoning=combined_reasoning,
            confidence=avg_confidence,
            errors=all_errors
        )
