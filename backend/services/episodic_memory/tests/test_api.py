"""
Unit tests for Episodic Memory API.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.routes import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_store_memory():
    payload = {
        "content": "API test memory",
        "type": "fact",
        "context": {"test": True}
    }
    response = client.post("/v1/memories", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "API test memory"
    assert "memory_id" in data

def test_search_memories():
    # First store a memory
    client.post("/v1/memories", json={
        "content": "Searchable memory",
        "type": "fact"
    })
    
    # Then search
    payload = {
        "query_text": "searchable",
        "limit": 5
    }
    response = client.post("/v1/memories/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] >= 1
    assert data["memories"][0]["content"] == "Searchable memory"

def test_get_and_delete_memory():
    # Store
    response = client.post("/v1/memories", json={
        "content": "To delete",
        "type": "fact"
    })
    memory_id = response.json()["memory_id"]
    
    # Get
    response = client.get(f"/v1/memories/{memory_id}")
    assert response.status_code == 200
    assert response.json()["content"] == "To delete"
    
    # Delete
    response = client.delete(f"/v1/memories/{memory_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify deleted
    response = client.get(f"/v1/memories/{memory_id}")
    assert response.status_code == 404
