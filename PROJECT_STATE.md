# 📊 PROJECT_STATE.md — Live Progress Tracker

> **Last updated:** 2026-08-04T22:25:00+05:30  
> **Updated by:** Antigravity (Claude Opus 4.6)  
> **Current Phase:** Phase 1 — GCP Foundation + Data Layer (Skeletons Created)  

---

## Overall Progress

```
Phase 1: GCP Foundation + Data Layer    [/] In Progress     (Week 1-2)
Phase 2: MCP Servers + Guardrails       [ ] Not Started     (Week 3)
Phase 3: LangGraph Agent + ADK          [ ] Not Started     (Week 4)
Phase 4: Next.js Dashboard              [ ] Not Started     (Week 5)
Phase 5: Observability + Evaluation     [ ] Not Started     (Week 6)
Phase 6: CI/CD + Documentation          [ ] Not Started     (Week 7)
```

**Legend:** `[ ]` = Not started | `[/]` = In progress | `[x]` = Complete | `[!]` = Blocked

---

## Phase 1: GCP Foundation + Data Layer

**Status:** `[/] IN PROGRESS — Skeletons created, need implementation`  
**Target:** Working Dataflow pipeline reading from Pub/Sub, validating schemas, writing to BigQuery, routing errors to error topic.  
**Breakpoint Test:** Generate events → check BigQuery for clean data + error topic for invalid events.

| ID | Task | Status | File(s) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 1.1 | Create GCP project, enable APIs | `[/]` | `scripts/setup_gcp.sh` | ✅ Script created, needs execution |
| 1.2 | Terraform: Pub/Sub topics + subs | `[/]` | `infra/terraform/pubsub.tf` | ✅ Full resource definitions written |
| 1.3 | Terraform: BigQuery dataset + tables | `[/]` | `infra/terraform/bigquery.tf` | ✅ Full resource definitions written |
| 1.4 | Terraform: GCS bucket for Iceberg | `[/]` | `infra/terraform/main.tf` | ✅ Full resource definitions written |
| 1.5 | Terraform: IAM service accounts | `[/]` | `infra/terraform/iam.tf` | ✅ Full resource definitions written |
| 1.6 | Run `terraform apply` | `[ ]` | All terraform | Depends: 1.2-1.5, needs User execution |
| 1.7 | Build event Pydantic models | `[/]` | `backend/app/models/events.py` | ✅ Full models with field definitions |
| 1.8 | Build order event generator | `[/]` | `backend/data_generator/order_events.py` | Skeleton + constants, needs logic impl |
| 1.9 | Build inventory event generator | `[/]` | `backend/data_generator/inventory_events.py` | Skeleton + constants, needs logic impl |
| 1.10 | Build user activity generator | `[/]` | `backend/data_generator/user_activity_events.py` | Skeleton + constants, needs logic impl |
| 1.11 | Build drift injector | `[/]` | `backend/data_generator/drift_injector.py` | Skeleton, needs logic impl |
| 1.12 | Build anomaly injector | `[/]` | `backend/data_generator/anomaly_injector.py` | Skeleton, needs logic impl |
| 1.13 | Build generator orchestrator | `[/]` | `backend/data_generator/generator.py` | Skeleton + CLI, needs logic impl |
| 1.14 | Build Beam schema definitions | `[/]` | `backend/streaming/schemas/*.py` | ✅ Full schema dicts defined |
| 1.15 | Build Beam JSON parser DoFn | `[/]` | `backend/streaming/transforms/parse_json.py` | Skeleton, needs process() impl |
| 1.16 | Build Beam schema validator DoFn | `[/]` | `backend/streaming/transforms/validate_schema.py` | Skeleton, needs process() impl |
| 1.17 | Build Beam quality checker DoFn | `[/]` | `backend/streaming/transforms/check_quality.py` | Skeleton, needs process() impl |
| 1.18 | Build Beam router DoFn | `[/]` | `backend/streaming/transforms/route_events.py` | Skeleton, needs process() impl |
| 1.19 | Build main Beam pipeline | `[/]` | `backend/streaming/pipeline.py` | Skeleton, needs build_pipeline() impl |
| 1.20 | Deploy pipeline to Dataflow | `[/]` | `infra/terraform/dataflow.tf` | ✅ TF written (commented out for cost) |
| 1.21 | **BREAKPOINT TEST** | `[ ]` | — | Generate events → verify BQ + error topic |

