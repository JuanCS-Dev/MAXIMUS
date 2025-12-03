"""
SimuRA World Model - Backwards Compatibility Module
====================================================

This module re-exports all components from the world_model package
for backwards compatibility.

The actual implementation has been decomposed into:
- world_model/models.py: Data models and enums
- world_model/heuristics.py: Heuristic predictions
- world_model/simulator.py: Main SimuRAWorldModel class

Import from this module or directly from the package:
    # Both work:
    from core.world_model import SimuRAWorldModel
    from core.world_model.simulator import SimuRAWorldModel
"""

from __future__ import annotations

# Re-export all public API from the package submodules
from .world_model.models import (
    ActionSimulation,
    DynaThinkState,
    SimulationOutcome,
    WorldModelConfig,
)
from .world_model.heuristics import predict_outcome_heuristic
from .world_model.simulator import SimuRAWorldModel

__all__ = [
    "SimuRAWorldModel",
    "ActionSimulation",
    "SimulationOutcome",
    "WorldModelConfig",
    "DynaThinkState",
    "predict_outcome_heuristic",
]
