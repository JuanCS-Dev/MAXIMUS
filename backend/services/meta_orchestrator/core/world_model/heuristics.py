"""
World Model - Heuristic Predictions
====================================

Deterministic heuristic-based prediction for action outcomes.
Used as fallback when Gemini is unavailable.

Each action type has predefined success probabilities, risk scores,
and expected side effects based on operational experience.
"""

from __future__ import annotations

from typing import Any, Dict

from .models import SimulationOutcome


# Action heuristics table
# Each entry defines expected behavior for an action type
ACTION_HEURISTICS: Dict[str, Dict[str, Any]] = {
    "restart": {
        "success_prob": 0.7,
        "outcome": SimulationOutcome.SUCCESS,
        "state_changes": {"status": "restarted"},
        "reasoning": "Restart typically resolves transient issues",
        "confidence": 0.6,
        "risk": 0.3,
        "side_effects": ["brief downtime", "connection reset"],
    },
    "scale_up": {
        "success_prob": 0.8,
        "outcome": SimulationOutcome.SUCCESS,
        "state_changes": {},  # Handled dynamically
        "reasoning": "Scaling up increases capacity, likely resolves load issues",
        "confidence": 0.7,
        "risk": 0.2,
        "side_effects": ["increased cost", "warm-up time"],
    },
    "scale_down": {
        "success_prob": 0.75,
        "outcome": SimulationOutcome.SUCCESS,
        "state_changes": {},  # Handled dynamically
        "reasoning": "Scaling down reduces resources, may impact performance",
        "confidence": 0.6,
        "risk": 0.4,
        "side_effects": ["reduced capacity", "potential load issues"],
    },
    "rollback": {
        "success_prob": 0.9,
        "outcome": SimulationOutcome.SUCCESS,
        "state_changes": {"version": "previous"},
        "reasoning": "Rollback to known-good state is low risk",
        "confidence": 0.8,
        "risk": 0.1,
        "side_effects": ["feature regression"],
    },
    "deploy": {
        "success_prob": 0.6,
        "outcome": SimulationOutcome.PARTIAL,
        "state_changes": {"version": "new"},
        "reasoning": "Deployments carry moderate risk",
        "confidence": 0.5,
        "risk": 0.5,
        "side_effects": ["potential bugs", "performance changes"],
    },
    "migrate": {
        "success_prob": 0.5,
        "outcome": SimulationOutcome.PARTIAL,
        "state_changes": {"migrated": True},
        "reasoning": "Migrations are complex and risky",
        "confidence": 0.4,
        "risk": 0.7,
        "side_effects": ["data transfer time", "potential data loss"],
    },
}

# Default heuristic for unknown action types
DEFAULT_HEURISTIC: Dict[str, Any] = {
    "success_prob": 0.4,
    "outcome": SimulationOutcome.UNKNOWN,
    "state_changes": {},
    "reasoning": "Unknown action type, cannot predict reliably",
    "confidence": 0.3,
    "risk": 0.7,
    "side_effects": [],
}


def predict_outcome_heuristic(
    current_state: Dict[str, Any],
    action: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Heuristic-based prediction (deterministic fallback).

    Args:
        current_state: Current system state
        action: Action to simulate

    Returns:
        Prediction dict with outcome, probability, and reasoning
    """
    action_type = action.get("type", "unknown")
    heuristic = ACTION_HEURISTICS.get(action_type, DEFAULT_HEURISTIC)

    # Build predicted state
    predicted_state = {**current_state, **heuristic["state_changes"]}

    # Handle dynamic state changes for scale actions
    if action_type == "scale_up":
        replicas = action.get("params", {}).get("replicas", 2)
        predicted_state["replicas"] = replicas
    elif action_type == "scale_down":
        replicas = max(1, action.get("params", {}).get("replicas", 1))
        predicted_state["replicas"] = replicas

    return {
        "action": action,
        "predicted_state": predicted_state,
        "success_probability": heuristic["success_prob"],
        "outcome": heuristic["outcome"],
        "reasoning": heuristic["reasoning"],
        "confidence": heuristic["confidence"],
        "risk_score": heuristic["risk"],
        "side_effects": heuristic["side_effects"],
        "simulation_depth": 1,
    }
