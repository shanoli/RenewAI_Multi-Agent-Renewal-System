# 🛡️ RenewAI — Multi-Agent Policy Renewal System

**Project RenewAI** is an agentic AI system for Suraksha Life Insurance that manages the full renewal communication lifecycle across Email, WhatsApp, and Voice channels using LangGraph + Gemini 2.5 Flash Lite.

---

## 🏗️ Architecture

```
FastAPI (Async)
    ↓
LangGraph Stateful Graph
    ↓
[Step 1] Orchestrator → selects best channel
    ↓
[Step 2] Critique A → verifies channel selection (evidence-based)
    ↓
[Step 3] Planner → builds execution plan (RAG-powered)
    ↓
[Step 4a] Greeting/Closing Agent  ← PARALLEL →  [Step 4b] Draft Agent
    ↓
[Step 5] Critique B → compliance & quality check
    ↓
[Step 6] Channel Agent: Email | WhatsApp | Voice
    ↓  (escalation at any step)
Escalation Manager → Human Queue
    ↓
SQLite (state + interactions + audit)
Chroma (policy_documents, objection_library, regulatory_guidelines)
```

---

## 🚀 Quick Start

### 1. Prerequisites
```bash
Python 3.11+
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY
```

### 3. Setup Database + RAG
```bash
python scripts/setup.py
```

### 4. Start Server
```bash
uvicorn app.main:app --reload
```

### 5. Open Swagger UI
```
http://localhost:8000/docs
```

---

## 🔑 Authentication

JWT login with **email as primary key**.

**Default credentials (after setup):**
| Role    | Email                    | Password     |
|---------|--------------------------|--------------|
| admin   | admin@renewai.com        | admin123     |
| agent   | agent1@renewai.com       | agent123     |
| manager | manager@renewai.com      | manager123   |

**Login flow:**
1. `POST /auth/login` → get JWT token
2. Click **Authorize** in Swagger → paste `Bearer <token>`

---

## 📁 Project Structure

```
renewai/
├── app/
│   ├── main.py                    # FastAPI entrypoint
│   ├── core/
│   │   ├── config.py              # Settings from .env
│   │   ├── security.py            # JWT auth
│   │   └── gemini_client.py       # Gemini 2.5 Flash Lite client
│   ├── db/
│   │   └── database.py            # SQLite init + schema
│   ├── rag/
│   │   └── chroma_store.py        # Chroma + hybrid search + reranking
│   ├── agents/
│   │   ├── state.py               # LangGraph RenewalState
│   │   ├── workflow.py            # LangGraph graph definition
│   │   ├── orchestrator.py        # Step 1: Channel selection
│   │   ├── critique_a.py          # Step 2: Evidence-based verification
│   │   ├── planner.py             # Step 3: Execution plan (RAG)
│   │   ├── greeting_closing.py    # Step 4a: Cultural greeting/closing
│   │   ├── draft_agent.py         # Step 4b: Channel-specific draft
│   │   ├── critique_b.py          # Step 5: Compliance review
│   │   ├── escalation.py          # Human queue manager
│   │   └── channels/
│   │       ├── email_agent.py     # Email send (modular)
│   │       ├── whatsapp_agent.py  # WhatsApp send (modular)
│   │       └── voice_agent.py     # Voice/IVR send (modular)
│   └── api/
│       ├── auth.py                # JWT login/register
│       ├── renewal.py             # Renewal workflow endpoints
│       └── dashboard.py           # Metrics, escalations, audit
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   ├── test_email_agent.py        # Email channel tests
│   ├── test_whatsapp_agent.py     # WhatsApp channel tests
│   ├── test_voice_agent.py        # Voice channel tests
│   └── test_all_scenarios.py      # All problem statement scenarios
├── scripts/
│   ├── setup.py                   # One-shot setup
│   ├── populate_data.py           # SQLite data population
│   └── populate_rag.py            # Chroma RAG population
├── data/                          # Auto-created (DB files)
├── .env                           # Your secrets (not in git)
├── .env.example                   # Template
├── requirements.txt
└── pytest.ini
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint         | Description          |
|--------|------------------|----------------------|
| POST   | /auth/register   | Register new user    |
| POST   | /auth/login      | Get JWT token        |

### Renewal Workflow
| Method | Endpoint                        | Description                      |
|--------|---------------------------------|----------------------------------|
| POST   | /renewal/trigger                | Start renewal for a policy       |
| POST   | /renewal/webhook/inbound        | Inbound customer reply           |
| GET    | /renewal/status/{policy_id}     | Get policy renewal status        |

### Dashboard
| Method | Endpoint                            | Description                    |
|--------|-------------------------------------|--------------------------------|
| GET    | /dashboard/overview                 | Operations summary             |
| GET    | /dashboard/escalations              | Open escalation queue          |
| PATCH  | /dashboard/escalations/{id}/resolve | Resolve escalation case        |
| GET    | /dashboard/audit-logs/{policy_id}   | IRDAI-ready audit trail        |
| GET    | /dashboard/customers                | Customer list with segment     |

---

## 🧪 Running Tests

```bash
# All tests
pytest

# Individual agent tests
pytest tests/test_email_agent.py -v
pytest tests/test_whatsapp_agent.py -v
pytest tests/test_voice_agent.py -v

# Full scenario tests
pytest tests/test_all_scenarios.py -v
```

> ⚠️ Note: Tests for orchestrator/planner/draft agents make real Gemini API calls. Ensure GEMINI_API_KEY is set in .env.

---

## 🔧 Modular Channel Development

Each channel agent is **fully independent** in `app/agents/channels/`:

```python
# To extend Email agent independently:
# app/agents/channels/email_agent.py

async def email_send_node(state: RenewalState) -> dict:
    # Add SendGrid/SES/Mailgun integration here
    # Access state["final_message"] for the assembled message
    ...
```

Channels share the same `RenewalState` input/output contract but are otherwise completely decoupled.

---

## 🛢️ Database Schema

SQLite tables: `users`, `customers`, `policies`, `policy_state`, `interactions`, `escalation_cases`, `audit_logs`

Chroma collections: `policy_documents`, `objection_library`, `regulatory_guidelines`

---

## 🔐 Security

- JWT tokens (HS256, configurable expiry)
- Email as primary key (no sequential IDs)
- All escalation cases SLA-tracked
- Audit logs retained per IRDAI 7-year requirement

---

## 🌍 Languages Supported

English, Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Urdu
