# Week 11 — Enterprise Security & Compliance

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week11-security/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week11-security/actions/workflows/ci.yml)

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class*.
> Course hub: [azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass).

---

## 🎯 Learning goal
Secure agents with identity, RBAC, **least privilege**, and audit.

## 🏢 Enterprise use case — "HR Self-Service Agent with Least Privilege" (Enterprise / Public Sector)
Employees ask about benefits/payroll. The agent acts **on behalf of** the signed-in user, so it only sees
data that user is entitled to. All accesses are audited.

## ✅ What this repo implements
- **Identity** — a FastAPI dependency resolves the caller. Dev mode uses `X-Debug-User`/`X-Debug-Roles`
  headers; prod validates a **Microsoft Entra ID** bearer JWT (signature/audience/issuer, lazy-imported).
- **Least privilege (OBO)** — you can read your own record; reading another employee's requires a
  `manager` role, else **403**.
- **Audit** — every access (allowed or denied) is logged at `GET /api/v1/audit`.

## 🚀 Quick start (dev identity mode)
```bash
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
```bash
# Self-service (allowed)
curl -X POST http://127.0.0.1:8000/api/v1/hr/ask \
  -H "Content-Type: application/json" -H "X-Debug-User: alice" \
  -d '{"question": "How many vacation days do I have?"}'

# Another employee without manager role -> 403
curl -X POST http://127.0.0.1:8000/api/v1/hr/ask \
  -H "Content-Type: application/json" -H "X-Debug-User: alice" \
  -d '{"question": "vacation?", "target_user": "bob"}'

# Manager (allowed)
curl -X POST http://127.0.0.1:8000/api/v1/hr/ask \
  -H "Content-Type: application/json" -H "X-Debug-User: carol" -H "X-Debug-Roles: manager" \
  -d '{"question": "vacation?", "target_user": "bob"}'
```
Run tests: `pytest -q`

## ☁️ Enforce Entra ID
Set `AZURE_TENANT_ID` + `AZURE_CLIENT_ID`. Requests must then carry a valid `Authorization: Bearer <jwt>`;
the dev headers are ignored. Implement **OAuth2 On-Behalf-Of** so downstream tools run with the user's
identity, and keep secrets in **Key Vault** + Managed Identity.

## 🏗️ Architect's lens
- Identity boundaries: app vs. user vs. tool identity.
- Data-exfiltration & prompt-injection defenses (tool allow-lists, output filtering).
- RBAC + Conditional Access; private networking (Private Endpoints, VNet).
- Audit/compliance: who did what, retention, Microsoft Purview lineage.

## 🧰 Tech stack
Microsoft Entra ID, OAuth2/OBO, MSAL, PyJWT, Key Vault, Managed Identity, Content Safety, Purview.

## 🗺️ Series
Prev: [Week 10](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week10-observability) ·
Next: [Week 12 — Capstone](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week12-capstone) ·
[All labs](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure)

## 📄 License
MIT — see [`LICENSE`](LICENSE).
