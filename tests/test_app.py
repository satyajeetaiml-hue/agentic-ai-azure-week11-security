"""Hermetic tests for the Week 11 HR agent (dev-identity mode)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_dev_mode():
    assert client.get("/health").json()["auth"] == "dev"


def test_requires_identity():
    r = client.post("/api/v1/hr/ask", json={"question": "vacation days?"})
    assert r.status_code == 401


def test_self_service_allowed():
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "How many vacation days do I have?"},
        headers={"X-Debug-User": "alice"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "12" in body["answer"]
    assert body["on_behalf_of"] == "alice"
    assert body["entitled"] is True


def test_least_privilege_blocks_other_user():
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "vacation days?", "target_user": "bob"},
        headers={"X-Debug-User": "alice"},
    )
    assert r.status_code == 403


def test_manager_can_read_reports():
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "vacation days?", "target_user": "bob"},
        headers={"X-Debug-User": "carol", "X-Debug-Roles": "manager"},
    )
    assert r.status_code == 200
    assert "5" in r.json()["answer"]


def test_audit_records_allowed_and_denied():
    audit = client.get("/api/v1/audit").json()["audit"]
    assert any(e["allowed"] is False for e in audit)
    assert any(e["allowed"] is True for e in audit)


def test_validation_rejects_empty():
    r = client.post("/api/v1/hr/ask", json={"question": ""}, headers={"X-Debug-User": "alice"})
    assert r.status_code == 422
