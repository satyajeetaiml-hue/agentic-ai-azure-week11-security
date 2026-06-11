"""Verifies the real Entra JWT validation path with a self-signed RSA key.

This exercises ``_validate_entra_jwt`` end-to-end (RS256 signature, audience and
issuer checks) — only the network JWKS lookup (`_get_signing_key`) is stubbed,
which is exactly what would hit Entra in production.
"""

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

import app.service as svc
from app.main import app

client = TestClient(app)


@pytest.fixture
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def entra(monkeypatch, rsa_key):
    """Force real-auth mode and inject our public key as the JWKS signing key."""
    settings = svc.Settings(azure_tenant_id="test-tenant", azure_client_id="api-client")
    monkeypatch.setattr(svc, "get_settings", lambda: settings)
    monkeypatch.setattr(svc, "_get_signing_key", lambda token: rsa_key.public_key())
    return settings


def _token(rsa_key, **overrides):
    claims = {
        "aud": "api://api-client",
        "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
        "preferred_username": "alice",
        "roles": [],
    }
    claims.update(overrides)
    return pyjwt.encode(claims, rsa_key, algorithm="RS256")


def test_valid_token_authenticates(entra, rsa_key):
    token = _token(rsa_key)
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "How many vacation days do I have?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "12" in r.json()["answer"]


def test_missing_bearer_rejected(entra):
    r = client.post("/api/v1/hr/ask", json={"question": "vacation?"})
    assert r.status_code == 401


def test_wrong_audience_rejected(entra, rsa_key):
    token = _token(rsa_key, aud="api://someone-else")
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "vacation?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401


def test_wrong_issuer_rejected(entra, rsa_key):
    token = _token(rsa_key, iss="https://evil.example.com/")
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "vacation?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401


def test_bad_signature_rejected(entra, rsa_key):
    # Sign with a *different* key than the one the JWKS resolver returns.
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _token(other)
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "vacation?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401


def test_app_role_grants_manager_access(entra, rsa_key):
    token = _token(rsa_key, preferred_username="carol", roles=["manager"])
    r = client.post(
        "/api/v1/hr/ask",
        json={"question": "vacation?", "target_user": "bob"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "5" in r.json()["answer"]
