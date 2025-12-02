"""
SimuRA World Model - Dyna-Think Architecture
=============================================

LLM-based world model for action simulation and outcome prediction.
Implements Dyna-Think style reasoning with Gemini integration.

Based on:
- Dyna-Think (2025): Reasoning + Acting + World Model simulation
- SimuRA: Simulative Reasoning Architecture
- Berkeley LLM Agents Hackathon (2nd place, Fundamental Track)

Architecture:
1. Perception: Observe current state
2. World Model: Predict next states (LLM-based via Gemini)
3. Reasoning: Evaluate simulations, select best action
4. Learning: Update model from actual outcomes
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .gemini_client import GeminiClient, GeminiConfig, SimulationPrediction

logger = logging.getLogger(__name__)


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
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence in prediction")
    risk_score: float = Field(0.5, ge=0.0, le=1.0, description="Risk of failure")
    side_effects: List[str] = Field(default_factory=list, description="Predicted side effects")

    # Dyna-Think specific
    simulation_depth: int = Field(1, description="How many steps ahead this simulates")
    alternative_outcomes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative possible outcomes"
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

    num_simulations: int = Field(5, ge=1, le=20, description="Number of simulations")
    simulation_depth: int = Field(3, ge=1, le=10, description="Steps ahead")
    min_success_threshold: float = Field(0.3, ge=0.0, le=1.0, description="Min success prob")
    use_parallel_simulations: bool = Field(True, description="Parallel execution")
    use_gemini: bool = Field(True, description="Use Gemini for predictions")
    gemini_config: Optional[GeminiConfig] = Field(None, description="Gemini configuration")


class DynaThinkState(BaseModel):
    """State for Dyna-Think reasoning loop."""

    current_state: Dict[str, Any] = Field(default_factory=dict)
    action_history: List[Dict[str, Any]] = Field(default_factory=list)
    prediction_accuracy: float = Field(0.5, description="Rolling accuracy of predictions")
    learning_rate: float = Field(0.1, description="How fast to update accuracy")


class SimuRAWorldModel:
    """
    SimuRA-inspired world model with Dyna-Think integration.

    Features:
    - LLM-based state prediction (Gemini)
    - Multi-hypothesis simulation
    - Outcome evaluation and ranking
    - Success probability estimation
    - Dyna-Think reasoning loop
    - Learning from actual outcomes

    Performance Target: 60%+ success rate (vs. 32% baseline)

    Example:
        >>> config = WorldModelConfig(
        ...     use_gemini=True,
        ...     gemini_config=GeminiConfig(api_key="...")
        ... )
        >>> world_model = SimuRAWorldModel(config)
        >>> simulations = await world_model.simulate_action(
        ...     current_state={"service": "down", "users": 100},
        ...     candidate_actions=[
        ...         {"type": "restart", "params": {}},
        ...         {"type": "scale_up", "params": {"replicas": 3}}
        ...     ]
        ... )
        >>> best = world_model.select_best_action(simulations)
    """

    def __init__(
        self,
        config: Optional[WorldModelConfig] = None,
        gemini_client: Optional[GeminiClient] = None
    ):
        """
        Initialize world model.

        Args:
            config: World model configuration
            gemini_client: Pre-configured Gemini client (optional)
        """
        self.config = config or WorldModelConfig()

        # Initialize Gemini client
        if gemini_client:
            self._gemini = gemini_client
        elif self.config.use_gemini and self.config.gemini_config:
            self._gemini = GeminiClient(self.config.gemini_config)
        else:
            self._gemini = None

        # Dyna-Think state
        self._dyna_state = DynaThinkState()

        # History tracking
        self.simulation_history: List[ActionSimulation] = []
        self._outcome_history: List[Tuple[ActionSimulation, str]] = []

        logger.info(
            "world_model_initialized",
            extra={
                "num_simulations": self.config.num_simulations,
                "depth": self.config.simulation_depth,
                "gemini_enabled": self._gemini is not None
            }
        )

    async def simulate_action(
        self,
        current_state: Dict[str, Any],
        candidate_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ActionSimulation]:
        """
        Simulate multiple candidate actions and predict outcomes.

        Implements Dyna-Think Phase 1: World Model Simulation

        Args:
            current_state: Current system state
            candidate_actions: List of actions to simulate
            context: Additional context (history, constraints)

        Returns:
            List of simulations with predictions
        """
        # Update Dyna-Think state
        self._dyna_state.current_state = current_state

        # Enrich context with history
        enriched_context = self._build_context(context)

        if self.config.use_parallel_simulations:
            simulations = await self._parallel_simulate(
                current_state, candidate_actions, enriched_context
            )
        else:
            simulations = []
            for action in candidate_actions:
                sim = await self._simulate_single_action(
                    current_state, action, enriched_context
                )
                simulations.append(sim)

        # Store in history
        self.simulation_history.extend(simulations)

        logger.info(
            "simulations_complete",
            extra={
                "num_actions": len(candidate_actions),
                "num_simulations": len(simulations),
                "avg_success_prob": sum(s.success_probability for s in simulations) / len(simulations)
                if simulations else 0
            }
        )

        return simulations

    async def _parallel_simulate(
        self,
        current_state: Dict[str, Any],
        actions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[ActionSimulation]:
        """Run simulations in parallel."""
        tasks = [
            self._simulate_single_action(current_state, action, context)
            for action in actions
        ]
        return await asyncio.gather(*tasks)

    async def _simulate_single_action(
        self,
        current_state: Dict[str, Any],
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ActionSimulation:
        """
        Simulate single action using Gemini or heuristics.

        Args:
            current_state: Current state
            action: Action to simulate
            context: Enriched context

        Returns:
            Simulation with predicted outcome
        """
        if self._gemini:
            prediction = await self._llm_predict_outcome(
                current_state, action, context
            )
        else:
            prediction = self._heuristic_predict_outcome(current_state, action)

        # Apply Dyna-Think confidence adjustment
        adjusted_confidence = self._adjust_confidence(prediction["confidence"])
        prediction["confidence"] = adjusted_confidence

        return ActionSimulation(**prediction)

    async def _llm_predict_outcome(
        self,
        current_state: Dict[str, Any],
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use Gemini to predict action outcome.

        Args:
            current_state: Current state
            action: Action to simulate
            context: Additional context

        Returns:
            Prediction dict
        """
        try:
            prediction: SimulationPrediction = await self._gemini.simulate_action(
                state=current_state,
                action=action,
                context=context
            )

            # Map SimulationPrediction to ActionSimulation fields
            outcome_map = {
                "success": SimulationOutcome.SUCCESS,
                "failure": SimulationOutcome.FAILURE,
                "partial": SimulationOutcome.PARTIAL,
                "unknown": SimulationOutcome.UNKNOWN
            }

            return {
                "action": action,
                "predicted_state": prediction.predicted_state,
                "success_probability": prediction.success_probability,
                "outcome": outcome_map.get(prediction.outcome, SimulationOutcome.UNKNOWN),
                "reasoning": prediction.reasoning,
                "confidence": prediction.confidence,
                "risk_score": prediction.risk_score,
                "side_effects": prediction.side_effects,
                "simulation_depth": 1
            }

        except Exception as e:
            logger.warning(
                "gemini_prediction_failed",
                extra={"error": str(e), "action": action.get("type")}
            )
            # Fallback to heuristics
            return self._heuristic_predict_outcome(current_state, action)

    def _heuristic_predict_outcome(
        self,
        current_state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Heuristic-based prediction (deterministic fallback).

        Args:
            current_state: Current state
            action: Action to simulate

        Returns:
            Prediction dict
        """
        action_type = action.get("type", "unknown")

        # Enhanced heuristics based on action type
        heuristics = {
            "restart": {
                "success_prob": 0.7,
                "outcome": SimulationOutcome.SUCCESS,
                "predicted_state": {**current_state, "status": "restarted"},
                "reasoning": "Restart typically resolves transient issues",
                "confidence": 0.6,
                "risk": 0.3,
                "side_effects": ["brief downtime", "connection reset"]
            },
            "scale_up": {
                "success_prob": 0.8,
                "outcome": SimulationOutcome.SUCCESS,
                "predicted_state": {
                    **current_state,
                    "replicas": action.get("params", {}).get("replicas", 2)
                },
                "reasoning": "Scaling up increases capacity, likely resolves load issues",
                "confidence": 0.7,
                "risk": 0.2,
                "side_effects": ["increased cost", "warm-up time"]
            },
            "scale_down": {
                "success_prob": 0.75,
                "outcome": SimulationOutcome.SUCCESS,
                "predicted_state": {
                    **current_state,
                    "replicas": max(1, action.get("params", {}).get("replicas", 1))
                },
                "reasoning": "Scaling down reduces resources, may impact performance",
                "confidence": 0.6,
                "risk": 0.4,
                "side_effects": ["reduced capacity", "potential load issues"]
            },
            "rollback": {
                "success_prob": 0.9,
                "outcome": SimulationOutcome.SUCCESS,
                "predicted_state": {**current_state, "version": "previous"},
                "reasoning": "Rollback to known-good state is low risk",
                "confidence": 0.8,
                "risk": 0.1,
                "side_effects": ["feature regression"]
            },
            "deploy": {
                "success_prob": 0.6,
                "outcome": SimulationOutcome.PARTIAL,
                "predicted_state": {**current_state, "version": "new"},
                "reasoning": "Deployments carry moderate risk",
                "confidence": 0.5,
                "risk": 0.5,
                "side_effects": ["potential bugs", "performance changes"]
            },
            "migrate": {
                "success_prob": 0.5,
                "outcome": SimulationOutcome.PARTIAL,
                "predicted_state": {**current_state, "migrated": True},
                "reasoning": "Migrations are complex and risky",
                "confidence": 0.4,
                "risk": 0.7,
                "side_effects": ["data transfer time", "potential data loss"]
            }
        }

        defaults = heuristics.get(action_type, {
            "success_prob": 0.4,
            "outcome": SimulationOutcome.UNKNOWN,
            "predicted_state": current_state,
            "reasoning": "Unknown action type, cannot predict reliably",
            "confidence": 0.3,
            "risk": 0.7,
            "side_effects": []
        })

        return {
            "action": action,
            "predicted_state": defaults["predicted_state"],
            "success_probability": defaults["success_prob"],
            "outcome": defaults["outcome"],
            "reasoning": defaults["reasoning"],
            "confidence": defaults["confidence"],
            "risk_score": defaults["risk"],
            "side_effects": defaults["side_effects"],
            "simulation_depth": 1
        }

    def _build_context(
        self,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build enriched context for simulation."""
        enriched = context or {}

        # Add action history
        if self._dyna_state.action_history:
            enriched["recent_actions"] = self._dyna_state.action_history[-5:]

        # Add prediction accuracy
        enriched["model_accuracy"] = self._dyna_state.prediction_accuracy

        # Add recent outcomes
        if self._outcome_history:
            enriched["recent_outcomes"] = [
                {"predicted": sim.outcome.value, "actual": actual}
                for sim, actual in self._outcome_history[-3:]
            ]

        return enriched

    def _adjust_confidence(self, base_confidence: float) -> float:
        """
        Adjust confidence based on historical accuracy (Dyna-Think).

        Args:
            base_confidence: Raw confidence from prediction

        Returns:
            Adjusted confidence
        """
        # Blend base confidence with historical accuracy
        accuracy = self._dyna_state.prediction_accuracy
        adjusted = base_confidence * 0.7 + accuracy * 0.3
        return min(1.0, max(0.0, adjusted))

    def select_best_action(
        self,
        simulations: List[ActionSimulation],
        strategy: str = "balanced"
    ) -> Optional[ActionSimulation]:
        """
        Select best action from simulations.

        Args:
            simulations: List of action simulations
            strategy: Selection strategy
                - "max_success": Highest success probability
                - "min_risk": Lowest risk score
                - "balanced": Balance success and risk
                - "conservative": Prioritize low risk

        Returns:
            Best action simulation or None
        """
        if not simulations:
            return None

        # Filter by minimum threshold
        viable = [
            s for s in simulations
            if s.success_probability >= self.config.min_success_threshold
        ]

        if not viable:
            logger.warning(
                "no_viable_actions",
                extra={"threshold": self.config.min_success_threshold}
            )
            # Return best of non-viable if needed
            return max(simulations, key=lambda s: s.success_probability)

        # Select based on strategy
        if strategy == "max_success":
            best = max(viable, key=lambda s: s.success_probability)
        elif strategy == "min_risk":
            best = min(viable, key=lambda s: s.risk_score)
        elif strategy == "balanced":
            # Balance success and risk (weighted)
            best = max(
                viable,
                key=lambda s: s.success_probability * 0.6 - s.risk_score * 0.3 + s.confidence * 0.1
            )
        elif strategy == "conservative":
            # Prioritize low risk, then high success
            best = min(
                viable,
                key=lambda s: (s.risk_score, -s.success_probability)
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        logger.info(
            "best_action_selected",
            extra={
                "action": best.action.get("type"),
                "success_prob": best.success_probability,
                "risk": best.risk_score,
                "strategy": strategy
            }
        )

        return best

    def record_outcome(
        self,
        simulation: ActionSimulation,
        actual_outcome: str
    ) -> None:
        """
        Record actual outcome for learning (Dyna-Think Phase 3).

        Args:
            simulation: The original simulation
            actual_outcome: What actually happened ("success", "failure", etc.)
        """
        # Record in history
        self._outcome_history.append((simulation, actual_outcome))
        self._dyna_state.action_history.append(simulation.action)

        # Trim history
        if len(self._outcome_history) > 100:
            self._outcome_history = self._outcome_history[-100:]
        if len(self._dyna_state.action_history) > 50:
            self._dyna_state.action_history = self._dyna_state.action_history[-50:]

        # Update accuracy (exponential moving average)
        predicted_correct = simulation.outcome.value == actual_outcome
        lr = self._dyna_state.learning_rate

        new_accuracy = (
            self._dyna_state.prediction_accuracy * (1 - lr) +
            (1.0 if predicted_correct else 0.0) * lr
        )
        self._dyna_state.prediction_accuracy = new_accuracy

        logger.info(
            "outcome_recorded",
            extra={
                "predicted": simulation.outcome.value,
                "actual": actual_outcome,
                "correct": predicted_correct,
                "new_accuracy": new_accuracy
            }
        )

    async def simulate_sequence(
        self,
        initial_state: Dict[str, Any],
        action_sequence: List[Dict[str, Any]]
    ) -> List[ActionSimulation]:
        """
        Simulate a sequence of actions (multi-step lookahead).

        Implements Dyna-Think Phase 2: Multi-Step Planning

        Args:
            initial_state: Starting state
            action_sequence: Ordered list of actions

        Returns:
            List of simulations showing state evolution
        """
        if self._gemini and len(action_sequence) > 1:
            try:
                predictions = await self._gemini.simulate_sequence(
                    initial_state, action_sequence
                )
                return self._convert_predictions_to_simulations(
                    action_sequence, predictions
                )
            except Exception as e:
                logger.warning("sequence_simulation_failed", extra={"error": str(e)})

        # Fallback: simulate step by step
        simulations = []
        current = initial_state

        for i, action in enumerate(action_sequence):
            sim = await self._simulate_single_action(current, action, {})
            sim.simulation_depth = i + 1
            simulations.append(sim)
            current = sim.predicted_state

        return simulations

    def _convert_predictions_to_simulations(
        self,
        actions: List[Dict[str, Any]],
        predictions: List[SimulationPrediction]
    ) -> List[ActionSimulation]:
        """Convert SimulationPredictions to ActionSimulations."""
        simulations = []

        outcome_map = {
            "success": SimulationOutcome.SUCCESS,
            "failure": SimulationOutcome.FAILURE,
            "partial": SimulationOutcome.PARTIAL,
            "unknown": SimulationOutcome.UNKNOWN
        }

        for i, (action, pred) in enumerate(zip(actions, predictions)):
            sim = ActionSimulation(
                action=action,
                predicted_state=pred.predicted_state,
                success_probability=pred.success_probability,
                outcome=outcome_map.get(pred.outcome, SimulationOutcome.UNKNOWN),
                reasoning=pred.reasoning,
                confidence=pred.confidence,
                risk_score=pred.risk_score,
                side_effects=pred.side_effects,
                simulation_depth=i + 1
            )
            simulations.append(sim)

        return simulations

    def get_simulation_stats(self) -> Dict[str, Any]:
        """
        Get statistics from simulation history.

        Returns:
            Dictionary of statistics
        """
        if not self.simulation_history:
            return {"total_simulations": 0}

        total = len(self.simulation_history)
        avg_success = sum(s.success_probability for s in self.simulation_history) / total
        avg_confidence = sum(s.confidence for s in self.simulation_history) / total
        avg_risk = sum(s.risk_score for s in self.simulation_history) / total

        outcome_counts: Dict[str, int] = {}
        for s in self.simulation_history:
            outcome_counts[s.outcome.value] = outcome_counts.get(s.outcome.value, 0) + 1

        return {
            "total_simulations": total,
            "avg_success_probability": round(avg_success, 3),
            "avg_confidence": round(avg_confidence, 3),
            "avg_risk": round(avg_risk, 3),
            "outcome_distribution": outcome_counts,
            "dyna_think_accuracy": round(self._dyna_state.prediction_accuracy, 3),
            "gemini_enabled": self._gemini is not None
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check health of world model components."""
        result = {
            "healthy": True,
            "gemini_enabled": self._gemini is not None,
            "simulation_count": len(self.simulation_history),
            "dyna_accuracy": self._dyna_state.prediction_accuracy
        }

        if self._gemini:
            gemini_health = await self._gemini.health_check()
            result["gemini_health"] = gemini_health
            result["healthy"] = gemini_health.get("healthy", False)

        return result

    async def close(self) -> None:
        """Cleanup resources."""
        if self._gemini:
            await self._gemini.close()
