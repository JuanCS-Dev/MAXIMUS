"""
Tests for SimuRA World Model with Dyna-Think integration.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from core.world_model import (
    SimuRAWorldModel,
    WorldModelConfig,
    ActionSimulation,
    SimulationOutcome,
    DynaThinkState,
)
from core.gemini_client import (
    GeminiClient,
    GeminiConfig,
    SimulationPrediction,
)


class TestWorldModelConfig:
    """Tests for WorldModelConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WorldModelConfig()

        assert config.num_simulations == 5
        assert config.simulation_depth == 3
        assert config.min_success_threshold == 0.3
        assert config.use_parallel_simulations is True
        assert config.use_gemini is True
        assert config.gemini_config is None

    def test_custom_config(self):
        """Test custom configuration."""
        gemini_config = GeminiConfig(api_key="test-key")
        config = WorldModelConfig(
            num_simulations=10,
            simulation_depth=5,
            min_success_threshold=0.5,
            use_parallel_simulations=False,
            use_gemini=True,
            gemini_config=gemini_config,
        )

        assert config.num_simulations == 10
        assert config.simulation_depth == 5
        assert config.min_success_threshold == 0.5
        assert config.use_parallel_simulations is False
        assert config.gemini_config.api_key == "test-key"


class TestActionSimulation:
    """Tests for ActionSimulation model."""

    def test_basic_simulation(self):
        """Test basic simulation creation."""
        sim = ActionSimulation(
            action={"type": "restart"},
            predicted_state={"status": "running"},
            success_probability=0.8,
            outcome=SimulationOutcome.SUCCESS,
            reasoning="Test reasoning",
        )

        assert sim.action["type"] == "restart"
        assert sim.success_probability == 0.8
        assert sim.outcome == SimulationOutcome.SUCCESS
        assert sim.confidence == 0.5  # Default
        assert sim.risk_score == 0.5  # Default
        assert sim.simulation_depth == 1  # Default

    def test_simulation_with_all_fields(self):
        """Test simulation with all fields."""
        sim = ActionSimulation(
            action={"type": "scale_up", "params": {"replicas": 3}},
            predicted_state={"replicas": 3},
            success_probability=0.9,
            outcome=SimulationOutcome.SUCCESS,
            reasoning="Scaling improves performance",
            confidence=0.85,
            risk_score=0.15,
            side_effects=["increased cost"],
            simulation_depth=2,
            alternative_outcomes=[{"outcome": "partial", "prob": 0.1}],
        )

        assert sim.confidence == 0.85
        assert sim.risk_score == 0.15
        assert len(sim.side_effects) == 1
        assert sim.simulation_depth == 2


