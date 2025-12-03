"""
World Model - Data Models
=========================

Pydantic models and enums for the SimuRA World Model.

Contains:
- SimulationOutcome: Possible simulation outcomes
- ActionSimulation: Simulated action with prediction
- WorldModelConfig: Configuration for world model
- DynaThinkState: State for Dyna-Think reasoning loop
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SimulationOutcome(str, Enum):
    """Possible outcomes from simulation."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class ActionSimulation(BaseModel):
    """
    Simulated action with predicted outcome.

    Attributes:
        action: Action to simulate
        predicted_state: Predicted next state
        success_probability: Probability of success (0-1)
        outcome: Expected outcome
        reasoning: Why this outcome is predicted
        timestamp: When simulation was performed
    """

    action: Dict[str, Any] = Field(..., description="Action being simulated")
    predicted_state: Dict[str, Any] = Field(..., description="Predicted next state")
    success_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Success probability"
    )
    outcome: SimulationOutcome = Field(..., description="Expected outcome")
    reasoning: str = Field(..., description="Reasoning for prediction")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Metrics
    confidence: float = Field(
        0.5, ge=0.0, le=1.0, description="Confidence in prediction"
    )
    risk_score: float = Field(0.5, ge=0.0, le=1.0, description="Risk of failure")
    side_effects: List[str] = Field(
        default_factory=list, description="Predicted side effects"
    )

    # Dyna-Think specific
    simulation_depth: int = Field(1, description="How many steps ahead this simulates")
    alternative_outcomes: List[Dict[str, Any]] = Field(
        default_factory=list, description="Alternative possible outcomes"
    )


class WorldModelConfig(BaseModel):
    """
    Configuration for world model.

    Attributes:
        num_simulations: Number of alternative futures to simulate
        simulation_depth: How many steps ahead to simulate
        min_success_threshold: Minimum success probability to consider action
        use_parallel_simulations: Run simulations in parallel
        use_gemini: Whether to use Gemini for predictions
    """

    # Import here to avoid circular dependency
    gemini_config: Optional[Any] = Field(None, description="Gemini configuration")

    num_simulations: int = Field(5, ge=1, le=20, description="Number of simulations")
    simulation_depth: int = Field(3, ge=1, le=10, description="Steps ahead")
    min_success_threshold: float = Field(
        0.3, ge=0.0, le=1.0, description="Min success prob"
    )
    use_parallel_simulations: bool = Field(True, description="Parallel execution")
    use_gemini: bool = Field(True, description="Use Gemini for predictions")


class DynaThinkState(BaseModel):
    """State for Dyna-Think reasoning loop."""

    current_state: Dict[str, Any] = Field(default_factory=dict)
    action_history: List[Dict[str, Any]] = Field(default_factory=list)
    prediction_accuracy: float = Field(
        0.5, description="Rolling accuracy of predictions"
    )
    learning_rate: float = Field(0.1, description="How fast to update accuracy")