---

## Phase 2: MCP Servers + Guardrails

**Status:** `[ ] NOT STARTED`  
**Target:** All 4 MCP servers running with 24 tools. SQL guardrails blocking destructive ops.  
**Breakpoint Test:** Call each MCP tool independently and verify correct responses.  
**Depends on:** Phase 1 complete (tasks 1.1-1.21)

| ID | Task | Status | File(s) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 2.1 | BigQuery Catalog MCP Server (8 tools) | `[ ]` | `backend/app/mcp_servers/bigquery_catalog.py` | |
| 2.2 | GitHub Ops MCP Server (5 tools) | `[ ]` | `backend/app/mcp_servers/github_ops.py` | |
| 2.3 | DQ Rules Engine MCP Server (5 tools) | `[ ]` | `backend/app/mcp_servers/dq_rules_engine.py` | |
| 2.4 | GCP Infra MCP Server (6 tools) | `[ ]` | `backend/app/mcp_servers/gcp_infra.py` | |
| 2.5 | SQL validator guardrail | `[ ]` | `backend/app/guardrails/sql_validator.py` | |
| 2.6 | Pydantic output schemas | `[ ]` | `backend/app/guardrails/output_schemas.py` | |
| 2.7 | Rate limiter | `[ ]` | `backend/app/guardrails/rate_limiter.py` | |
| 2.8 | Unit tests: MCP servers | `[ ]` | `backend/tests/unit/test_mcp_*.py` | |
| 2.9 | Unit tests: Guardrails | `[ ]` | `backend/tests/unit/test_sql_validator.py` | |
| 2.10 | **BREAKPOINT TEST** | `[ ]` | — | All unit tests passing |

---

## Phase 3: LangGraph Agent + ADK Orchestrator

**Status:** `[ ] NOT STARTED`  
**Target:** Full healing loop: inject drift → agent detects → diagnoses → generates fix → applies or escalates → verifies.  
**Breakpoint Test:** `inject_drift.sh` → agent auto-heals on GCP.  
**Depends on:** Phase 2 complete (tasks 2.1-2.10)

