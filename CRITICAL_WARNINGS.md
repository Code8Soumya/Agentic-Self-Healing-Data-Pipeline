# 🚨 CRITICAL_WARNINGS.md — Danger Zone

> **WARNING:** Read this file carefully. These are the critical things that will break the app, cause production outages, or result in massive cloud bills if ignored.

---

## 🛑 Application Breaking Points (Code)

### 1. LangGraph State Mutability
- **The Danger:** LangGraph state is immutable in some contexts and heavily relies on the exact `TypedDict` structure. If you change a key in `state.py` but forget to update a single node that reads/writes that key, the graph will crash at runtime, causing the agent to hang indefinitely.
- **The Rule:** Search the entire `backend/app/agents/` directory for the key name before deleting or renaming it.

### 2. Server-Sent Events (SSE) Streaming
- **The Danger:** Next.js and Cloud Run both have timeout limits for long-lived HTTP connections. If your backend SSE endpoint (`api/stream.py`) stops sending keep-alive pings, Cloud Run will forcefully terminate the connection, and the dashboard will go out of sync.
- **The Rule:** Always include a ping/heartbeat every 15 seconds in the SSE stream. Handle client disconnects gracefully to avoid memory leaks.

### 3. BigQuery Iceberg Table Schema Evolution
- **The Danger:** BigQuery Iceberg tables require specific Parquet configurations. If the AI agent generates a raw BigQuery DDL that isn't compatible with Iceberg managed tables (e.g., trying to use native BQ clustering instead of Iceberg partitioning), the table will break.
- **The Rule:** The `sql_validator.py` guardrail must enforce Iceberg-compatible DDL. Do not bypass the guardrail.

### 4. Pydantic Model Validation
- **The Danger:** The FastAPI endpoints and the LangChain structured output both rely on Pydantic `v2`. If you use Pydantic `v1` syntax (e.g., `parse_obj_as` instead of `TypeAdapter`), the app will crash.
- **The Rule:** Always use Pydantic v2 syntax.

---

## 💸 Cloud Infrastructure & Billing Gotchas

### 1. Cloud Dataflow Runaway Costs
- **The Danger:** Dataflow does NOT have a free tier. If you deploy a streaming pipeline and forget to tear it down, it will run 24/7 and consume your $300 GCP credit in a matter of days.
- **The Rule:** For local development and testing, use the `DirectRunner`. Only deploy to Dataflow (`DataflowRunner`) for the final demonstration or integration test. ALWAYS tear down the Dataflow job when done.

### 2. Vertex AI API Quotas (Gemini)
- **The Danger:** Gemini 3.1 Pro has stricter rate limits (Requests Per Minute) than Gemini 3.5 Flash. If the LangGraph retry loop spins out of control, it will hit the Vertex AI quota, crashing the agent and potentially incurring high token costs.
- **The Rule:** The `max_retries` counter in the agent state MUST be strictly enforced (default: 3). Do not allow infinite retry loops.

### 3. Cloud Run "Scale to Zero" Cold Starts
- **The Danger:** Cloud Run scales to zero to save money. When a new event triggers the agent, the container must boot up. If the LangGraph initialization takes too long (e.g., loading heavy models into memory locally instead of using APIs), the Pub/Sub push request will time out, and Pub/Sub will retry endlessly.
- **The Rule:** Keep the backend container lightweight. Do not bundle ML models; rely entirely on the Vertex AI API.

### 4. Firestore Indexing
- **The Danger:** The dashboard queries Firestore for pending approvals. If you add a new filter (e.g., sorting by severity AND filtering by status), Firestore will throw an error requiring a composite index.
- **The Rule:** If you change the query logic in `firestore_service.py` or the Next.js hooks, you MUST update `infra/terraform/firestore.tf` to create the required composite index.

---

## 🔐 Security & Access Control

### 1. IAM Permissions (Service Accounts)
- **The Danger:** The Cloud Run agent service needs permission to read Pub/Sub, write to Firestore, query BigQuery, and call Vertex AI. If you add a new GCP service (e.g., Cloud Storage) but don't grant the IAM role in Terraform, the agent will silently fail.
- **The Rule:** Every new GCP service interaction MUST be paired with an IAM role binding in `infra/terraform/iam.tf`.

### 2. The SQL Guardrail
- **The Danger:** The agent is generating SQL DDL to execute on a production database. A hallucination could result in `DROP TABLE ecommerce.orders`.
- **The Rule:** NEVER disable `sql_validator.py`. It is the final defense against destructive agent behavior. If a valid query is blocked, fix the regex in the validator, do not bypass it.
