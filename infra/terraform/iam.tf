# ══════════════════════════════════════════════════════════════════════
# IAM — Service Accounts and Role Bindings
# ══════════════════════════════════════════════════════════════════════
#
# CONNECTIONS:
#   - Dataflow SA: Used by streaming/pipeline.py to run the Beam pipeline
#   - Agent SA: Used by Cloud Run agent service (Phase 3)
#   - Dashboard SA: Used by Cloud Run frontend service (Phase 4)
#
# WARNING: If you add a new GCP service interaction, you MUST add
# the corresponding IAM role here. See CRITICAL_WARNINGS.md.

# ── Dataflow Service Account ──
# Used by the Apache Beam pipeline deployed to Cloud Dataflow.
# Needs: Pub/Sub read, BigQuery write, GCS read/write
resource "google_service_account" "dataflow" {
  account_id   = "dataflow-pipeline-sa"
  display_name = "Dataflow Pipeline Service Account"
  description  = "Service account for the Apache Beam streaming pipeline"

  depends_on = [google_project_service.iam]
}

# Dataflow needs to read from Pub/Sub
resource "google_project_iam_member" "dataflow_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.dataflow.email}"
}

# Dataflow needs to publish errors to Pub/Sub
resource "google_project_iam_member" "dataflow_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.dataflow.email}"
}

# Dataflow needs to write to BigQuery
resource "google_project_iam_member" "dataflow_bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dataflow.email}"
}

# Dataflow needs BigQuery job creation
resource "google_project_iam_member" "dataflow_bq_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dataflow.email}"
}

# Dataflow needs GCS for temp/staging files
resource "google_project_iam_member" "dataflow_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataflow.email}"
}

# Dataflow needs its own worker role
resource "google_project_iam_member" "dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow.email}"
}

# ── Agent Service Account (Phase 3) ──
# Used by the Cloud Run agent service. Pre-created here so permissions
# are ready when we deploy the agent.
# Needs: Pub/Sub, BigQuery, Firestore, Vertex AI, GCS
resource "google_service_account" "agent" {
  account_id   = "healing-agent-sa"
  display_name = "Healing Agent Service Account"
  description  = "Service account for the AI healing agent on Cloud Run"

  depends_on = [google_project_service.iam]
}

resource "google_project_iam_member" "agent_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_bq_admin" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_bq_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_trace" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.agent.email}"
}