| ID | Task | Status | File(s) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 3.1 | Agent state definition | `[ ]` | `backend/app/agents/state.py` | |
| 3.2 | Vertex AI service (model init + routing) | `[ ]` | `backend/app/services/vertex_ai_service.py` | |
| 3.3 | Triage agent prompts | `[ ]` | `backend/app/agents/prompts/triage_prompt.py` | |
| 3.4 | Triage node | `[ ]` | `backend/app/agents/nodes/triage.py` | Depends: 3.1-3.3 |
| 3.5 | Schema evolution prompts | `[ ]` | `backend/app/agents/prompts/schema_evolution_prompt.py` | |
| 3.6 | Schema evolution node | `[ ]` | `backend/app/agents/nodes/schema_evolution.py` | Depends: 2.1, 3.5 |
| 3.7 | Data quality prompts | `[ ]` | `backend/app/agents/prompts/data_quality_prompt.py` | |
| 3.8 | Data quality node | `[ ]` | `backend/app/agents/nodes/data_quality.py` | Depends: 2.3, 3.7 |
| 3.9 | Infra repair prompts | `[ ]` | `backend/app/agents/prompts/infra_repair_prompt.py` | |
| 3.10 | Infra repair node | `[ ]` | `backend/app/agents/nodes/infra_repair.py` | Depends: 2.4, 3.9 |
| 3.11 | Confidence gate node | `[ ]` | `backend/app/agents/nodes/confidence_gate.py` | |
| 3.12 | Firestore service | `[ ]` | `backend/app/services/firestore_service.py` | |
| 3.13 | Slack notifier | `[ ]` | `backend/app/notifications/slack_notifier.py` | |
| 3.14 | Escalation node | `[ ]` | `backend/app/agents/nodes/escalate.py` | Depends: 3.12, 3.13 |
| 3.15 | Apply fix node | `[ ]` | `backend/app/agents/nodes/apply_fix.py` | Depends: 2.1, 2.2, 2.5 |
| 3.16 | Verify fix node | `[ ]` | `backend/app/agents/nodes/verify_fix.py` | |
| 3.17 | Edge routing functions | `[ ]` | `backend/app/agents/edges/*.py` | |
| 3.18 | Main LangGraph graph | `[ ]` | `backend/app/agents/graph.py` | Depends: 3.4-3.17 |
| 3.19 | ADK root orchestrator | `[ ]` | `backend/app/orchestrator/root_agent.py` | Depends: 3.18 |
| 3.20 | ADK health checker | `[ ]` | `backend/app/orchestrator/health_checker.py` | |
| 3.21 | ADK supervisor | `[ ]` | `backend/app/orchestrator/supervisor.py` | |
| 3.22 | ADK-LangGraph bridge | `[ ]` | `backend/app/orchestrator/adk_langgraph_bridge.py` | Depends: 3.18, 3.19 |
| 3.23 | FastAPI main app | `[ ]` | `backend/app/main.py` | |
| 3.24 | Event endpoint | `[ ]` | `backend/app/api/events.py` | |
| 3.25 | Approval endpoints | `[ ]` | `backend/app/api/approvals.py` | |
| 3.26 | Backend Dockerfile | `[ ]` | `backend/Dockerfile` | |
| 3.27 | Deploy backend to Cloud Run | `[ ]` | `infra/terraform/cloud_run.tf` | |
| 3.28 | Connect Pub/Sub push subscription | `[ ]` | `infra/terraform/pubsub.tf` | |
| 3.29 | **BREAKPOINT TEST** | `[ ]` | — | Inject drift → agent heals on GCP |

---

## Phase 4: Next.js Dashboard

**Status:** `[ ] NOT STARTED`  
**Target:** Full dashboard on Cloud Run. SSE real-time. HITL approval flow works through UI.  
**Breakpoint Test:** Inject drift → approve in UI → fix applied.  
**Depends on:** Phase 3 complete (tasks 3.1-3.29)

| ID | Task | Status | File(s) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 4.1 | Initialize Next.js 15 project | `[ ]` | `frontend/` | |
| 4.2 | Tailwind + dark theme setup | `[ ]` | `tailwind.config.ts`, `globals.css` | |
| 4.3 | API client | `[ ]` | `frontend/src/lib/api.ts` | |
| 4.4 | TypeScript types | `[ ]` | `frontend/src/lib/types.ts` | |
| 4.5 | SSE hook | `[ ]` | `frontend/src/hooks/useSSE.ts` | |
| 4.6 | Root layout + sidebar | `[ ]` | `layout.tsx`, `Sidebar.tsx` | |
| 4.7 | Shared components | `[ ]` | `components/shared/*.tsx` | |
| 4.8 | MetricCard component | `[ ]` | `components/dashboard/MetricCard.tsx` | |
| 4.9 | Dashboard home page | `[ ]` | `app/page.tsx` | Depends: 4.5, 4.8 |
| 4.10 | Pipeline Health page | `[ ]` | `app/pipeline/page.tsx` | |
| 4.11 | EventFlowChart | `[ ]` | `components/pipeline/EventFlowChart.tsx` | |
| 4.12 | Agent Actions page | `[ ]` | `app/agents/page.tsx` | |
| 4.13 | Agent Detail page | `[ ]` | `app/agents/[id]/page.tsx` | |
| 4.14 | AgentDecisionTree | `[ ]` | `components/agents/AgentDecisionTree.tsx` | |
| 4.15 | TrajectoryViewer | `[ ]` | `components/agents/TrajectoryViewer.tsx` | |
| 4.16 | DiffViewer component | `[ ]` | `components/approvals/DiffViewer.tsx` | |
| 4.17 | SQLPreview component | `[ ]` | `components/approvals/SQLPreview.tsx` | |
| 4.18 | ApprovalCard component | `[ ]` | `components/approvals/ApprovalCard.tsx` | |
| 4.19 | Approvals page | `[ ]` | `app/approvals/page.tsx` | Depends: 4.5, 4.18 |
| 4.20 | Approval Detail page | `[ ]` | `app/approvals/[id]/page.tsx` | |
| 4.21 | Approval hooks | `[ ]` | `hooks/useApprovals.ts` | |
| 4.22 | Evaluation page | `[ ]` | `app/evaluation/page.tsx` | |
| 4.23 | Cost Tracker page | `[ ]` | `app/costs/page.tsx` | |
| 4.24 | SSE backend endpoint | `[ ]` | `backend/app/api/stream.py` | |
| 4.25 | SSE Next.js route | `[ ]` | `frontend/src/app/api/stream/route.ts` | |
| 4.26 | Dashboard data endpoints | `[ ]` | `backend/app/api/dashboard.py` | |
| 4.27 | Frontend Dockerfile | `[ ]` | `frontend/Dockerfile` | |
| 4.28 | Deploy frontend to Cloud Run | `[ ]` | `infra/terraform/cloud_run.tf` | |
| 4.29 | **BREAKPOINT TEST** | `[ ]` | — | Full HITL flow via dashboard |

