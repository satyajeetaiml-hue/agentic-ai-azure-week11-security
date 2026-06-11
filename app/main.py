"""Week 11 — Enterprise Security & Compliance.

HR Self-Service Agent with least-privilege access, Entra ID identity (dev headers
in mock mode), and an audit log. Run:  uvicorn app.main:app --reload
"""

from fastapi import Depends, FastAPI

from app.service import (
    HRRequest,
    HRResponse,
    Identity,
    answer_hr,
    audit_log,
    get_identity,
    get_settings,
)

settings = get_settings()
app = FastAPI(title="Week 11 — Security (HR Least-Privilege Agent)", version="0.2.0")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "week": "11", "auth": "entra" if settings.require_auth else "dev"}


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": "agentic-ai-azure-week11-security",
        "endpoint": "/api/v1/hr/ask",
        "auth": "entra" if settings.require_auth else "dev",
        "docs": "/docs",
    }


@app.post("/api/v1/hr/ask", response_model=HRResponse, tags=["week11"])
def hr_ask(payload: HRRequest, identity: Identity = Depends(get_identity)) -> HRResponse:
    """Answer HR questions, enforcing least-privilege on whose record is read."""
    return answer_hr(payload, identity)


@app.get("/api/v1/audit", tags=["week11"])
def audit() -> dict:
    """Audit trail of accesses (allowed and denied)."""
    return {"audit": audit_log()}