class TestSimuRAWorldModel:
    """Tests for SimuRAWorldModel."""

    @pytest.mark.asyncio
    async def test_init_without_gemini(self):
        """Test initialization without Gemini."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        assert model._gemini is None
        assert model.config.use_gemini is False
        assert len(model.simulation_history) == 0

    @pytest.mark.asyncio
    async def test_init_with_gemini_config(self):
        """Test initialization with Gemini config."""
        gemini_config = GeminiConfig(api_key="test-key")
        config = WorldModelConfig(use_gemini=True, gemini_config=gemini_config)

        model = SimuRAWorldModel(config=config)

        assert model._gemini is not None
        assert isinstance(model._gemini, GeminiClient)

    @pytest.mark.asyncio
    async def test_init_with_external_gemini_client(self):
        """Test initialization with pre-configured Gemini client."""
        mock_client = MagicMock(spec=GeminiClient)

        model = SimuRAWorldModel(gemini_client=mock_client)

        assert model._gemini == mock_client

    @pytest.mark.asyncio
    async def test_heuristic_prediction_restart(self):
        """Test heuristic prediction for restart action."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "failed"},
            candidate_actions=[{"type": "restart"}],
        )

        assert len(simulations) == 1
        sim = simulations[0]
        assert sim.success_probability == 0.7
        assert sim.outcome == SimulationOutcome.SUCCESS
        assert "restarted" in sim.predicted_state.get("status", "")

    @pytest.mark.asyncio
    async def test_heuristic_prediction_scale_up(self):
        """Test heuristic prediction for scale_up action."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"replicas": 1},
            candidate_actions=[{"type": "scale_up", "params": {"replicas": 3}}],
        )

        assert len(simulations) == 1
        sim = simulations[0]
        assert sim.success_probability == 0.8
        assert sim.outcome == SimulationOutcome.SUCCESS
        assert sim.predicted_state.get("replicas") == 3

    @pytest.mark.asyncio
    async def test_heuristic_prediction_rollback(self):
        """Test heuristic prediction for rollback action."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"version": "v2"},
            candidate_actions=[{"type": "rollback"}],
        )

        assert len(simulations) == 1
        sim = simulations[0]
        assert sim.success_probability == 0.9
        assert sim.risk_score == 0.1

    @pytest.mark.asyncio
    async def test_heuristic_prediction_unknown_action(self):
        """Test heuristic prediction for unknown action type."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[{"type": "unknown_action"}],
        )

        assert len(simulations) == 1
        sim = simulations[0]
        assert sim.success_probability == 0.4
        assert sim.outcome == SimulationOutcome.UNKNOWN

    @pytest.mark.asyncio
    async def test_multiple_actions_simulation(self):
        """Test simulating multiple actions at once."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "degraded"},
            candidate_actions=[
                {"type": "restart"},
                {"type": "scale_up", "params": {"replicas": 3}},
                {"type": "rollback"},
            ],
        )

        assert len(simulations) == 3
        assert all(isinstance(s, ActionSimulation) for s in simulations)

    @pytest.mark.asyncio
    async def test_select_best_action_max_success(self):
        """Test selecting best action with max_success strategy."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "failed"},
            candidate_actions=[
                {"type": "restart"},  # 0.7
                {"type": "rollback"},  # 0.9
                {"type": "deploy"},  # 0.6
            ],
        )

        best = model.select_best_action(simulations, strategy="max_success")

        assert best is not None
        assert best.action["type"] == "rollback"

    @pytest.mark.asyncio
    async def test_select_best_action_min_risk(self):
        """Test selecting best action with min_risk strategy."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[
                {"type": "restart"},  # risk 0.3
                {"type": "rollback"},  # risk 0.1
                {"type": "deploy"},  # risk 0.5
            ],
        )

        best = model.select_best_action(simulations, strategy="min_risk")

        assert best is not None
        assert best.action["type"] == "rollback"

    @pytest.mark.asyncio
    async def test_select_best_action_balanced(self):
        """Test selecting best action with balanced strategy."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[
                {"type": "restart"},
                {"type": "scale_up"},
                {"type": "rollback"},
            ],
        )

        best = model.select_best_action(simulations, strategy="balanced")

        assert best is not None
        # Rollback has best balance (high success, low risk)
        assert best.action["type"] == "rollback"

    @pytest.mark.asyncio
    async def test_select_best_action_conservative(self):
        """Test selecting best action with conservative strategy."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[
                {"type": "restart"},
                {"type": "rollback"},
                {"type": "deploy"},
            ],
        )

        best = model.select_best_action(simulations, strategy="conservative")

        assert best is not None
        # Conservative should pick lowest risk
        assert best.action["type"] == "rollback"

    @pytest.mark.asyncio
    async def test_select_best_action_empty_list(self):
        """Test selecting from empty list."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        best = model.select_best_action([])

        assert best is None

    @pytest.mark.asyncio
    async def test_select_best_action_below_threshold(self):
        """Test selecting when all below threshold."""
        config = WorldModelConfig(use_gemini=False, min_success_threshold=0.95)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[
                {"type": "restart"},  # 0.7
                {"type": "rollback"},  # 0.9
            ],
        )

        # Should still return best option even if below threshold
        best = model.select_best_action(simulations, strategy="max_success")

        assert best is not None
        assert best.action["type"] == "rollback"

    @pytest.mark.asyncio
    async def test_record_outcome_correct_prediction(self):
        """Test recording outcome when prediction was correct."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        sim = ActionSimulation(
            action={"type": "restart"},
            predicted_state={"status": "running"},
            success_probability=0.8,
            outcome=SimulationOutcome.SUCCESS,
            reasoning="Test",
        )

        initial_accuracy = model._dyna_state.prediction_accuracy

        model.record_outcome(sim, "success")

        # Accuracy should increase
        assert model._dyna_state.prediction_accuracy > initial_accuracy
        assert len(model._outcome_history) == 1

    @pytest.mark.asyncio
    async def test_record_outcome_incorrect_prediction(self):
        """Test recording outcome when prediction was incorrect."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        sim = ActionSimulation(
            action={"type": "restart"},
            predicted_state={"status": "running"},
            success_probability=0.8,
            outcome=SimulationOutcome.SUCCESS,
            reasoning="Test",
        )

        initial_accuracy = model._dyna_state.prediction_accuracy

        model.record_outcome(sim, "failure")

        # Accuracy should decrease
        assert model._dyna_state.prediction_accuracy < initial_accuracy

    @pytest.mark.asyncio
    async def test_simulate_sequence(self):
        """Test simulating a sequence of actions."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_sequence(
            initial_state={"status": "failed", "replicas": 1},
            action_sequence=[
                {"type": "restart"},
                {"type": "scale_up", "params": {"replicas": 3}},
            ],
        )

        assert len(simulations) == 2
        assert simulations[0].simulation_depth == 1
        assert simulations[1].simulation_depth == 2

    @pytest.mark.asyncio
    async def test_get_simulation_stats_empty(self):
        """Test getting stats with no simulations."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        stats = model.get_simulation_stats()

        assert stats["total_simulations"] == 0

    @pytest.mark.asyncio
    async def test_get_simulation_stats_with_data(self):
        """Test getting stats with simulations."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[
                {"type": "restart"},
                {"type": "scale_up"},
            ],
        )

        stats = model.get_simulation_stats()

        assert stats["total_simulations"] == 2
        assert "avg_success_probability" in stats
        assert "avg_confidence" in stats
        assert "outcome_distribution" in stats
        assert stats["gemini_enabled"] is False

    @pytest.mark.asyncio
    async def test_health_check_without_gemini(self):
        """Test health check without Gemini."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        health = await model.health_check()

        assert health["healthy"] is True
        assert health["gemini_enabled"] is False

    @pytest.mark.asyncio
    async def test_confidence_adjustment(self):
        """Test confidence adjustment based on history."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        # Set high accuracy
        model._dyna_state.prediction_accuracy = 0.9

        adjusted = model._adjust_confidence(0.5)

        # Should be boosted by high accuracy
        assert adjusted > 0.5

    @pytest.mark.asyncio
    async def test_context_enrichment(self):
        """Test context enrichment with history."""
        config = WorldModelConfig(use_gemini=False)
        model = SimuRAWorldModel(config=config)

        # Add some history
        model._dyna_state.action_history = [{"type": "restart"}]
        model._dyna_state.prediction_accuracy = 0.8

        context = model._build_context({"custom": "value"})

        assert "recent_actions" in context
        assert "model_accuracy" in context
        assert context["custom"] == "value"

    @pytest.mark.asyncio
    async def test_parallel_simulation(self):
        """Test parallel simulation execution."""
        config = WorldModelConfig(use_gemini=False, use_parallel_simulations=True)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[
                {"type": "restart"},
                {"type": "scale_up"},
                {"type": "rollback"},
            ],
        )

        assert len(simulations) == 3

    @pytest.mark.asyncio
    async def test_sequential_simulation(self):
        """Test sequential simulation execution."""
        config = WorldModelConfig(use_gemini=False, use_parallel_simulations=False)
        model = SimuRAWorldModel(config=config)

        simulations = await model.simulate_action(
            current_state={"status": "running"},
            candidate_actions=[
                {"type": "restart"},
                {"type": "scale_up"},
            ],
        )

        assert len(simulations) == 2


