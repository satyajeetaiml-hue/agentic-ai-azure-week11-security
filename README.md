# Week 11 — Enterprise Security & Compliance

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week11-security/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week11-security/actions/workflows/ci.yml)

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class* (12 weeks).
> Each lab is an independent, runnable FastAPI starter. Part of the
> [course series](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure).

---

## 🎯 Learning goal
Secure agents with identity, RBAC, OAuth2/OBO, secrets, and compliance guardrails.

## 🏢 Enterprise use case — "HR Self-Service Agent with Least Privilege" (Enterprise / Public Sector)
Employees ask about benefits/payroll. The agent acts on behalf of the signed-in user (OBO flow), so it only sees data that user is entitled to. All secrets live in Key Vault; all calls are audited.

---

## 🧪 What you'll build (lab)
1. Protect FastAPI with **Microsoft Entra ID** (JWT validation, scopes/roles).
2. Implement **OAuth2 On-Behalf-Of** so tools run with the user's identity.
3. Move all secrets to **Key Vault** + **Managed Identity**; add input/output compliance filters.
4. Add tool allow-lists and output filtering as prompt-injection defenses.

> This starter ships with a **runnable mock** of the endpoint so you can run and test
> immediately, then progressively replace the mock with the real Azure implementation.

## 🏗️ Architect's lens
- Identity boundaries: app identity vs. user identity vs. tool identity.
- Data exfiltration & prompt-injection defenses (tool allow-lists, output filtering).
- RBAC + Conditional Access; private networking (Private Endpoints, VNet integration).
- Audit/compliance: who did what, retention, Microsoft Purview lineage.

## 🧰 Tech stack
Microsoft Entra ID, OAuth2/OBO, MSAL, Azure Key Vault, Managed Identity, Private Endpoints/VNet, Azure Content Safety, Microsoft Purview.

---

## 🚀 Quick start

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) copy the env template — runs in MOCK mode without it
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# 4. Run the API
uvicorn app.main:app --reload
```

Open the interactive docs at **http://127.0.0.1:8000/docs**.

### Try the endpoint
```bash
curl -X POST http://127.0.0.1:8000/api/v1/hr/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I have left this year?"}'
```

### Run the tests
```bash
pytest -q
```

### Run with Docker
```bash
docker build -t agentic-ai-azure-week11-security .
docker run -p 8000:8000 agentic-ai-azure-week11-security
```

---

## 📁 Project structure
```
agentic-ai-azure-week11-security/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI app + the /api/v1/hr/ask endpoint
├── tests/
│   └── test_smoke.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗺️ Where this fits
This repo covers **Week 11 — Enterprise Security & Compliance**. The full 12-week path and reference architecture
live in the master-class companion repo:
**[azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass)**.

## 📄 License
MIT — see [`LICENSE`](LICENSE).
