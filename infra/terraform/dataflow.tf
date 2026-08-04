# ══════════════════════════════════════════════════════════════════════
# Dataflow Job — Apache Beam Streaming Pipeline
# ══════════════════════════════════════════════════════════════════════
#
# CONNECTIONS:
#   - Runs the pipeline defined in: backend/streaming/pipeline.py
#   - Reads from: Pub/Sub raw-ecommerce-events topic
#   - Writes to: BigQuery ecommerce.orders table
#   - Publishes errors to: Pub/Sub pipeline-errors topic
#   - Uses: Dataflow service account from iam.tf
#   - Temp files: GCS dataflow_temp bucket from main.tf
#
# WARNING (from CRITICAL_WARNINGS.md):
#   Dataflow has NO free tier! A streaming pipeline runs 24/7.
#   Only deploy for integration testing or final demo.
#   Use DirectRunner for local development.
#
# NOTE: This Terraform resource is commented out by default.
# Uncomment and apply ONLY when you're ready to deploy to Dataflow.
# For local testing, use: make run-pipeline-local

# resource "google_dataflow_flex_template_job" "ecommerce_pipeline" {
#   name                    = "ecommerce-streaming-pipeline"
#   container_spec_gcs_path = "gs://${google_storage_bucket.dataflow_temp.name}/templates/pipeline.json"
#   region                  = var.region
#
#   parameters = {
#     project       = var.project_id
#     region        = var.region
#     input_topic   = google_pubsub_topic.raw_events.id
#     output_table  = "${var.project_id}:${var.bq_dataset}.orders"
#     error_topic   = google_pubsub_topic.pipeline_errors.id
#     temp_location = "gs://${google_storage_bucket.dataflow_temp.name}/temp"
#   }
#
#   service_account_email = google_service_account.dataflow.email
#
#   depends_on = [
#     google_project_service.dataflow,
#     google_bigquery_table.orders,
#     google_pubsub_topic.raw_events,
#     google_pubsub_topic.pipeline_errors,
#   ]
# }

# ────────────────────────────────────────────────────────────────
# Alternative: Classic Dataflow job (if not using Flex Templates)
# Deploy via CLI instead:
#
# python -m streaming.pipeline \
#   --runner DataflowRunner \
#   --project YOUR_PROJECT_ID \
#   --region asia-south1 \
#   --temp_location gs://YOUR_PROJECT-dataflow-temp/temp \
#   --staging_location gs://YOUR_PROJECT-dataflow-temp/staging \
#   --service_account_email dataflow-pipeline-sa@YOUR_PROJECT.iam.gserviceaccount.com \
#   --streaming
# ────────────────────────────────────────────────────────────────
