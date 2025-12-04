"""
Tests for FastAPI Application
==============================

Integration tests for main.py FastAPI app.

Follows CODE_CONSTITUTION: ≥85% coverage, clear test names.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_returns_ok(self):
        """HYPOTHESIS: /health returns 200 with status ok."""
        from main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data


class TestMetricsEndpoint:
    """Test metrics endpoint."""

    def test_metrics_returns_stats(self):
        """HYPOTHESIS: /metrics returns circuit breaker stats."""
        from main import app

        client = TestClient(app)
        response = client.get("/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "circuit_breakers" in data


class TestAppStartup:
    """Test app startup."""

    def test_app_imports_successfully(self):
        """HYPOTHESIS: App can be imported without errors."""
        from main import app

        assert app is not None
        assert app.title == "MAXIMUS MCP Server"
