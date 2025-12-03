"""
Unit tests for API routes.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any

from api.routes import app, MissionRequest, MissionResponse, AgentInfo
from core.orchestrator import Orchestrator
from core.agent_registry import AgentRegistry
from plugins.base import TaskResult, TaskStatus, AgentPluginMetadata, AgentPlugin

client = TestClient(app)


@pytest.fixture
def mock_dependencies():
    """Fixture to mock orchestrator and registry."""
    with patch("api.routes.orchestrator") as mock_orch, \
         patch("api.routes.registry") as mock_reg:

        # Setup registry
        mock_reg.list_agents = AsyncMock(return_value=[{
            "name": "test_agent",
            "version": "1.0.0",
            "enabled": True,
            "capabilities": ["test"],
            "description": "Test agent",
            "stats": {}
        }])
        mock_reg.health_check_all = AsyncMock(return_value={"test_agent": {"healthy": True}})
        mock_reg.get_agent = AsyncMock(return_value=None)

        # Setup orchestrator
        mock_result = TaskResult(
            task_id="1",
            status=TaskStatus.COMPLETED,
            output={"result": "success"}
        )
        mock_orch.execute_mission = AsyncMock(return_value=mock_result)

        yield mock_orch, mock_reg


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self):
        """Test health check returns healthy."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "meta-orchestrator"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data


class TestMissionEndpoint:
    """Tests for mission execution endpoint."""

    def test_execute_mission_success(self, mock_dependencies):
        """Test successful mission execution."""
        payload = {
            "type": "test",
            "description": "Test mission",
            "context": {}
        }

        response = client.post("/v1/missions", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_execute_mission_with_priority(self, mock_dependencies):
        """Test mission execution with priority."""
        payload = {
            "type": "test",
            "description": "Test mission",
            "context": {},
            "priority": "high"
        }

        response = client.post("/v1/missions", json=payload)

        assert response.status_code == 200

    def test_execute_mission_with_critical_priority(self, mock_dependencies):
        """Test mission execution with critical priority."""
        payload = {
            "type": "test",
            "description": "Critical mission",
            "context": {},
            "priority": "critical"
        }

        response = client.post("/v1/missions", json=payload)

        assert response.status_code == 200

    def test_execute_mission_with_low_priority(self, mock_dependencies):
        """Test mission execution with low priority."""
        payload = {
            "type": "test",
            "description": "Low priority mission",
            "context": {},
            "priority": "low"
        }

        response = client.post("/v1/missions", json=payload)

        assert response.status_code == 200

    def test_execute_mission_with_context(self, mock_dependencies):
        """Test mission execution with context."""
        payload = {
            "type": "infrastructure",
            "description": "Deploy service",
            "context": {"env": "production", "region": "us-east-1"}
        }

        response = client.post("/v1/missions", json=payload)

        assert response.status_code == 200

    def test_execute_mission_no_orchestrator(self):
        """Test mission execution when orchestrator not initialized."""
        with patch("api.routes.orchestrator", None):
            payload = {
                "type": "test",
                "description": "Test mission",
                "context": {}
            }

            response = client.post("/v1/missions", json=payload)

            assert response.status_code == 503
            assert "not initialized" in response.json()["detail"]

    def test_execute_mission_orchestrator_error(self, mock_dependencies):
        """Test mission execution when orchestrator raises error."""
        mock_orch, _ = mock_dependencies
        mock_orch.execute_mission = AsyncMock(side_effect=Exception("Execution error"))

        payload = {
            "type": "test",
            "description": "Test mission",
            "context": {}
        }

        response = client.post("/v1/missions", json=payload)

        assert response.status_code == 500

    def test_execute_mission_invalid_payload(self):
        """Test mission execution with invalid payload."""
        payload = {"invalid": "data"}

        response = client.post("/v1/missions", json=payload)

        assert response.status_code == 422


class TestAgentsEndpoint:
    """Tests for agents endpoint."""

    def test_list_agents(self, mock_dependencies):
        """Test listing all agents."""
        response = client.get("/v1/agents")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "test_agent"

    def test_list_agents_enabled_only(self, mock_dependencies):
        """Test listing enabled agents only."""
        response = client.get("/v1/agents?enabled_only=true")

        assert response.status_code == 200

    def test_list_agents_no_registry(self):
        """Test listing agents when registry not initialized."""
        with patch("api.routes.registry", None):
            response = client.get("/v1/agents")

            assert response.status_code == 503
            assert "not initialized" in response.json()["detail"]


class TestAgentHealthEndpoint:
    """Tests for agent health endpoints."""

    def test_all_agents_health(self, mock_dependencies):
        """Test health check for all agents."""
        response = client.get("/v1/agents/health/all")

        assert response.status_code == 200
        data = response.json()
        assert "test_agent" in data
        assert data["test_agent"]["healthy"] is True

    def test_all_agents_health_no_registry(self):
        """Test all agents health when registry not initialized."""
        with patch("api.routes.registry", None):
            response = client.get("/v1/agents/health/all")

            assert response.status_code == 503

    def test_specific_agent_health(self, mock_dependencies):
        """Test health check for specific agent."""
        _, mock_reg = mock_dependencies
        mock_agent = MagicMock()
        mock_agent.health_check = AsyncMock(return_value={"healthy": True})
        mock_reg.get_agent = AsyncMock(return_value=mock_agent)

        response = client.get("/v1/agents/test_agent/health")

        assert response.status_code == 200
        assert response.json()["healthy"] is True

    def test_specific_agent_health_not_found(self, mock_dependencies):
        """Test health check for nonexistent agent."""
        response = client.get("/v1/agents/nonexistent/health")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_specific_agent_health_error(self, mock_dependencies):
        """Test health check when agent health check fails."""
        _, mock_reg = mock_dependencies
        mock_agent = MagicMock()
        mock_agent.health_check = AsyncMock(side_effect=Exception("Health check error"))
        mock_reg.get_agent = AsyncMock(return_value=mock_agent)

        response = client.get("/v1/agents/error_agent/health")

        assert response.status_code == 200
        data = response.json()
        assert data["healthy"] is False
        assert "error" in data

    def test_specific_agent_health_no_registry(self):
        """Test specific agent health when registry not initialized."""
        with patch("api.routes.registry", None):
            response = client.get("/v1/agents/test_agent/health")

            assert response.status_code == 503


class TestModels:
    """Tests for Pydantic models."""

    def test_mission_request_defaults(self):
        """Test MissionRequest default values."""
        request = MissionRequest(type="test", description="Test")

        assert request.context == {}
        assert request.priority == "medium"

    def test_mission_response(self):
        """Test MissionResponse model."""
        response = MissionResponse(
            mission_id="123",
            status="completed",
            output={"result": "success"},
            reasoning="Test reasoning",
            confidence=0.9,
            execution_time_ms=100,
            errors=[]
        )

        assert response.mission_id == "123"
        assert response.status == "completed"
        assert response.confidence == 0.9

    def test_agent_info(self):
        """Test AgentInfo model."""
        info = AgentInfo(
            name="test_agent",
            version="1.0.0",
            enabled=True,
            capabilities=["test"],
            description="Test agent",
            stats={}
        )

        assert info.name == "test_agent"
        assert info.enabled is True
