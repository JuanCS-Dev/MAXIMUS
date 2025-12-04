"""
Tests for Tribunal MCP Tools
=============================

Scientific tests for Tribunal service integration via MCP tools.

Follows CODE_CONSTITUTION: ≥85% coverage, clear test names.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tools.tribunal_tools import (
    tribunal_evaluate,
    tribunal_health,
    tribunal_stats,
    TribunalEvaluateRequest,
    TribunalEvaluateResponse,
)
from clients.tribunal_client import TribunalClient
from middleware.circuit_breaker import ServiceUnavailableError


class TestTribunalEvaluateRequest:
    """Test TribunalEvaluateRequest validation."""

    def test_request_with_execution_log_only(self):
        """HYPOTHESIS: Request accepts execution_log alone."""
        request = TribunalEvaluateRequest(execution_log="test log")
        assert request.execution_log == "test log"
        assert request.context is None

    def test_request_with_context(self):
        """HYPOTHESIS: Request accepts optional context."""
        request = TribunalEvaluateRequest(
            execution_log="test log",
            context={"user": "test_user"}
        )
        assert request.context == {"user": "test_user"}

    def test_request_validation_empty_log(self):
        """HYPOTHESIS: Empty execution_log raises ValidationError."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            TribunalEvaluateRequest(execution_log="")

    def test_request_validation_log_too_long(self):
        """HYPOTHESIS: Execution log > 10000 chars raises error."""
        from pydantic import ValidationError
        long_log = "x" * 10001
        with pytest.raises(ValidationError):
            TribunalEvaluateRequest(execution_log=long_log)


class TestTribunalEvaluateResponse:
    """Test TribunalEvaluateResponse parsing."""

    def test_response_parsing_pass(self, mock_tribunal_response):
        """HYPOTHESIS: Response parses PASS decision."""
        response = TribunalEvaluateResponse(**mock_tribunal_response)
        assert response.decision == "PASS"
        assert response.consensus_score == 0.85
        assert response.punishment is None

    def test_response_parsing_with_punishment(self, mock_tribunal_response):
        """HYPOTHESIS: Response parses punishment when present."""
        mock_tribunal_response["decision"] = "FAIL"
        mock_tribunal_response["punishment"] = "retry_required"

        response = TribunalEvaluateResponse(**mock_tribunal_response)
        assert response.decision == "FAIL"
        assert response.punishment == "retry_required"

    def test_response_validation_invalid_decision(self, mock_tribunal_response):
        """HYPOTHESIS: Invalid decision raises ValidationError."""
        from pydantic import ValidationError
        mock_tribunal_response["decision"] = "INVALID"

        with pytest.raises(ValidationError):
            TribunalEvaluateResponse(**mock_tribunal_response)

    def test_response_validation_score_range(self, mock_tribunal_response):
        """HYPOTHESIS: Consensus score must be 0.0-1.0."""
        from pydantic import ValidationError
        mock_tribunal_response["consensus_score"] = 1.5

        with pytest.raises(ValidationError):
            TribunalEvaluateResponse(**mock_tribunal_response)


class TestTribunalEvaluateTool:
    """Test tribunal_evaluate MCP tool."""

    @pytest.mark.asyncio
    async def test_evaluate_success(self, config, mock_tribunal_response):
        """HYPOTHESIS: Successful evaluation returns verdict."""
        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_tribunal_response

            result = await tribunal_evaluate(
                execution_log="test log",
                context=None
            )

            assert result["decision"] == "PASS"
            assert result["consensus_score"] == 0.85
            mock_eval.assert_called_once()

    @pytest.mark.asyncio
    async def test_evaluate_with_context(self, config, mock_tribunal_response):
        """HYPOTHESIS: Context is passed to client."""
        context = {"user": "test_user", "session": "abc123"}

        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_tribunal_response

            await tribunal_evaluate(
                execution_log="test log",
                context=context,
                config=config
            )

            # Verify context was passed
            call_args = mock_eval.call_args
            assert call_args[1]["context"] == context

    @pytest.mark.asyncio
    async def test_evaluate_circuit_breaker_opens(self, config):
        """HYPOTHESIS: Circuit breaker opens after failures."""
        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            # Simulate repeated failures
            mock_eval.side_effect = Exception("Service down")

            # Try multiple times to trigger circuit breaker
            for _ in range(config.circuit_breaker_threshold):
                try:
                    await tribunal_evaluate(
                        execution_log="test log",
                        config=config
                    )
                except Exception:
                    pass

            # Next call should raise ServiceUnavailableError
            with pytest.raises(ServiceUnavailableError):
                await tribunal_evaluate(
                    execution_log="test log",
                    config=config
                )

    @pytest.mark.asyncio
    async def test_evaluate_rate_limiting(self, config):
        """HYPOTHESIS: Rate limiter blocks excessive calls."""
        config.rate_limit_per_tool = 2

        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = {"decision": "PASS", "consensus_score": 0.9}

            # First 2 calls should succeed
            await tribunal_evaluate("log1", )
            await tribunal_evaluate("log2", )

            # Third call should be rate limited
            from middleware.rate_limiter import RateLimitExceededError
            with pytest.raises(RateLimitExceededError):
                await tribunal_evaluate("log3", )

    @pytest.mark.asyncio
    async def test_evaluate_client_closed_properly(self, config, mock_tribunal_response):
        """HYPOTHESIS: Client is closed after call."""
        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            with patch.object(TribunalClient, 'close', new_callable=AsyncMock) as mock_close:
                mock_eval.return_value = mock_tribunal_response

                await tribunal_evaluate(
                    execution_log="test log",
                    config=config
                )

                mock_close.assert_called_once()


