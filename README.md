# AIVOA – AI-Powered Customer Complaint Management System

An AI-native Customer Complaint module for a pharmaceutical Quality Management
System (QMS). The **left panel** is a read-only "Log Customer Complaint" form;
the **right panel** is the **AIVOA Copilot**, an AI assistant you talk to in
plain English (or hand a PDF/email to) that fills and edits the form for you
and produces an AI Risk Assessment alongside it.

Built for the AIVOA Round 1 Full Stack Developer Assessment.

---

## 1. What this demonstrates

| Assignment requirement | Where it lives |
|---|---|
| React + Redux frontend | `frontend/src` (`@reduxjs/toolkit`, `react-redux`) |
| FastAPI backend | `backend/app/main.py` + `backend/app/api/*` |
| LangGraph agent | `backend/app/langgraph_agent/graph.py` |
| Groq LLM (`gemma2-9b-it`) | `backend/app/langgraph_agent/llm_client.py` |
| Postgres/MySQL (SQLAlchemy) | `backend/app/models.py`, `backend/app/database.py` |
| Google Inter font | `frontend/public/index.html` |
| **Log Complaint tool** | Natural-language chat → new complaint |
| **Edit Complaint tool** | Natural-language chat → updates existing complaint, preserves everything else |
| **Document Extraction tool** | Upload a PDF/email → same extraction + risk pipeline |

The form on the left is intentionally **read-only**. Every field is written
by the AI Copilot, never typed directly — this was a hard requirement in the
assessment brief and is enforced in the UI (`ComplaintForm.jsx` renders
`readOnly` inputs).

---

## 2. Architecture

```
┌──────────────────────────┐        HTTP/JSON        ┌────────────────────────────┐
│   React + Redux (SPA)    │  ───────────────────▶   │   FastAPI backend          │
│                           │                          │                            │
│  ComplaintForm (left)     │  ◀───────────────────   │  /api/chat                 │
│  CopilotChat (right)      │      complaint JSON      │  /api/upload/document      │
│  RiskAssessment card      │                          │  /api/complaints/*         │
└──────────────────────────┘                          └─────────────┬──────────────┘
                                                                       │
                                                                       ▼
                                                      ┌────────────────────────────┐
                                                      │  LangGraph Agent            │
                                                      │                            │
                                                      │  classify_intent           │
                                                      │        │                   │
                                                      │        ▼                   │
                                                      │  extract_and_merge  ───▶ Groq (gemma2-9b-it)
                                                      │        │                   │
                                                      │        ▼                   │
                                                      │  risk_assessment    ───▶ Groq (gemma2-9b-it)
                                                      │        │                   │
                                                      │        ▼                   │
                                                      │  compose_reply      ───▶ Groq (gemma2-9b-it)
                                                      └─────────────┬──────────────┘
                                                                       │
                                                                       ▼
                                                      ┌────────────────────────────┐
                                                      │  Postgres / MySQL /         │
                                                      │  SQLite (dev default)       │
                                                      │  complaints, chat_messages  │
                                                      └────────────────────────────┘
```

### Why one graph handles all three "tools"

`log_complaint`, `edit_complaint`, and `document_extraction` are really the
**same pipeline** — extract structured fields from unstructured text, merge
them into whatever complaint state already exists, then reason about risk —
just triggered from a different entry point:

- **Log Complaint tool**: user types a fresh description → `is_new_complaint=True`
  → the router sends it straight to `log_complaint`.
- **Edit Complaint tool**: user sends a follow-up message on an existing
  complaint → an LLM-based intent classifier decides `edit_complaint` vs.
  idle chat → the extraction node is given the **previous form state** and
  told to overwrite only fields the new message actually mentions.
- **Document Extraction tool**: the `/api/upload/document` endpoint pulls
  text out of a PDF/email/txt file with `pypdf`, then feeds that text into
  the exact same graph with `source_channel="document"`. After extraction,
  the resulting complaint can still be edited via chat, exactly like the
  "sorry, the batch number is CHG260712A…" example in the brief.

This keeps the "preserve everything else" behavior (a hard requirement) in
one place instead of three separate, divergent code paths.

### LangGraph node breakdown

| Node | Responsibility |
|---|---|
| `classify_intent` | Decides `log_complaint` / `edit_complaint` / `general_chat` (document uploads skip this and are routed directly) |
| `extract_and_merge` | LLM extracts structured fields as JSON; merged with the previous form state so unmentioned fields are preserved |
| `risk_assessment` | LLM reasons over the current merged complaint and produces severity, risk category, recommended next action, CAPA suggestion, and a short reasoning summary |
| `compose_reply` | LLM writes the short natural-language confirmation shown back in the chat bubble |

State is a single `AgentState` TypedDict (`backend/app/langgraph_agent/state.py`)
threaded through all four nodes — see the diagram in that file's docstring
(`graph.py`) for the exact edges.

---

## 3. Tech stack

- **Frontend**: React 18, Redux Toolkit, react-redux, axios, Google Inter / JetBrains Mono
- **Backend**: FastAPI, SQLAlchemy, Pydantic v2, pypdf
- **AI**: LangGraph, Groq (`gemma2-9b-it`, with `llama-3.3-70b-versatile` available as a configurable fallback)
- **Database**: Postgres or MySQL in production; SQLite by default for a zero-setup local demo

