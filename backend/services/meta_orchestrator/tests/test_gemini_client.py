"""
Tests for Gemini 3 Pro Client.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict

import httpx

from core.gemini_client import (
    GeminiClient,
    GeminiConfig,
    SimulationPrediction,
)


class TestGeminiConfig:
    """Tests for GeminiConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GeminiConfig(api_key="test-key")

        assert config.api_key == "test-key"
        assert config.model == "gemini-3-pro-preview"
        assert config.thinking_level == "high"
        assert config.max_output_tokens == 8192
        assert config.timeout_seconds == 60
        assert config.use_thought_signatures is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = GeminiConfig(
            api_key="custom-key",
            model="gemini-3-pro-image-preview",
            thinking_level="low",
            max_output_tokens=4096,
            timeout_seconds=120,
            use_thought_signatures=False,
        )

        assert config.api_key == "custom-key"
        assert config.model == "gemini-3-pro-image-preview"
        assert config.thinking_level == "low"
        assert config.max_output_tokens == 4096
        assert config.timeout_seconds == 120
        assert config.use_thought_signatures is False


class TestSimulationPrediction:
    """Tests for SimulationPrediction."""

    def test_default_prediction(self):
        """Test default prediction values."""
        pred = SimulationPrediction()

        assert pred.predicted_state == {}
        assert pred.success_probability == 0.5
        assert pred.outcome == "unknown"
        assert pred.reasoning == ""
        assert pred.confidence == 0.5
        assert pred.risk_score == 0.5
        assert pred.side_effects == []
        assert pred.thought_signature is None

    def test_custom_prediction(self):
        """Test custom prediction values."""
        pred = SimulationPrediction(
            predicted_state={"status": "running"},
            success_probability=0.9,
            outcome="success",
            reasoning="Test reasoning",
            confidence=0.85,
            risk_score=0.15,
            side_effects=["downtime"],
            thought_signature="sig123",
        )

        assert pred.predicted_state == {"status": "running"}
        assert pred.success_probability == 0.9
        assert pred.outcome == "success"
        assert pred.reasoning == "Test reasoning"
        assert pred.confidence == 0.85
        assert pred.risk_score == 0.15
        assert pred.side_effects == ["downtime"]
        assert pred.thought_signature == "sig123"


