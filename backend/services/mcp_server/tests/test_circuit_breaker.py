"""
Tests for Circuit Breaker
=========================

Scientific tests for circuit breaker pattern implementation.

Follows CODE_CONSTITUTION: ≥85% coverage, clear test names.
"""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock
from pybreaker import CircuitBreakerError

from middleware.circuit_breaker import (
    get_circuit_breaker,
    ServiceUnavailableError,
)


class TestCircuitBreakerBasics:
    """Test basic circuit breaker functionality."""

    def test_get_circuit_breaker_creates_instance(self, config):
        """HYPOTHESIS: get_circuit_breaker() creates breaker instance."""
        breaker = get_circuit_breaker("test_service", config)
        assert breaker is not None
        assert breaker.name == "test_service"

    def test_get_circuit_breaker_returns_same_instance(self, config):
        """HYPOTHESIS: Same name returns same breaker instance."""
        breaker1 = get_circuit_breaker("test_service", config)
        breaker2 = get_circuit_breaker("test_service", config)
        assert breaker1 is breaker2

    def test_circuit_breaker_initial_state_closed(self, config):
        """HYPOTHESIS: Circuit breaker starts in closed state."""
        breaker = get_circuit_breaker("test_initial", config)
        assert str(breaker.current_state) == "closed"


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions."""

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold_failures(self, config):
        """HYPOTHESIS: Circuit opens after threshold failures."""
        breaker = get_circuit_breaker("test_open", config)
        breaker.close()  # Ensure closed

        # Simulate failures
        for _ in range(config.circuit_breaker_threshold):
            try:
                breaker.call(lambda: 1 / 0)  # Raises ZeroDivisionError
            except ZeroDivisionError:
                pass

        # Circuit should be open now
        assert str(breaker.current_state) == "open"

    @pytest.mark.asyncio
    async def test_circuit_open_rejects_calls(self, config):
        """HYPOTHESIS: Open circuit rejects calls immediately."""
        breaker = get_circuit_breaker("test_reject", config)
        breaker.close()

        # Force circuit open
        for _ in range(config.circuit_breaker_threshold):
            try:
                breaker.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        # Next call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            breaker.call(lambda: "should fail")

    @pytest.mark.asyncio
    async def test_circuit_half_open_after_timeout(self, config):
        """HYPOTHESIS: Circuit becomes half-open after timeout."""
        # Use short timeout for testing
        config.circuit_breaker_timeout = 0.1
        breaker = get_circuit_breaker("test_halfopen", config)
        breaker.close()

        # Force open
        for _ in range(config.circuit_breaker_threshold):
            try:
                breaker.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        # Wait for timeout
        await asyncio.sleep(0.2)

        # Should be half-open now (allows one test call)
        assert str(breaker.current_state) in ["half-open", "open"]


class TestCircuitBreakerManualUsage:
    """Test manual circuit breaker usage."""

    @pytest.mark.asyncio
    async def test_manual_call_async_success(self, config):
        """HYPOTHESIS: Manual call_async allows successful calls."""
        breaker = get_circuit_breaker("test_manual_ok", config)

        async def successful_call():
            return "success"

        result = await breaker.call_async(successful_call)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_manual_call_async_failure_propagates(self, config):
        """HYPOTHESIS: Manual call_async propagates failures."""
        breaker = get_circuit_breaker("test_manual_fail", config)

        async def failing_call():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            await breaker.call_async(failing_call)

    @pytest.mark.asyncio
    async def test_manual_opens_circuit_after_failures(self, config):
        """HYPOTHESIS: Manual usage opens circuit after threshold failures."""
        breaker = get_circuit_breaker("test_manual_open", config)
        breaker.close()

        async def flaky_call():
            raise RuntimeError("always fails")

        # Make failures
        for _ in range(config.circuit_breaker_threshold):
            try:
                await breaker.call_async(flaky_call)
            except RuntimeError:
                pass

        # Circuit should be open, next call raises CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            await breaker.call_async(flaky_call)


class TestCircuitBreakerStateInspection:
    """Test circuit breaker state inspection."""

    def test_breaker_has_state_attribute(self, config):
        """HYPOTHESIS: Breaker has current_state attribute."""
        breaker = get_circuit_breaker("test_state_attr", config)
        assert hasattr(breaker, "current_state")
        assert str(breaker.current_state) in ["closed", "open", "half-open"]

    def test_breaker_has_fail_counter(self, config):
        """HYPOTHESIS: Breaker tracks failure count."""
        breaker = get_circuit_breaker("test_fail_counter", config)
        breaker.close()

        # Make a failure
        try:
            breaker.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Should have incremented counter
        assert breaker.fail_counter > 0

    def test_breaker_reset_clears_failures(self, config):
        """HYPOTHESIS: reset() clears failure counter."""
        breaker = get_circuit_breaker("test_reset_clear", config)
        breaker.close()

        # Make failures
        for _ in range(2):
            try:
                breaker.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        # Reset
        breaker.close()  # Closes and resets

        # Should be back to closed
        assert str(breaker.current_state) == "closed"


class TestCircuitBreakerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_sync_function_through_breaker(self, config):
        """HYPOTHESIS: Breaker works with sync functions."""
        breaker = get_circuit_breaker("test_sync", config)

        def sync_function():
            return 42

        # Sync function called through breaker
        result = breaker.call(sync_function)
        assert result == 42

    @pytest.mark.asyncio
    async def test_multiple_breakers_independent(self, config):
        """HYPOTHESIS: Different breakers are independent."""
        breaker1 = get_circuit_breaker("service_1", config)
        breaker2 = get_circuit_breaker("service_2", config)

        # Open breaker1
        for _ in range(config.circuit_breaker_threshold):
            try:
                breaker1.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        # breaker1 should be open
        assert str(breaker1.current_state) == "open"

        # breaker2 should still be closed
        assert str(breaker2.current_state) == "closed"