---

## 4. Setup

### 4.1 Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set GROQ_API_KEY (create one at https://console.groq.com)
# DATABASE_URL defaults to a local SQLite file — fine for the demo.
# For Postgres/MySQL, see the comments in .env.example.

uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000` (interactive docs at `/docs`).
Tables are created automatically on first run via `Base.metadata.create_all`.

### 4.2 Frontend

```bash
cd frontend
npm install
cp .env.example .env    # REACT_APP_API_BASE defaults to http://localhost:8000
npm start
```

The app opens at `http://localhost:3000`.

### 4.3 Try it

1. **Log Complaint tool** — in the Copilot chat, type:
   > Apollo pharmacy reported discolored capsules in amoxicillin capsules 500mg

   The left form fills in (customer, product, strength, complaint type,
   description, date), and the Risk Assessment card above the chat populates
   with a severity, category, next action, and CAPA suggestion.

2. **Edit Complaint tool** — follow up with:
   > sorry, the batch number is BMX240602, and the affected quantity is 48 capsules

   Only `batch_number` and `affected_quantity` change; everything else
   (product name, severity, etc.) is preserved.

3. **Document Extraction tool** — click the 📎 icon and upload
   `sample_data/sample_complaint_letter.pdf` (a realistic Metformin
   Hydrochloride API contamination complaint) or
   `sample_data/sample_complaint_email.txt` (an Ibuprofen blister-seal
   complaint email). The form and risk assessment populate from the document.
   You can then correct it via chat, e.g.:
   > sorry, the batch number is CHG260712A and affected quantity is 50 kg, 2 HDPE drums

4. Click **+ New Complaint** in the header to start a fresh session.

---

## 5. API reference

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/chat` | Log or edit a complaint via natural language. Body: `{ message, complaint_id }` (`complaint_id: null` starts a new complaint) |
| `POST` | `/api/upload/document` | Document extraction tool. Multipart form: `file`, optional `complaint_id` |
| `GET` | `/api/complaints` | List all complaints |
| `GET` | `/api/complaints/{id}` | Fetch one complaint |
| `GET` | `/api/complaints/{id}/messages` | Full chat history for a complaint |

Full interactive schema at `http://localhost:8000/docs`.

---

## 6. Design decisions

- **Merge-not-overwrite extraction**: the extraction prompt is explicitly
  instructed to keep previous field values when the new message doesn't
  mention them, and the backend does a second defensive merge pass so a
  malformed/partial LLM response can never silently null out existing data.
- **Read-only form**: enforces the "don't fill the form manually" requirement
  at the UI layer, not just as a suggestion.
- **Same graph for chat and documents**: avoids duplicating the
  extraction/merge/risk logic for the document-extraction tool.
- **SQLite default, Postgres/MySQL-ready**: `DATABASE_URL` is the only thing
  that changes — SQLAlchemy handles the rest — so the assessment stack
  requirement (Postgres/MySQL) is honored while keeping first-run setup to
  zero external services.
- **gemma2-9b-it doesn't support strict JSON mode** on Groq, so
  `llm_client.py` instructs the model firmly in-prompt and defensively
  parses/repairs the response (strips markdown fences, regex-extracts the
  first `{...}` block) rather than assuming perfectly formed JSON every time.

---

## 7. Possible extensions (not implemented)

The brief calls these out as optional bonus features. The architecture makes
each of these an additional LangGraph node reading from the same
`AgentState`/DB, so they'd slot in without restructuring:

- **Duplicate Complaint Detection** — embed/compare new complaints against
  open ones on `product_name` + `batch_number` + `complaint_type`.
- **Complaint Completeness Checker** — a node that flags which fields are
  still missing and prompts the user for them.
- **Complaint Summary** — a condensed executive summary for QA review, generated
  from the full field set + chat history.

---

## 8. Project structure

```
aivoa-complaint-system/
├── backend/
│   ├── app/
│   │   ├── main.py               FastAPI app, CORS, router registration
│   │   ├── config.py             env-based settings
│   │   ├── database.py           SQLAlchemy engine/session
│   │   ├── models.py             Complaint, ChatSession, ChatMessage
│   │   ├── schemas.py            Pydantic request/response models
│   │   ├── api/
│   │   │   ├── chat.py           /api/chat (log + edit tools)
│   │   │   ├── upload.py         /api/upload/document (extraction tool)
│   │   │   └── complaints.py     read endpoints
│   │   └── langgraph_agent/
│   │       ├── state.py          AgentState TypedDict
│   │       ├── graph.py          graph wiring
│   │       ├── nodes.py          the 4 node functions
│   │       ├── prompts.py        system prompts
│   │       └── llm_client.py     Groq client + JSON parsing
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx / App.css
│   │   ├── index.js / index.css
│   │   ├── store/                 Redux Toolkit slices
│   │   ├── components/            ComplaintForm, RiskAssessment, CopilotChat
│   │   └── api/api.js
│   ├── public/index.html
│   ├── package.json
│   └── .env.example
├── sample_data/
│   ├── sample_complaint_letter.pdf   Metformin HCl API contamination complaint
│   └── sample_complaint_email.txt    Ibuprofen blister-seal complaint email
└── README.md
```
