from fastapi.testclient import TestClient
from healthmon import app, proxy_stats
import pytest

# FILE: healthmon/test_main.py

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_proxy_stats():
    proxy_stats["requests_served"] = 0
    proxy_stats["success_count"] = 0
    proxy_stats["failure_count"] = 0

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_stats_initial():
    response = client.get("/stats")
    assert response.status_code == 200
    assert response.json() == {"requests_served": 1, "success_count": 0, "failure_count": 0}

def test_update_stats_success():
    response = client.post("/update_stats", json={"status": "success"})
    assert response.status_code == 200
    assert response.json() == {"message": "Stats updated"}
    assert proxy_stats["success_count"] == 1

def test_update_stats_failure():
    response = client.post("/update_stats", json={"status": "failure"})
    assert response.status_code == 200
    assert response.json() == {"message": "Stats updated"}
    assert proxy_stats["failure_count"] == 1

def test_track_requests_middleware():
    initial_requests_served = proxy_stats["requests_served"]
    client.get("/health")
    assert proxy_stats["requests_served"] == initial_requests_served + 1