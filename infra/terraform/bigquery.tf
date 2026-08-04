# ══════════════════════════════════════════════════════════════════════
# BigQuery Dataset and Tables
# ══════════════════════════════════════════════════════════════════════
#
# CONNECTIONS:
#   - Dataset: ecommerce
#   - Table 1 (orders): Written to by Dataflow pipeline via Beam WriteToBigQuery
#     Schema must match: streaming/schemas/order_schema.py ORDER_BQ_SCHEMA
#     Schema must match: app/models/events.py OrderEventV1
#   - Table 2 (healing_events): Written to by agents/nodes/apply_fix.py
#     Schema must match: app/models/healing.py HealingResult
#   - Table 3 (trajectory_scores): Written to by observability/trajectory_evaluator.py
#     Schema must match: app/models/trajectory.py TrajectoryScore
#
# WARNING: If you change the table schema here, you MUST also update:
#   1. The corresponding Pydantic model in backend/app/models/
#   2. The Beam schema in backend/streaming/schemas/
#   3. The frontend TypeScript types in frontend/src/lib/types.ts

# ── BigQuery Dataset ──
resource "google_bigquery_dataset" "ecommerce" {
  dataset_id = var.bq_dataset
  location   = var.region

  description = "E-commerce data pipeline dataset — orders, healing events, trajectory scores"

  # Delete all tables when dataset is destroyed (for dev/test cleanup)
  delete_contents_on_destroy = true

  depends_on = [google_project_service.bigquery]
}

# ── Table 1: Orders (Iceberg Managed Table) ──
# Stores valid e-commerce order events processed by the Dataflow pipeline.
# Uses BigQuery's managed Apache Iceberg format for time-travel queries.
#
# NOTE: BigQuery Iceberg managed tables use external_data_configuration
# with a GCS storage URI for Parquet files.
resource "google_bigquery_table" "orders" {
  dataset_id = google_bigquery_dataset.ecommerce.dataset_id
  table_id   = "orders"

  description = "E-commerce order events — Iceberg managed table"

  # For now using standard BigQuery table. Iceberg managed tables
  # may need to be created via SQL DDL if Terraform support is limited.
  # TODO: Switch to Iceberg managed table via DDL if needed.

  schema = jsonencode([
    {name = "event_id",         type = "STRING",    mode = "REQUIRED",  description = "Unique event UUID"},
    {name = "timestamp",        type = "TIMESTAMP", mode = "REQUIRED",  description = "Event timestamp"},
    {name = "order_id",         type = "STRING",    mode = "REQUIRED",  description = "Order ID (ORD-2026-XXXXX)"},
    {name = "customer_id",      type = "STRING",    mode = "REQUIRED",  description = "Customer ID"},
    {name = "product_id",       type = "STRING",    mode = "REQUIRED",  description = "Product ID"},
    {name = "product_name",     type = "STRING",    mode = "NULLABLE",  description = "Product name"},
    {name = "category",         type = "STRING",    mode = "NULLABLE",  description = "Product category"},
    {name = "quantity",         type = "INT64",     mode = "NULLABLE",  description = "Quantity ordered"},
    {name = "unit_price",       type = "FLOAT64",   mode = "NULLABLE",  description = "Price per unit"},
    {name = "currency",         type = "STRING",    mode = "NULLABLE",  description = "Currency code"},
    {name = "total_amount",     type = "FLOAT64",   mode = "NULLABLE",  description = "Total order amount"},
    {name = "payment_method",   type = "STRING",    mode = "NULLABLE",  description = "Payment method"},
    {name = "shipping_city",    type = "STRING",    mode = "NULLABLE",  description = "Shipping city"},
    {name = "shipping_state",   type = "STRING",    mode = "NULLABLE",  description = "Shipping state"},
    {name = "shipping_pincode", type = "STRING",    mode = "NULLABLE",  description = "Shipping postal code"},
    {name = "status",           type = "STRING",    mode = "NULLABLE",  description = "Order status"},
    {name = "ingested_at",      type = "TIMESTAMP", mode = "NULLABLE",  description = "Pipeline ingestion time"},
  ])

  deletion_protection = false  # Allow terraform destroy in dev
}

# ── Table 2: Healing Events ──
# Stores complete healing event records (diagnosis, fix, verification).
# Written by the agent after each healing cycle completes.
resource "google_bigquery_table" "healing_events" {
  dataset_id = google_bigquery_dataset.ecommerce.dataset_id
  table_id   = "healing_events"

  description = "Agent healing event records — one row per error → fix cycle"

  schema = jsonencode([
    {name = "healing_id",           type = "STRING",    mode = "REQUIRED"},
    {name = "error_event_id",       type = "STRING",    mode = "REQUIRED"},
    {name = "error_type",           type = "STRING",    mode = "NULLABLE"},
    {name = "error_subtype",        type = "STRING",    mode = "NULLABLE"},
    {name = "severity",             type = "STRING",    mode = "NULLABLE"},
    {name = "complexity",           type = "STRING",    mode = "NULLABLE"},
    {name = "model_used",           type = "STRING",    mode = "NULLABLE"},
    {name = "diagnosis",            type = "STRING",    mode = "NULLABLE"},
    {name = "proposed_fix",         type = "STRING",    mode = "NULLABLE"},
    {name = "rollback_statement",   type = "STRING",    mode = "NULLABLE"},
    {name = "confidence",           type = "FLOAT64",   mode = "NULLABLE"},
    {name = "approval_status",      type = "STRING",    mode = "NULLABLE"},
    {name = "approved_by",          type = "STRING",    mode = "NULLABLE"},
    {name = "fix_applied",          type = "BOOL",      mode = "NULLABLE"},
    {name = "verification_passed",  type = "BOOL",      mode = "NULLABLE"},
    {name = "time_to_resolution_ms",type = "INT64",     mode = "NULLABLE"},
    {name = "input_tokens",         type = "INT64",     mode = "NULLABLE"},
    {name = "output_tokens",        type = "INT64",     mode = "NULLABLE"},
    {name = "cost_usd",             type = "FLOAT64",   mode = "NULLABLE"},
    {name = "created_at",           type = "TIMESTAMP", mode = "NULLABLE"},
    {name = "resolved_at",          type = "TIMESTAMP", mode = "NULLABLE"},
    {name = "trajectory",           type = "JSON",      mode = "NULLABLE"},
  ])

  deletion_protection = false
}

# ── Table 3: Trajectory Scores ──
# Stores the 5-metric trajectory evaluation scores for each healing event.
resource "google_bigquery_table" "trajectory_scores" {
  dataset_id = google_bigquery_dataset.ecommerce.dataset_id
  table_id   = "trajectory_scores"

  description = "5-metric trajectory evaluation scores per healing event"

  schema = jsonencode([
    {name = "score_id",                   type = "STRING",    mode = "REQUIRED"},
    {name = "healing_id",                 type = "STRING",    mode = "REQUIRED"},
    {name = "task_completion",             type = "FLOAT64",   mode = "NULLABLE"},
    {name = "tool_selection_accuracy",     type = "FLOAT64",   mode = "NULLABLE"},
    {name = "trajectory_efficiency",       type = "FLOAT64",   mode = "NULLABLE"},
    {name = "time_to_resolution_sec",      type = "FLOAT64",   mode = "NULLABLE"},
    {name = "cost_per_heal_usd",           type = "FLOAT64",   mode = "NULLABLE"},
    {name = "safety_violations",           type = "INT64",     mode = "NULLABLE"},
    {name = "scored_at",                   type = "TIMESTAMP", mode = "NULLABLE"},
  ])

  deletion_protection = false
}
