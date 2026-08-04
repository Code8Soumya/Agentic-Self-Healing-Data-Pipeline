# ══════════════════════════════════════════════════════════════════════
# Terraform Outputs — Exported Values
# ══════════════════════════════════════════════════════════════════════
#
# These outputs are used by:
# - scripts/deploy.sh to get Cloud Run URLs
# - Data generator to know the Pub/Sub topic path
# - Frontend .env to know the backend URL

output "lakehouse_bucket" {
  description = "GCS bucket for Iceberg Parquet files"
  value       = google_storage_bucket.lakehouse.name
}

output "dataflow_temp_bucket" {
  description = "GCS bucket for Dataflow temp/staging"
  value       = google_storage_bucket.dataflow_temp.name
}

output "raw_events_topic" {
  description = "Pub/Sub topic for raw e-commerce events"
  value       = google_pubsub_topic.raw_events.id
}

output "error_events_topic" {
  description = "Pub/Sub topic for pipeline errors"
  value       = google_pubsub_topic.pipeline_errors.id
}

output "bq_dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.ecommerce.dataset_id
}

output "dataflow_service_account_email" {
  description = "Service account for Dataflow pipeline"
  value       = google_service_account.dataflow.email
}

output "agent_service_account_email" {
  description = "Service account for the agent Cloud Run service"
  value       = google_service_account.agent.email
}
