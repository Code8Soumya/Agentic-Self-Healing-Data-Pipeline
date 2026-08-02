# 🤖 AGENTS.md — Master AI Instruction File

> **READ THIS FIRST.** Any AI assistant (Claude Code, Codex, GitHub Copilot, Antigravity, Cursor, or any other) working on this project MUST read this file before making any changes.

---

## What Is This Project?

**Agentic Self-Healing Data Pipeline** — A production-grade system on GCP that autonomously detects, diagnoses, and repairs broken e-commerce data pipelines using a LangGraph + Google ADK combined architecture, with human-in-the-loop escalation for complex failures. Full Next.js 15 dashboard.

**Cloud:** Google Cloud Platform (GCP) — direct deployment, no local tier  

---

## 📂 Critical Files You Must Read

Read these files in this order before doing ANY work:

| Order | File | Purpose |
| :--- | :--- | :--- |
| 1 | **`AGENTS.md`** (this file) | Project overview, rules, what NOT to do |
| 2 | **`PROJECT_STATE.md`** | Current phase, task completion status, what's done/in-progress/blocked |
| 3 | **`ARCHITECTURE_MAP.md`** | Where everything is, file dependencies, what to update when changing code |
| 4 | **`CRITICAL_WARNINGS.md`** | Things that WILL break the app, gotchas, patterns to follow |
| 5 | **`SYNC_LOG.md`** | Changelog of all AI-made changes — YOU must append to this after every session |
| 6 | **`IMPLEMENTATION_PLAN.md`** | The full detailed implementation plan (phases, tasks, schemas, APIs) |

---

## 🏗️ Architecture Summary

```
Google ADK (Root Orchestrator — lifecycle, health, supervision)
    └── LangGraph (Healing State Machine — stateful graph, retries, HITL)
            ├── Triage Agent (Gemini 3.5 Flash)
            ├── Schema Evolution Agent (Gemini 3.1 Pro for complex)
            ├── Data Quality Agent (Gemini 3.5 Flash)
            └── Infrastructure Agent (Gemini 3.5 Flash)
                    │
                    └── 4 × FastMCP Servers (BigQuery, GitHub, DQ Rules, GCP Infra)

GCP Services: Pub/Sub → Dataflow → BigQuery Iceberg → Cloud Run → Firestore → Vertex AI
Frontend: Next.js 15 (App Router, TypeScript, Tailwind, SSE real-time)
```

---

## ⚖️ Rules for ALL AI Assistants

### ALWAYS Do
1. **Read `PROJECT_STATE.md`** before starting work to know what's done and what's next
2. **Update `PROJECT_STATE.md`** after completing any task (mark `[x]` for done, `[/]` for in-progress)
3. **Append to `SYNC_LOG.md`** after every coding session with: date, AI tool used, files changed, what was done
4. **Check `CRITICAL_WARNINGS.md`** before touching any file listed there
5. **Follow the file dependency graph** in `ARCHITECTURE_MAP.md` — if you change a file, update all dependents
6. **Use the exact tech stack specified** — don't substitute libraries
7. **Run tests** after any code change if tests exist for that module
8. **Ask the user** if you need to deviate from the implementation plan

### NEVER Do
1. **Never skip reading PROJECT_STATE.md** — you might redo completed work or skip dependencies
2. **Never change the LangGraph state schema** (`backend/app/agents/state.py`) without updating ALL nodes, edges, and the frontend types
3. **Never add new GCP services** without updating Terraform AND `ARCHITECTURE_MAP.md`
4. **Never change API endpoint signatures** without updating the frontend API client AND types
5. **Never install new Python/npm packages** without updating requirements.txt/package.json AND documenting why in SYNC_LOG
6. **Never commit directly to main** — always use feature branches
7. **Never hardcode GCP credentials, API keys, or project IDs** — use environment variables / Secret Manager
8. **Never modify `IMPLEMENTATION_PLAN.md`** — if the plan needs changing, flag it to the user first

---

## 🛠️ Tech Stack — Do Not Substitute

### Backend
| Component | Technology | Version |
| :--- | :--- | :--- |
| Language | Python | 3.11+ |
| API Framework | FastAPI | latest |
| Agent Framework (Core) | LangGraph | latest |
| Agent Framework (Orchestrator) | Google ADK | latest |
| MCP Servers | FastMCP | latest |
| LLM (Simple) | Gemini 3.5 Flash | via Vertex AI |
| LLM (Complex) | Gemini 3.1 Pro | via Vertex AI |
| LangChain Google | langchain-google-vertexai | latest |
| MCP Adapters | langchain-mcp-adapters | latest |
| Streaming | Apache Beam | latest |
| Data Validation | Pydantic v2 | latest |
| Tracing | OpenTelemetry | latest |
| Testing | pytest | latest |

### Frontend
| Component | Technology | Version |
| :--- | :--- | :--- |
| Framework | Next.js | 15 (App Router) |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | v4 |
| Charts | Recharts | latest |
| Syntax Highlighting | Prism.js or Shiki | latest |
| Testing | Jest + React Testing Library | latest |

### Infrastructure
| Component | Technology |
| :--- | :--- |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Container Registry | Google Artifact Registry |
| Compute | Cloud Run |
| Streaming | Cloud Dataflow |
| Database | BigQuery (Iceberg Managed Tables) |
| State Store | Firestore |
| Messaging | Cloud Pub/Sub |
| Secrets | Secret Manager |
| Monitoring | Cloud Trace + Cloud Monitoring |

---

## 📁 Project Root Structure

```
agentic-self-healing-pipeline/
├── AGENTS.md                    ← YOU ARE HERE (read first)
├── PROJECT_STATE.md             ← Current progress tracker
├── ARCHITECTURE_MAP.md          ← File dependency graph + navigation
├── CRITICAL_WARNINGS.md         ← Breaking points + gotchas
├── SYNC_LOG.md                  ← AI session changelog
├── IMPLEMENTATION_PLAN.md       ← Full detailed plan (DO NOT MODIFY)
├── README.md                    ← Public-facing project documentation
├── LICENSE
├── Makefile
├── .gitignore
│
├── backend/                     ← Python (FastAPI + LangGraph + ADK + MCP)
├── frontend/                    ← Next.js 15 (App Router, TypeScript)
├── infra/                       ← Terraform + Docker
├── scripts/                     ← Deployment + demo scripts
├── docs/                        ← Architecture docs, ADLC report
└── .github/                     ← CI/CD workflows
```

---

## 🔀 Deviation Protocol

If you (the AI) find yourself needing to deviate from the implementation plan:

1. **STOP** coding immediately
2. **Document** the deviation in `SYNC_LOG.md` with:
   - What you were trying to do
   - Why the plan doesn't work
   - What you propose instead
3. **Ask the user** for approval before proceeding
4. If approved, user will update `IMPLEMENTATION_PLAN.md`
5. You update `PROJECT_STATE.md` and `ARCHITECTURE_MAP.md` accordingly

---

## 🧪 How to Verify Your Work

After completing any task:

```bash
# Backend tests
cd backend && pytest tests/unit/ -v

# Frontend tests  
cd frontend && npm test

# Type checking
cd frontend && npx tsc --noEmit

# Lint
cd backend && ruff check .
cd frontend && npm run lint
```

---

## 💬 How to Communicate With the User

- If something is **unclear** → Ask the user, don't assume
- If something is **broken** → Log it in SYNC_LOG.md, tell the user
- If something **deviates from plan** → Follow the Deviation Protocol above
- If you **complete a phase** → Update PROJECT_STATE.md, celebrate 🎉
