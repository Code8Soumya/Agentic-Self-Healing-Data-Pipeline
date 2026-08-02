# 🗺️ ARCHITECTURE_MAP.md — The Project Compass

> **PURPOSE:** Use this file to understand where code lives and what other files you need to update when you make a change.

---

## 🧭 Where Is Everything?

### Backend (Python)
- **FastAPI App & API Routes:** `backend/app/api/`
- **LangGraph Core (The Brain):** `backend/app/agents/`
  - *Graph Definition:* `graph.py`
  - *Agent State:* `state.py`
  - *Nodes (Actions):* `nodes/`
  - *Edges (Routing):* `edges/`
  - *Prompts:* `prompts/`
- **Google ADK (The Orchestrator):** `backend/app/orchestrator/`
- **MCP Servers (Tools):** `backend/app/mcp_servers/`
- **Safety / Guardrails:** `backend/app/guardrails/`
- **Data Models:** `backend/app/models/`
- **Observability (Trace/Eval):** `backend/app/observability/`
- **External Services (BQ, Firestore):** `backend/app/services/`
- **Dataflow Streaming Pipeline:** `backend/streaming/`
- **Event Simulators:** `backend/data_generator/`

### Frontend (Next.js 15)
- **Pages / Routing:** `frontend/src/app/`
- **React Components:** `frontend/src/components/`
- **API Client / Types:** `frontend/src/lib/`
- **Custom Hooks:** `frontend/src/hooks/`

### Infrastructure
- **Terraform:** `infra/terraform/`
- **Docker / Compose:** `infra/docker/`

---

## 🔗 The Dependency Matrix (If you change X, change Y)

**When modifying code, ALWAYS check this matrix to ensure you update dependent files.**

| If you change... | You MUST also update... | Why? |
| :--- | :--- | :--- |
| **LangGraph State (`state.py`)** | ALL Nodes, ALL Edges, `models/trajectory.py`, Frontend Types (`types.ts`) | The entire graph relies on this exact TypedDict structure. |
| **API Endpoint Signature** | Frontend API Client (`api.ts`), Frontend Types (`types.ts`) | The React components will break if the API contract changes. |
| **BigQuery Table Schema** | Terraform (`bigquery.tf`), Beam Pipeline (`streaming/schemas/`), MCP Server (`bigquery_catalog.py`) | Terraform must provision the correct schema; pipeline must validate it. |
| **MCP Tool Parameters** | LangChain MCP Adapter config, Agent Prompts (so LLM knows the new args) | The agent will hallucinate arguments if it doesn't know the new tool schema. |
| **Event Structure (`events.py`)** | Data Generator, Beam Pipeline (`validate_schema.py`), Frontend Types | The generator creates the data; pipeline verifies it; UI displays it. |
| **Firestore Document Schema** | Frontend Types, `firestore_service.py`, Frontend Hooks (`useApprovals.ts`) | Data mismatches will crash the React UI. |
| **Environment Variables** | `.env.example`, Backend Config (`config.py`), Next.js Config, Terraform (`cloud_run.tf`) | App will crash on startup if missing environment vars. |

---

## 🛠️ Update Guidelines by Task Nature

### 1. Adding a new Agent Node (LangGraph)
1. Define the node function in `backend/app/agents/nodes/`
2. Define any new state fields required in `backend/app/agents/state.py`
3. Add the node to the graph in `backend/app/agents/graph.py`
4. Create/update edges to route to the new node
5. Instrument the node in `observability/tracer.py`

### 2. Adding a new MCP Tool
1. Define the tool in the relevant server in `backend/app/mcp_servers/`
2. Ensure parameters have clear type hints and docstrings (FastMCP uses these for the LLM)
3. Write a unit test for the tool in `backend/tests/unit/`
4. Update the relevant agent's prompt to let it know when to use the tool

### 3. Adding a new Dashboard Widget
1. Define the UI component in `frontend/src/components/`
2. Create/update the data fetching hook in `frontend/src/hooks/`
3. If new data is needed, create/update the API route in `backend/app/api/dashboard.py`
4. Add the component to the relevant page in `frontend/src/app/`

### 4. Modifying Infrastructure
1. Update the `.tf` file in `infra/terraform/`
2. Run `terraform plan` to verify
3. If adding a new IAM role/permission, update `infra/terraform/iam.tf`
4. Document the new infrastructure in `docs/architecture.md`
