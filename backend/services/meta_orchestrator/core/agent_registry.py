"""
Meta-Orchestrator: Agent Registry
===================================

Plugin registry system for managing specialist agents.
Implements dynamic agent discovery, routing, and load balancing.

Pattern: Registry Pattern + Factory Pattern
Inspiration: Google's agent management, Kubernetes controller pattern
"""

import asyncio
from typing import Dict, List, Optional, Set, Any, cast
from datetime import datetime
import logging

from plugins.base import (
    AgentPlugin,
    AgentPluginMetadata,
    Task
)


logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Central registry for all agent plugins in Maximus 2.0.

    Responsibilities:
    - Agent registration and discovery
    - Task routing (which agent handles which task)
    - Load balancing
    - Health monitoring
    - Performance tracking

    Thread-safe for concurrent agent operations.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._agents: Dict[str, AgentPluginMetadata] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
        logger.info("AgentRegistry initialized")

    async def register(
        self,
        agent: AgentPlugin,
        enabled: bool = True,
        priority: int = 100,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Register a new agent plugin.

        Args:
            agent: Agent plugin to register
            enabled: Whether agent is enabled
            priority: Agent priority (higher = more preferred)
            tags: Optional tags for categorization

        Raises:
            ValueError: If agent with same name already registered
        """
        async with self._lock:
            agent_name = agent.name

            if agent_name in self._agents:
                raise ValueError(
                    f"Agent '{agent_name}' is already registered. "
                    "Unregister it first or use update()."
                )

            metadata = AgentPluginMetadata(
                agent=agent,
                enabled=enabled,
                priority=priority,
                tags=tags
            )
            metadata.registration_timestamp = datetime.now().timestamp()

            self._agents[agent_name] = metadata

            logger.info(
                "Registered agent: %s (version=%s, enabled=%s, capabilities=%s)",
                agent_name, agent.version, enabled, agent.capabilities
            )

    async def unregister(self, agent_name: str) -> None:
        """
        Unregister an agent plugin.

        Args:
            agent_name: Name of agent to unregister

        Raises:
            KeyError: If agent not found
        """
        async with self._lock:
            if agent_name not in self._agents:
                raise KeyError(f"Agent '{agent_name}' not found in registry")

            metadata = self._agents[agent_name]

            # Graceful shutdown
            try:
                await metadata.agent.shutdown()
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error during shutdown of %s: %s", agent_name, e)

            del self._agents[agent_name]
            logger.info("Unregistered agent: %s", agent_name)

    async def select_agent(self, task: Task) -> Optional[AgentPlugin]:
        """
        Select the best agent to handle a given task.

        Algorithm:
        1. Filter agents that can handle this task type
        2. Filter enabled agents
        3. Check health status
        4. Pick agent with highest (priority / current_load)

        Args:
            task: Task to route

        Returns:
            Best agent to handle task, or None if no suitable agent found
        """
        async with self._lock:
            candidate_agents: List[tuple[float, AgentPluginMetadata]] = []

            for metadata in self._agents.values():
                # Skip disabled agents
                if not metadata.enabled:
                    continue

                agent = metadata.agent

                # Check if agent can handle this task
                try:
                    if not await agent.can_handle(task):
                        continue
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "Agent %s failed can_handle check: %s",
                        agent.name, e
                    )
                    continue

                # Check health
                try:
                    health = await agent.health_check()
                    if not health.get("healthy", False):
                        logger.warning(
                            "Agent %s is unhealthy, skipping",
                            agent.name
                        )
                        continue
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.error("Health check failed for %s: %s", agent.name, e)
                    continue

                # Calculate score (priority / average_exec_time)
                # Higher priority and faster execution = higher score
                avg_time = metadata.average_execution_time_ms or 1.0
                score = metadata.priority / avg_time

                candidate_agents.append((score, metadata))

            if not candidate_agents:
                logger.warning(
                    "No suitable agent found for task: %s (type=%s)",
                    task.task_id, task.type
                )
                return None

            # Sort by score (descending)
            candidate_agents.sort(key=lambda x: x[0], reverse=True)

            # Return best agent
            best_metadata = candidate_agents[0][1]
            logger.info(
                "Selected agent %s for task %s (score=%.2f)",
                best_metadata.agent.name, task.task_id, candidate_agents[0][0]
            )

            return best_metadata.agent

    async def get_agent(self, agent_name: str) -> Optional[AgentPlugin]:
        """
        Get agent by name.

        Args:
            agent_name: Name of agent

        Returns:
            Agent plugin or None if not found
        """
        async with self._lock:
            metadata = self._agents.get(agent_name)
            return metadata.agent if metadata else None

    async def list_agents(
        self,
        enabled_only: bool = False,
        tags: Optional[Set[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all registered agents.

        Args:
            enabled_only: If True, only return enabled agents
            tags: If provided, only return agents with these tags

        Returns:
            List of agent info dictionaries
        """
        async with self._lock:
            result = []

            for agent_name, metadata in self._agents.items():
                if enabled_only and not metadata.enabled:
                    continue

                if tags and not set(metadata.tags).intersection(tags):
                    continue

                result.append({
                    "name": agent_name,
                    "version": metadata.agent.version,
                    "enabled": metadata.enabled,
                    "priority": metadata.priority,
                    "capabilities": metadata.agent.capabilities,
                    "description": metadata.agent.description,
                    "tags": metadata.tags,
                    "stats": {
                        "total_executed": metadata.total_tasks_executed,
                        "total_failed": metadata.total_tasks_failed,
                        "success_rate": metadata.success_rate,
                        "avg_exec_time_ms": metadata.average_execution_time_ms
                    }
                })

            return result

    async def update_stats(
        self,
        agent_name: str,
        success: bool,
        execution_time_ms: int
    ) -> None:
        """
        Update agent execution statistics.

        Called by orchestrator after task execution.

        Args:
            agent_name: Name of agent that executed task
            success: Whether execution succeeded
            execution_time_ms: Time taken
        """
        async with self._lock:
            metadata = self._agents.get(agent_name)
            if metadata:
                metadata.update_stats(success, execution_time_ms)

    async def enable_agent(self, agent_name: str) -> None:
        """Enable an agent."""
        async with self._lock:
            if agent_name in self._agents:
                self._agents[agent_name].enabled = True
                logger.info("Enabled agent: %s", agent_name)

    async def disable_agent(self, agent_name: str) -> None:
        """Disable an agent."""
        async with self._lock:
            if agent_name in self._agents:
                self._agents[agent_name].enabled = False
                logger.info("Disabled agent: %s", agent_name)

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Run health check on all agents.

        Returns:
            Dictionary mapping agent names to health status
        """
        results = {}

        async with self._lock:
            agents_copy = list(self._agents.items())

        # Run health checks in parallel
        tasks = []
        for agent_name, metadata in agents_copy:
            tasks.append(self._check_agent_health(agent_name, metadata))

        health_results = await asyncio.gather(*tasks, return_exceptions=True)

        for (agent_name, _), health in zip(agents_copy, health_results):
            if isinstance(health, Exception):
                results[agent_name] = {
                    "healthy": False,
                    "error": str(health)
                }
            else:
                results[agent_name] = cast(Dict[str, Any], health)

        return results

    async def _check_agent_health(
        self,
        _: str,
        metadata: AgentPluginMetadata
    ) -> Dict[str, Any]:
        """Helper to check single agent health."""
        try:
            health = await metadata.agent.health_check()
            health["enabled"] = metadata.enabled
            return health
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {
                "healthy": False,
                "status": "error",
                "error": str(e)
            }
