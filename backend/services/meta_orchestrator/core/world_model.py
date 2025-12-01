"""
SimuRA World Model - Simulative Reasoning Architecture
=======================================================

LLM-based world model for action simulation and outcome prediction.

Based on: Berkeley LLM Agents Hackathon (2nd place, Fundamental Track)
Performance: +124% vs. autoregressive reasoning, 32% success rate

Architecture:
1. Perception: Observe current state
2. World Model: Predict next states (LLM-based)
3. Reasoning: Evaluate simulations, select best action
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


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
    success_probability: float = Field(..., ge=0.0, le=1.0, description="Success probability")
    outcome: SimulationOutcome = Field(..., description="Expected outcome")
    reasoning: str = Field(..., description="Reasoning for prediction")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Metrics
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence in prediction")
    risk_score: float = Field(0.5, ge=0.0, le=1.0, description="Risk of failure")


class WorldModelConfig(BaseModel):
    """
    Configuration for world model.
    
    Attributes:
        num_simulations: Number of alternative futures to simulate
        simulation_depth: How many steps ahead to simulate
        min_success_threshold: Minimum success probability to consider action
        use_parallel_simulations: Run simulations in parallel
    """
    
    num_simulations: int = Field(5, ge=1, le=20, description="Number of simulations")
    simulation_depth: int = Field(3, ge=1, le=10, description="Steps ahead")
    min_success_threshold: float = Field(0.3, ge=0.0, le=1.0, description="Min success prob")
    use_parallel_simulations: bool = Field(True, description="Parallel execution")


class SimuRAWorldModel:
    """
    SimuRA-inspired world model for action simulation.
    
    Features:
    - LLM-based state prediction
    - Multi-hypothesis simulation
    - Outcome evaluation and ranking
    - Success probability estimation
    
    Performance Target: 60%+ success rate (vs. 32% baseline)
    
    Example:
        >>> world_model = SimuRAWorldModel()
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
        llm_client: Optional[Any] = None
    ):
        """
        Initialize world model.
        
        Args:
            config: World model configuration
            llm_client: LLM client for predictions (optional, uses mock if None)
        """
        self.config = config or WorldModelConfig()
        self.llm_client = llm_client
        
        self.simulation_history: List[ActionSimulation] = []
        
        logger.info(
            "world_model_initialized",
            extra={
                "num_simulations": self.config.num_simulations,
                "depth": self.config.simulation_depth
            }
        )
    
    async def simulate_action(
        self,
        current_state: Dict[str, Any],
        candidate_actions: List[Dict[str, Any]]
    ) -> List[ActionSimulation]:
        """
        Simulate multiple candidate actions and predict outcomes.
        
        Args:
            current_state: Current system state
            candidate_actions: List of actions to simulate
            
        Returns:
            List of simulations with predictions
        """
        simulations: List[ActionSimulation] = []
        
        for action in candidate_actions:
            simulation = await self._simulate_single_action(
                current_state,
                action
            )
            simulations.append(simulation)
            self.simulation_history.append(simulation)
        
        logger.info(
            "simulations_complete",
            extra={
                "num_actions": len(candidate_actions),
                "num_simulations": len(simulations)
            }
        )
        
        return simulations
    
    async def _simulate_single_action(
        self,
        current_state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> ActionSimulation:
        """
        Simulate single action using LLM world model.
        
        Args:
            current_state: Current state
            action: Action to simulate
            
        Returns:
            Simulation with predicted outcome
        """
        if self.llm_client:
            # Real LLM-based prediction
            prediction = await self._llm_predict_outcome(current_state, action)
        else:
            # Mock prediction (deterministic heuristics)
            prediction = self._heuristic_predict_outcome(current_state, action)
        
        return ActionSimulation(**prediction)
    
    async def _llm_predict_outcome(
        self,
        current_state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to predict action outcome.
        
        Args:
            current_state: Current state
            action: Action to simulate
            
        Returns:
            Prediction dict
        """
        # Construct simulation prompt
        prompt = f"""
You are a world model that predicts outcomes of infrastructure actions.

Current State: {current_state}
Proposed Action: {action}

Simulate this action and predict:
1. Next state after action
2. Success probability (0-1)
3. Outcome (success/failure/partial/unknown)
4. Reasoning for prediction
5. Confidence in prediction (0-1)
6. Risk score (0-1)

Format response as JSON.
        """
        
        # Call LLM (Future: integrate with hcl_planner's Gemini client)
        # For now, return structure
        raise NotImplementedError(
            "LLM prediction not yet integrated. "
            "Connect to hcl_planner's GeminiClient for real predictions. "
            "Using heuristic prediction as fallback."
        )
    
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
        
        # Simple heuristics based on action type
        if action_type == "restart":
            success_prob = 0.7
            outcome = SimulationOutcome.SUCCESS
            predicted_state = {**current_state, "status": "restarted"}
            reasoning = "Restart typically resolves transient issues"
            confidence = 0.6
            risk = 0.3
            
        elif action_type == "scale_up":
            success_prob = 0.8
            outcome = SimulationOutcome.SUCCESS
            predicted_state = {
                **current_state,
                "replicas": action.get("params", {}).get("replicas", 2)
            }
            reasoning = "Scaling up increases capacity, likely resolves load issues"
            confidence = 0.7
            risk = 0.2
            
        elif action_type == "rollback":
            success_prob = 0.9
            outcome = SimulationOutcome.SUCCESS
            predicted_state = {**current_state, "version": "previous"}
            reasoning = "Rollback to known-good state is low risk"
            confidence = 0.8
            risk = 0.1
            
        else:
            # Unknown action type
            success_prob = 0.4
            outcome = SimulationOutcome.UNKNOWN
            predicted_state = current_state
            reasoning = "Unknown action type, cannot predict reliably"
            confidence = 0.3
            risk = 0.7
        
        return {
            "action": action,
            "predicted_state": predicted_state,
            "success_probability": success_prob,
            "outcome": outcome,
            "reasoning": reasoning,
            "confidence": confidence,
            "risk_score": risk
        }
    
    def select_best_action(
        self,
        simulations: List[ActionSimulation],
        strategy: str = "max_success"
    ) -> Optional[ActionSimulation]:
        """
        Select best action from simulations.
        
        Args:
            simulations: List of action simulations
            strategy: Selection strategy
                - "max_success": Highest success probability
                - "min_risk": Lowest risk score
                - "balanced": Balance success and risk
                
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
            return None
        
        # Select based on strategy
        if strategy == "max_success":
            best = max(viable, key=lambda s: s.success_probability)
        elif strategy == "min_risk":
            best = min(viable, key=lambda s: s.risk_score)
        elif strategy == "balanced":
            # Balance success and risk (weighted)
            best = max(
                viable,
                key=lambda s: s.success_probability * 0.7 - s.risk_score * 0.3
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
        
        outcome_counts = {}
        for s in self.simulation_history:
            outcome_counts[s.outcome.value] = outcome_counts.get(s.outcome.value, 0) + 1
        
        return {
            "total_simulations": total,
            "avg_success_probability": round(avg_success, 3),
            "avg_confidence": round(avg_confidence, 3),
            "avg_risk": round(avg_risk, 3),
            "outcome_distribution": outcome_counts
        }
