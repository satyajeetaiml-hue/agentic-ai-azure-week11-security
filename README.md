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

## ☁️ Wire the real Entra ID backend

The Entra JWT validation is **real and verified** — `tests/test_jwt.py` exercises the full
signature/audience/issuer/expiry path with a self-signed key (only the JWKS network lookup is stubbed).
To enforce it against a live tenant:

### 1. Register the API app (Azure CLI)
```bash
az login
# Create an app registration for THIS API
az ad app create --display-name "hr-agent-api" --sign-in-audience AzureADMyOrg
APP_ID=$(az ad app list --display-name "hr-agent-api" --query "[0].appId" -o tsv)

# Expose an API + an app role used for least privilege
az ad app update --id $APP_ID --identifier-uris "api://$APP_ID"
# In the portal (App registrations → App roles) add an app role "manager" (value: manager),
# or define it via the app manifest. Assign it to users/groups under Enterprise applications.
```
Note your **tenant id** (`az account show --query tenantId -o tsv`) and `$APP_ID`.

### 2. Configure `.env`
```
AZURE_TENANT_ID=<tenant-guid>
AZURE_CLIENT_ID=<APP_ID>
# Optional overrides:
# AZURE_API_AUDIENCE=api://<APP_ID>      # default
# AZURE_ISSUER=https://login.microsoftonline.com/<tenant>/v2.0   # default (v2 tokens)
```
> **Common gotcha:** if your access tokens are **v1.0** (default unless the manifest sets
> `accessTokenAcceptedVersion: 2`), set `AZURE_ISSUER=https://sts.windows.net/<tenant>/` and the audience
> to the GUID. The validator reports the exact mismatch in the 401 detail.

### 3. Run — now Entra-enforced
```bash
uvicorn app.main:app --reload   # GET /health -> "auth": "entra"
```
The `X-Debug-*` headers are now ignored; requests must carry `Authorization: Bearer <token>`. App roles in
the token's `roles` claim drive least-privilege (a `manager` role can read reports).

### 4. Get a token to test
```bash
# Client-credentials example (app-only); for user OBO use the on-behalf-of flow.
az account get-access-token --resource "api://<APP_ID>" --query accessToken -o tsv
```
Then: `curl -H "Authorization: Bearer <token>" ...`. Next step in the lab is **OAuth2 On-Behalf-Of** so
downstream tools run with the user's identity, with all secrets in **Key Vault** + Managed Identity.

## 🏗️ Architect's lens
- Identity boundaries: app vs. user vs. tool identity.
- Data-exfiltration & prompt-injection defenses (tool allow-lists, output filtering).
- RBAC + Conditional Access; private networking (Private Endpoints, VNet).
- Audit/compliance: who did what, retention, Microsoft Purview lineage.

## 📁 Structure
```
app/service.py       # settings, identity dependency, Entra JWT validation, least-privilege + audit
app/main.py          # /api/v1/hr/ask (Depends(get_identity)) + /api/v1/audit
tests/test_app.py    # dev-identity mode (headers)
tests/test_jwt.py    # real Entra JWT validation (self-signed key, JWKS stubbed)
```

## 🧰 Tech stack
Microsoft Entra ID, OAuth2/OBO, MSAL, PyJWT, Key Vault, Managed Identity, Content Safety, Purview.

## 🗺️ Series
Prev: [Week 10](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week10-observability) ·
Next: [Week 12 — Capstone](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week12-capstone) ·
[All labs](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure)

## 📄 License
MIT — see [`LICENSE`](LICENSE).