class TestWorldModelWithGemini:
    """Tests for world model with Gemini integration."""

    @pytest.mark.asyncio
    async def test_gemini_prediction_success(self):
        """Test successful Gemini prediction."""
        mock_client = MagicMock(spec=GeminiClient)
        mock_client.simulate_action = AsyncMock(
            return_value=SimulationPrediction(
                predicted_state={"status": "running"},
                success_probability=0.85,
                outcome="success",
                reasoning="Gemini reasoning",
                confidence=0.9,
                risk_score=0.15,
                side_effects=["brief downtime"],
            )
        )

        model = SimuRAWorldModel(gemini_client=mock_client)

        simulations = await model.simulate_action(
            current_state={"status": "failed"},
            candidate_actions=[{"type": "restart"}],
        )

        assert len(simulations) == 1
        sim = simulations[0]
        assert sim.success_probability == 0.85
        assert sim.reasoning == "Gemini reasoning"
        mock_client.simulate_action.assert_called_once()

    @pytest.mark.asyncio
    async def test_gemini_prediction_fallback_on_error(self):
        """Test fallback to heuristics when Gemini fails."""
        mock_client = MagicMock(spec=GeminiClient)
        mock_client.simulate_action = AsyncMock(
            side_effect=Exception("API Error")
        )

        model = SimuRAWorldModel(gemini_client=mock_client)

        simulations = await model.simulate_action(
            current_state={"status": "failed"},
            candidate_actions=[{"type": "restart"}],
        )

        assert len(simulations) == 1
        sim = simulations[0]
        # Should use heuristic values
        assert sim.success_probability == 0.7
        assert sim.outcome == SimulationOutcome.SUCCESS

    @pytest.mark.asyncio
    async def test_health_check_with_gemini(self):
        """Test health check with Gemini."""
        mock_client = MagicMock(spec=GeminiClient)
        mock_client.health_check = AsyncMock(
            return_value={"healthy": True, "model": "gemini-2.0-flash"}
        )

        model = SimuRAWorldModel(gemini_client=mock_client)

        health = await model.health_check()

        assert health["healthy"] is True
        assert health["gemini_enabled"] is True
        assert "gemini_health" in health

    @pytest.mark.asyncio
    async def test_close(self):
        """Test cleanup on close."""
        mock_client = MagicMock(spec=GeminiClient)
        mock_client.close = AsyncMock()

        model = SimuRAWorldModel(gemini_client=mock_client)

        await model.close()

        mock_client.close.assert_called_once()


class TestDynaThinkState:
    """Tests for DynaThinkState."""

    def test_default_state(self):
        """Test default state values."""
        state = DynaThinkState()

        assert state.current_state == {}
        assert state.action_history == []
        assert state.prediction_accuracy == 0.5
        assert state.learning_rate == 0.1

    def test_state_with_values(self):
        """Test state with custom values."""
        state = DynaThinkState(
            current_state={"cpu": 50},
            action_history=[{"type": "restart"}],
            prediction_accuracy=0.8,
            learning_rate=0.2,
        )

        assert state.current_state["cpu"] == 50
        assert len(state.action_history) == 1
        assert state.prediction_accuracy == 0.8