class TestGeminiClient:
    """Tests for GeminiClient."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return GeminiConfig(api_key="test-api-key")

    @pytest.fixture
    def client(self, config):
        """Create test client."""
        return GeminiClient(config)

    def test_init(self, client, config):
        """Test client initialization."""
        assert client.config == config
        assert client._client is None
        assert client._thought_signature is None

    @pytest.mark.asyncio
    async def test_get_client_creates_new(self, client):
        """Test _get_client creates new client."""
        http_client = await client._get_client()

        assert http_client is not None
        assert isinstance(http_client, httpx.AsyncClient)
        assert client._client is http_client

        await client.close()

    @pytest.mark.asyncio
    async def test_get_client_reuses_existing(self, client):
        """Test _get_client reuses existing client."""
        http_client1 = await client._get_client()
        http_client2 = await client._get_client()

        assert http_client1 is http_client2

        await client.close()

    @pytest.mark.asyncio
    async def test_close(self, client):
        """Test client close."""
        await client._get_client()
        assert client._client is not None

        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_close_when_no_client(self, client):
        """Test close when no client exists."""
        await client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_simulate_action_success(self, client):
        """Test successful action simulation."""
        mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "predicted_state": {"status": "running"},
                            "success_probability": 0.85,
                            "outcome": "success",
                            "reasoning": "Action will succeed",
                            "confidence": 0.9,
                            "risk_score": 0.1,
                            "side_effects": []
                        })
                    }, {
                        "thoughtSignature": "sig_abc123"
                    }]
                }
            }]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            mock_get.return_value = mock_http

            prediction = await client.simulate_action(
                state={"cpu": 80},
                action={"type": "restart"}
            )

            assert prediction.success_probability == 0.85
            assert prediction.outcome == "success"
            assert prediction.thought_signature == "sig_abc123"

    @pytest.mark.asyncio
    async def test_simulate_action_with_context(self, client):
        """Test action simulation with context."""
        mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "predicted_state": {"status": "scaled"},
                            "success_probability": 0.9,
                            "outcome": "success",
                            "reasoning": "Context used",
                            "confidence": 0.8,
                            "risk_score": 0.2,
                            "side_effects": ["cost_increase"]
                        })
                    }]
                }
            }]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            mock_get.return_value = mock_http

            prediction = await client.simulate_action(
                state={"replicas": 1},
                action={"type": "scale_up"},
                context={"budget": "unlimited"}
            )

            assert prediction.success_probability == 0.9
            assert prediction.side_effects == ["cost_increase"]

    @pytest.mark.asyncio
    async def test_simulate_action_fallback_on_error(self, client):
        """Test fallback when API call fails."""
        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(side_effect=Exception("API Error"))
            mock_get.return_value = mock_http

            prediction = await client.simulate_action(
                state={"status": "failed"},
                action={"type": "restart"}
            )

            # Should use heuristic fallback
            assert prediction.success_probability == 0.7
            assert prediction.outcome == "success"
            assert "Fallback" in prediction.reasoning

    @pytest.mark.asyncio
    async def test_simulate_sequence_success(self, client):
        """Test successful sequence simulation."""
        mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps([
                            {
                                "predicted_state": {"step": 1},
                                "success_probability": 0.8,
                                "outcome": "success",
                                "reasoning": "Step 1",
                                "confidence": 0.7,
                                "risk_score": 0.2,
                                "side_effects": []
                            },
                            {
                                "predicted_state": {"step": 2},
                                "success_probability": 0.9,
                                "outcome": "success",
                                "reasoning": "Step 2",
                                "confidence": 0.8,
                                "risk_score": 0.1,
                                "side_effects": []
                            }
                        ])
                    }]
                }
            }]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            mock_get.return_value = mock_http

            predictions = await client.simulate_sequence(
                initial_state={"status": "init"},
                actions=[{"type": "restart"}, {"type": "scale_up"}]
            )

            assert len(predictions) == 2
            assert predictions[0].success_probability == 0.8
            assert predictions[1].success_probability == 0.9

    @pytest.mark.asyncio
    async def test_simulate_sequence_fallback_on_error(self, client):
        """Test sequence fallback when API fails."""
        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(side_effect=Exception("API Error"))
            mock_get.return_value = mock_http

            predictions = await client.simulate_sequence(
                initial_state={"status": "init"},
                actions=[{"type": "restart"}, {"type": "scale_up"}]
            )

            assert len(predictions) == 2
            # All should be fallback predictions
            for pred in predictions:
                assert "Fallback" in pred.reasoning

    @pytest.mark.asyncio
    async def test_call_gemini_with_thought_signature(self, config):
        """Test API call with existing thought signature."""
        config.use_thought_signatures = True
        client = GeminiClient(config)
        client._thought_signature = "existing_sig"

        mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "predicted_state": {},
                            "success_probability": 0.5,
                            "outcome": "success"
                        })
                    }]
                }
            }]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = lambda: None
            mock_http.post = AsyncMock(return_value=mock_response_obj)
            mock_get.return_value = mock_http

            response_text, thought_sig = await client._call_gemini("test prompt")

            # Verify thought signature was included in request
            call_args = mock_http.post.call_args
            payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
            parts = payload.get('contents', [{}])[0].get('parts', [])
            has_thought_sig = any('thoughtSignature' in p for p in parts)
            assert has_thought_sig

    @pytest.mark.asyncio
    async def test_call_gemini_no_candidates(self, client):
        """Test API call with no candidates in response."""
        mock_response = {"candidates": []}

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            mock_get.return_value = mock_http

            with pytest.raises(ValueError, match="No candidates"):
                await client._call_gemini("test prompt")

    @pytest.mark.asyncio
    async def test_call_gemini_no_parts(self, client):
        """Test API call with no parts in response."""
        mock_response = {
            "candidates": [{
                "content": {"parts": []}
            }]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            mock_get.return_value = mock_http

            with pytest.raises(ValueError, match="No parts"):
                await client._call_gemini("test prompt")

    def test_parse_prediction_valid_json(self, client):
        """Test parsing valid JSON prediction."""
        response = json.dumps({
            "predicted_state": {"status": "ok"},
            "success_probability": 0.75,
            "outcome": "success",
            "reasoning": "Test",
            "confidence": 0.8,
            "risk_score": 0.2,
            "side_effects": []
        })

        pred = client._parse_prediction(response)

        assert pred.success_probability == 0.75
        assert pred.outcome == "success"

    def test_parse_prediction_markdown_json(self, client):
        """Test parsing JSON wrapped in markdown."""
        response = """```json
{
    "predicted_state": {"status": "ok"},
    "success_probability": 0.8,
    "outcome": "success",
    "reasoning": "Test",
    "confidence": 0.7,
    "risk_score": 0.3,
    "side_effects": []
}
```"""

        pred = client._parse_prediction(response)

        assert pred.success_probability == 0.8
        assert pred.outcome == "success"

    def test_parse_prediction_invalid_json(self, client):
        """Test parsing invalid JSON."""
        response = "not valid json"

        pred = client._parse_prediction(response)

        assert pred.outcome == "unknown"
        assert "Parse error" in pred.reasoning

    def test_parse_sequence_valid_array(self, client):
        """Test parsing valid JSON array."""
        response = json.dumps([
            {"predicted_state": {}, "success_probability": 0.8, "outcome": "success"},
            {"predicted_state": {}, "success_probability": 0.9, "outcome": "success"}
        ])

        preds = client._parse_sequence(response, 2)

        assert len(preds) == 2
        assert preds[0].success_probability == 0.8
        assert preds[1].success_probability == 0.9

    def test_parse_sequence_single_object(self, client):
        """Test parsing single object in sequence."""
        response = json.dumps({
            "predicted_state": {},
            "success_probability": 0.85,
            "outcome": "success"
        })

        preds = client._parse_sequence(response, 1)

        assert len(preds) == 1
        assert preds[0].success_probability == 0.85

    def test_parse_sequence_markdown_wrapped(self, client):
        """Test parsing markdown-wrapped sequence."""
        response = """```json
[
    {"predicted_state": {}, "success_probability": 0.7, "outcome": "success"}
]
```"""

        preds = client._parse_sequence(response, 1)

        assert len(preds) == 1
        assert preds[0].success_probability == 0.7

    def test_parse_sequence_invalid_json(self, client):
        """Test parsing invalid JSON sequence."""
        response = "invalid json"

        preds = client._parse_sequence(response, 3)

        assert len(preds) == 3
        for pred in preds:
            assert pred.outcome == "unknown"
            assert "Parse error" in pred.reasoning

    def test_fallback_prediction_restart(self, client):
        """Test fallback prediction for restart action."""
        pred = client._fallback_prediction(
            state={"status": "failed"},
            action={"type": "restart"},
            error="API timeout"
        )

        assert pred.success_probability == 0.7
        assert pred.outcome == "success"
        assert pred.risk_score == 0.3
        assert "restart" in pred.predicted_state.get("action_applied", "")

    def test_fallback_prediction_scale_up(self, client):
        """Test fallback prediction for scale_up action."""
        pred = client._fallback_prediction(
            state={"replicas": 1},
            action={"type": "scale_up"},
            error="Connection error"
        )

        assert pred.success_probability == 0.8
        assert pred.risk_score == 0.2

    def test_fallback_prediction_scale_down(self, client):
        """Test fallback prediction for scale_down action."""
        pred = client._fallback_prediction(
            state={"replicas": 5},
            action={"type": "scale_down"},
            error="Timeout"
        )

        assert pred.success_probability == 0.75
        assert pred.risk_score == 0.4

    def test_fallback_prediction_rollback(self, client):
        """Test fallback prediction for rollback action."""
        pred = client._fallback_prediction(
            state={"version": "v2"},
            action={"type": "rollback"},
            error="Rate limit"
        )

        assert pred.success_probability == 0.85
        assert pred.risk_score == 0.15

    def test_fallback_prediction_deploy(self, client):
        """Test fallback prediction for deploy action."""
        pred = client._fallback_prediction(
            state={"version": "v1"},
            action={"type": "deploy"},
            error="API error"
        )

        assert pred.success_probability == 0.6
        assert pred.outcome == "partial"
        assert pred.risk_score == 0.5

    def test_fallback_prediction_unknown_action(self, client):
        """Test fallback prediction for unknown action."""
        pred = client._fallback_prediction(
            state={"status": "running"},
            action={"type": "custom_action"},
            error="Unknown action"
        )

        assert pred.success_probability == 0.4
        assert pred.outcome == "unknown"
        assert pred.risk_score == 0.6
        assert "custom_action" in pred.reasoning

    def test_reset_thought_context(self, client):
        """Test resetting thought context."""
        client._thought_signature = "some_signature"

        client.reset_thought_context()

        assert client._thought_signature is None

    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        mock_response = {
            "models": [
                {"name": "models/gemini-3-pro-preview"},
                {"name": "models/gemini-3-pro-image-preview"}
            ]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.get = AsyncMock(return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response
            ))
            mock_get.return_value = mock_http

            health = await client.health_check()

            assert health["healthy"] is True
            assert health["model_available"] is True
            assert health["model"] == "gemini-3-pro-preview"

    @pytest.mark.asyncio
    async def test_health_check_model_not_available(self, client):
        """Test health check when model not available."""
        mock_response = {
            "models": [
                {"name": "models/other-model"}
            ]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.get = AsyncMock(return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response
            ))
            mock_get.return_value = mock_http

            health = await client.health_check()

            assert health["healthy"] is False
            assert health["model_available"] is False

    @pytest.mark.asyncio
    async def test_health_check_api_error(self, client):
        """Test health check when API fails."""
        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.get = AsyncMock(side_effect=Exception("Connection failed"))
            mock_get.return_value = mock_http

            health = await client.health_check()

            assert health["healthy"] is False
            assert "Connection failed" in health["error"]

    @pytest.mark.asyncio
    async def test_call_gemini_with_override_thinking_level(self, client):
        """Test API call with overridden thinking level."""
        mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "predicted_state": {},
                            "success_probability": 0.5,
                            "outcome": "success"
                        })
                    }]
                }
            }]
        }

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = lambda: None
            mock_http.post = AsyncMock(return_value=mock_response_obj)
            mock_get.return_value = mock_http

            await client._call_gemini("test", thinking_level="low")

            # Verify thinking level was overridden
            call_args = mock_http.post.call_args
            payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
            assert payload.get('thinkingConfig', {}).get('thinkingLevel') == "low"

    @pytest.mark.asyncio
    async def test_get_client_recreates_after_close(self, client):
        """Test _get_client recreates after close."""
        http_client1 = await client._get_client()
        await client.close()

        http_client2 = await client._get_client()

        assert http_client2 is not None
        assert http_client1 is not http_client2

        await client.close()
