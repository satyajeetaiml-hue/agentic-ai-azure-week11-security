"""Week 11 — Enterprise Security & Compliance: HR Self-Service Agent.

Demonstrates least-privilege agent access:

* **Identity** — requests carry an identity. In dev/mock mode it comes from
  ``X-Debug-User`` / ``X-Debug-Roles`` headers; in prod a **Microsoft Entra ID**
  bearer JWT is validated (lazy-imported).
* **On-Behalf-Of / least privilege** — the agent only returns data the signed-in
  user is entitled to; reading another employee's record requires a manager role.
* **Audit** — every access (allowed or denied) is logged.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import HTTPException, Request
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── settings ────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    azure_tenant_id: str = ""
    azure_client_id: str = ""  # API audience

    @property
    def require_auth(self) -> bool:
        """Real Entra JWT validation is enforced when tenant + client are set."""
        return bool(self.azure_tenant_id and self.azure_client_id)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ── identity ────────────────────────────────────────────────────────────
class Identity(BaseModel):
    user: str
    roles: list[str] = Field(default_factory=list)


def get_identity(request: Request) -> Identity:
    """FastAPI dependency that resolves the caller identity (Entra or dev headers)."""
    settings = get_settings()
    auth = request.headers.get("authorization")

    if settings.require_auth:
        if not auth or not auth.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing bearer token.")
        claims = _validate_entra_jwt(auth.split(" ", 1)[1])
        roles = claims.get("roles", []) or []
        return Identity(user=claims.get("preferred_username") or claims.get("sub", "unknown"), roles=roles)

    # Dev/mock mode: identity from headers (never use in production).
    user = request.headers.get("x-debug-user")
    if not user:
        raise HTTPException(status_code=401, detail="No identity. Set X-Debug-User (dev) or configure Entra.")
    roles = [r.strip() for r in request.headers.get("x-debug-roles", "").split(",") if r.strip()]
    return Identity(user=user, roles=roles)


def _validate_entra_jwt(token: str) -> dict:  # pragma: no cover - requires Entra + PyJWT
    """Validate a Microsoft Entra ID access token (signature, audience, issuer)."""
    import jwt
    from jwt import PyJWKClient

    s = get_settings()
    jwks = PyJWKClient(f"https://login.microsoftonline.com/{s.azure_tenant_id}/discovery/v2.0/keys")
    signing_key = jwks.get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience=s.azure_client_id,
        issuer=f"https://login.microsoftonline.com/{s.azure_tenant_id}/v2.0",
    )


# ── HR data + audit (Key Vault / downstream API + Purview in prod) ───────
_HR = {
    "alice": {"vacation_days": 12, "manager": "carol", "salary_band": "B"},
    "bob": {"vacation_days": 5, "manager": "carol", "salary_band": "C"},
    "carol": {"vacation_days": 20, "manager": None, "salary_band": "A"},
}
_AUDIT: list[dict] = []


def audit_log() -> list[dict]:
    return _AUDIT[-50:]


# ── schemas ─────────────────────────────────────────────────────────────
class HRRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The employee's HR question.")
    target_user: str | None = Field(default=None, description="Whose record (defaults to self).")


class HRResponse(BaseModel):
    answer: str
    acting_as: str
    on_behalf_of: str
    entitled: bool
    mode: str


# ── backend ─────────────────────────────────────────────────────────────
def answer_hr(req: HRRequest, identity: Identity) -> HRResponse:
    target = (req.target_user or identity.user).lower()
    is_self = target == identity.user.lower()
    is_manager = "manager" in identity.roles

    entitled = is_self or is_manager
    _AUDIT.append(
        {"actor": identity.user, "target": target, "action": "hr.read", "allowed": entitled}
    )
    if not entitled:
        raise HTTPException(status_code=403, detail="Least privilege: you may only access your own record.")

    record = _HR.get(target)
    if not record:
        answer = f"No HR record found for '{target}'."
    elif "vacation" in req.question.lower() or "leave" in req.question.lower():
        answer = f"{target} has {record['vacation_days']} vacation days remaining."
    elif "salary" in req.question.lower() or "pay" in req.question.lower():
        answer = f"{target}'s salary band is {record['salary_band']}."
    else:
        answer = f"I can help with leave and pay-band questions for {target}."

    return HRResponse(
        answer=answer,
        acting_as=identity.user,
        on_behalf_of=target,
        entitled=True,
        mode="entra" if get_settings().require_auth else "dev",
    )