class TestTribunalHealthTool:
    """Test tribunal_health MCP tool."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, config):
        """HYPOTHESIS: Health check returns service status."""
        with patch.object(TribunalClient, 'get_health', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "judges": ["VERITAS", "SOPHIA", "DIKE"],
                "uptime": 3600
            }

            result = await tribunal_health()

            assert result["status"] == "healthy"
            assert len(result["judges"]) == 3
            mock_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, config):
        """HYPOTHESIS: Health check detects unhealthy service."""
        with patch.object(TribunalClient, 'get_health', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {
                "status": "unhealthy",
                "error": "Database connection failed"
            }

            result = await tribunal_health()

            assert result["status"] == "unhealthy"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_health_check_timeout(self, config):
        """HYPOTHESIS: Health check handles timeout gracefully."""
        with patch.object(TribunalClient, 'get_health', new_callable=AsyncMock) as mock_health:
            import httpx
            mock_health.side_effect = httpx.TimeoutException("Health check timeout")

            with pytest.raises(httpx.TimeoutException):
                await tribunal_health()


class TestTribunalStatsTool:
    """Test tribunal_stats MCP tool."""

    @pytest.mark.asyncio
    async def test_stats_success(self, config):
        """HYPOTHESIS: Stats returns tribunal metrics."""
        with patch.object(TribunalClient, 'get_stats', new_callable=AsyncMock) as mock_stats:
            mock_stats.return_value = {
                "total_evaluations": 1523,
                "decisions": {"PASS": 1245, "REVIEW": 200, "FAIL": 78},
                "avg_consensus_score": 0.82
            }

            result = await tribunal_stats()

            assert result["total_evaluations"] == 1523
            assert result["decisions"]["PASS"] == 1245
            mock_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_stats_empty(self, config):
        """HYPOTHESIS: Stats returns zeros for new tribunal."""
        with patch.object(TribunalClient, 'get_stats', new_callable=AsyncMock) as mock_stats:
            mock_stats.return_value = {
                "total_evaluations": 0,
                "decisions": {},
                "avg_consensus_score": 0.0
            }

            result = await tribunal_stats()

            assert result["total_evaluations"] == 0

    @pytest.mark.asyncio
    async def test_stats_client_closed(self, config):
        """HYPOTHESIS: Client is closed after stats call."""
        with patch.object(TribunalClient, 'get_stats', new_callable=AsyncMock) as mock_stats:
            with patch.object(TribunalClient, 'close', new_callable=AsyncMock) as mock_close:
                mock_stats.return_value = {"total_evaluations": 100}

                await tribunal_stats()

                mock_close.assert_called_once()


class TestTribunalToolsIntegration:
    """Test integration scenarios."""

    @pytest.mark.asyncio
    async def test_evaluate_then_check_health(self, config, mock_tribunal_response):
        """HYPOTHESIS: Can evaluate then check health."""
        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            with patch.object(TribunalClient, 'get_health', new_callable=AsyncMock) as mock_health:
                mock_eval.return_value = mock_tribunal_response
                mock_health.return_value = {"status": "healthy"}

                # Evaluate
                verdict = await tribunal_evaluate("test log", )
                assert verdict["decision"] == "PASS"

                # Check health
                health = await tribunal_health()
                assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_evaluate_then_check_stats(self, config, mock_tribunal_response):
        """HYPOTHESIS: Can evaluate then check stats."""
        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            with patch.object(TribunalClient, 'get_stats', new_callable=AsyncMock) as mock_stats:
                mock_eval.return_value = mock_tribunal_response
                mock_stats.return_value = {"total_evaluations": 1}

                # Evaluate
                verdict = await tribunal_evaluate("test log", )
                assert verdict["decision"] == "PASS"

                # Check stats
                stats = await tribunal_stats()
                assert stats["total_evaluations"] >= 1


class TestTribunalToolsErrorHandling:
    """Test error handling edge cases."""

    @pytest.mark.asyncio
    async def test_malformed_response_from_tribunal(self, config):
        """HYPOTHESIS: Malformed response raises appropriate error."""
        from pydantic import ValidationError
        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            # Missing required fields
            mock_eval.return_value = {"decision": "PASS"}  # Missing consensus_score

            with pytest.raises(ValidationError):
                await tribunal_evaluate("test log", )

    @pytest.mark.asyncio
    async def test_network_error_propagation(self, config):
        """HYPOTHESIS: Network errors propagate correctly."""
        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            import httpx
            mock_eval.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(httpx.ConnectError):
                await tribunal_evaluate("test log", )

    @pytest.mark.asyncio
    async def test_trace_id_propagation(self, config, mock_tribunal_response):
        """HYPOTHESIS: Trace ID is propagated through calls."""
        trace_id = "test-trace-abc123"
        mock_tribunal_response["trace_id"] = trace_id

        with patch.object(TribunalClient, 'evaluate', new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_tribunal_response

            result = await tribunal_evaluate("test log", )

            assert result["trace_id"] == trace_id
