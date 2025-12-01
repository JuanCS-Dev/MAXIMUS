"""
Unit tests for API routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any

from backend.services.meta_orchestrator.api.routes import app
from backend.services.meta_orchestrator.core.orchestrator import Orchestrator
from backend.services.meta_orchestrator.core.agent_registry import AgentRegistry
from backend.services.meta_orchestrator.plugins.base import TaskResult, TaskStatus, AgentPluginMetadata, AgentPlugin

client = TestClient(app)

@pytest.fixture
def mock_dependencies():
    with patch("backend.services.meta_orchestrator.api.routes.orchestrator") as mock_orch, \
         patch("backend.services.meta_orchestrator.api.routes.registry") as mock_reg:
        
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
        
        # Setup orchestrator
        mock_result = TaskResult(
            task_id="1",
            status=TaskStatus.COMPLETED,
            output={"result": "success"}
        )
        mock_orch.execute_mission = AsyncMock(return_value=mock_result)
        
        yield mock_orch, mock_reg

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_execute_mission(mock_dependencies):
    payload = {
        "type": "test",
        "description": "Test mission",
        "context": {}
    }
    response = client.post("/v1/missions", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_list_agents(mock_dependencies):
    response = client.get("/v1/agents")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_all_agents_health(mock_dependencies):
    response = client.get("/v1/agents/health/all")
    assert response.status_code == 200
    assert response.json()["test_agent"]["healthy"] is True