---

## Phase 5: Observability + Evaluation

**Status:** `[ ] NOT STARTED`  
**Target:** Traces in Cloud Trace. Trajectory scores in BigQuery. Evaluation suite passing targets.  
**Breakpoint Test:** Run evaluation suite → all target metrics met.  
**Depends on:** Phase 4 complete

| ID | Task | Status | File(s) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 5.1 | OpenTelemetry setup | `[ ]` | `backend/app/observability/tracer.py` | |
| 5.2 | Instrument agent nodes | `[ ]` | `backend/app/agents/nodes/*.py` | |
| 5.3 | Trajectory evaluator | `[ ]` | `backend/app/observability/trajectory_evaluator.py` | |
| 5.4 | Cost tracker | `[ ]` | `backend/app/observability/cost_tracker.py` | |
| 5.5 | Metrics collector | `[ ]` | `backend/app/observability/metrics_collector.py` | |
| 5.6 | Cloud Monitoring alerts | `[ ]` | `infra/terraform/monitoring.tf` | |
| 5.7 | Build 200+ test scenarios | `[ ]` | `backend/tests/evaluation/scenarios.json` | |
| 5.8 | Evaluation runner | `[ ]` | `backend/tests/evaluation/run_evaluation.py` | |
| 5.9 | Run evaluation suite | `[ ]` | — | |
| 5.10 | **BREAKPOINT TEST** | `[ ]` | — | Target metrics met |

---

## Phase 6: CI/CD + Documentation

**Status:** `[ ] NOT STARTED`  
**Target:** PROJECT COMPLETE. Live URLs. Demo video. Public GitHub repo.  
**Depends on:** Phase 5 complete

| ID | Task | Status | File(s) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 6.1 | CI pipeline | `[ ]` | `.github/workflows/ci.yml` | |
| 6.2 | Deploy pipelines | `[ ]` | `.github/workflows/deploy-*.yml` | |
| 6.3 | README.md | `[ ]` | `README.md` | |
| 6.4 | Architecture doc | `[ ]` | `docs/architecture.md` | |
| 6.5 | ADLC report | `[ ]` | `docs/adlc-report.md` | |
| 6.6 | API reference | `[ ]` | `docs/api-reference.md` | |
| 6.7 | Record demo video | `[ ]` | — | |
| 6.8 | UI polish pass | `[ ]` | `frontend/` | |
| 6.9 | Final deploy | `[ ]` | — | |
| 6.10 | Push to GitHub | `[ ]` | — | |

---

## Known Blockers

| Blocker | Impact | Resolution |
| :--- | :--- | :--- |
| (none yet) | | |

## Deviations from Plan

| Date | What Changed | Why | Approved By |
| :--- | :--- | :--- | :--- |
| (none yet) | | | |
