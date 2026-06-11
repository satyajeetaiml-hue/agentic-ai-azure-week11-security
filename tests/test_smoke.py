"""Smoke tests for Week 11 — Enterprise Security & Compliance."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_endpoint_accepts_input():
    r = client.post("/api/v1/hr/ask", json={"question": "How many vacation days do I have left this year?"})
    assert r.status_code == 200


def test_endpoint_rejects_empty():
    r = client.post("/api/v1/hr/ask", json={"question": ""})
    assert r.status_code == 422
