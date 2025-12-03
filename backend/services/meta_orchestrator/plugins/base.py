"""
Meta-Orchestrator: Plugin Base Interface
=========================================

Abstract base class for all agent plugins in Maximus 2.0.
Implements the Strategy Pattern for flexible agent composition.

Based on research from:
- ROMA (Recursive Open Meta-Agent)
- Google/Anthropic plugin systems
- Nov 2025 agentic patterns
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """
    Represents a task that can be executed by an agent.

    Attributes:
        task_id: Unique identifier
        type: Task type (e.g., "infrastructure", "intelligence", "security")
        description: Human-readable description
        context: Relevant context data
        priority: Task priority level
        is_atomic: Whether task can be decomposed further
        dependencies: IDs of tasks that must complete first
    """
    task_id: str
    type: str
    description: str
    context: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    is_atomic: bool = False
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TaskResult:  # pylint: disable=too-many-instance-attributes
    """
    Result of task execution.

    Attributes:
        task_id: ID of executed task
        status: Execution status
        output: Result data
        reasoning: Agent's explanation
        thought_trace: Meta-cognitive reasoning steps (if available)
        confidence: Confidence score (0.0 to 1.0)
        execution_time_ms: Time taken to execute
        errors: List of errors encountered (if any)
    """
    task_id: str
    status: TaskStatus
    output: Dict[str, Any]
    reasoning: str = ""
    thought_trace: str = ""
    confidence: float = 1.0
    execution_time_ms: int = 0
    errors: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


class AgentPlugin(ABC):
    """
    Abstract base class for all Maximus 2.0 agent plugins.

    All specialist agents (HCL, OSINT, Memory, etc.) must implement this interface.
    This enables the Meta-Orchestrator to treat all agents uniformly while
    allowing each to maintain its specialized logic.

    Design Pattern: Strategy Pattern
    Inspiration: Google's Gemini agent plugins, Anthropic's Claude skills
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique agent identifier.

        Returns:
            Lowercase identifier (e.g., "hcl_planner", "osint_analyzer")
        """


    @property
    @abstractmethod
    def version(self) -> str:
        """
        Agent version following semver.

        Returns:
            Version string (e.g., "2.0.0")
        """


    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        List of task types this agent can handle.

        Returns:
            List of capability names (e.g., ["infrastructure_planning", "resource_scaling"])
        """


    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of agent's purpose.

        Returns:
            Description string
        """


    @abstractmethod
    async def can_handle(self, task: Task) -> bool:
        """
        Determine if this agent can handle a given task.

        Args:
            task: Task to evaluate

        Returns:
            True if agent can handle this task type
        """


    @abstractmethod
    async def estimate_effort(self, task: Task) -> float:
        """
        Estimate computational effort required for task.

        Used by orchestrator for load balancing and scheduling.

        Args:
            task: Task to estimate

        Returns:
            Effort score (0.0 = trivial, 1.0 = maximum complexity)
        """


    @abstractmethod
    async def execute(self, task: Task) -> TaskResult:
        """
        Execute a task and return result.

        This is the core method where the agent's specialized logic runs.

        Args:
            task: Task to execute

        Returns:
            Task execution result

        Raises:
            Exception: If execution fails critically
        """


    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check agent's operational health.

        Returns:
            Health status dictionary with keys:
                - healthy: bool
                - status: str (e.g., "operational", "degraded", "down")
                - details: Dict[str, Any] (optional details)
                - last_error: str (if applicable)
        """


    async def shutdown(self) -> None:
        """
        Graceful shutdown hook.

        Override this if agent needs cleanup (e.g., close connections).
        Default implementation does nothing.
        """



class AgentPluginMetadata:  # pylint: disable=too-many-instance-attributes
    """
    Metadata for agent plugin registration.

    Used by AgentRegistry to track and manage plugins.
    """

    def __init__(
        self,
        agent: AgentPlugin,
        enabled: bool = True,
        priority: int = 100,
        tags: Optional[List[str]] = None
    ):
        """
        Initialize plugin metadata.

        Args:
            agent: The agent plugin instance
            enabled: Whether agent is currently enabled
            priority: Priority for task assignment (higher = higher priority)
            tags: Optional tags for categorization
        """
        self.agent = agent
        self.enabled = enabled
        self.priority = priority
        self.tags = tags or []
        self.registration_timestamp: Optional[float] = None
        self.total_tasks_executed: int = 0
        self.total_tasks_failed: int = 0
        self.average_execution_time_ms: float = 0.0

    def update_stats(
        self,
        success: bool,
        execution_time_ms: int
    ) -> None:
        """
        Update execution statistics.

        Args:
            success: Whether task succeeded
            execution_time_ms: Time taken to execute
        """
        if success:
            self.total_tasks_executed += 1
        else:
            self.total_tasks_failed += 1

        # Update moving average
        total = self.total_tasks_executed + self.total_tasks_failed
        self.average_execution_time_ms = (
            (self.average_execution_time_ms * (total - 1) + execution_time_ms) / total
        )

    @property
    def success_rate(self) -> float:
        """
        Calculate success rate.

        Returns:
            Success rate (0.0 to 1.0)
        """
        total = self.total_tasks_executed + self.total_tasks_failed
        if total == 0:
            return 1.0
        return self.total_tasks_executed / total
