# ══════════════════════════════════════════════════════════════════════
# Main Terraform Configuration — Agentic Self-Healing Data Pipeline
# ══════════════════════════════════════════════════════════════════════
#
# CONNECTIONS:
# - variables.tf: All configurable parameters
# - outputs.tf: Exported values for other modules and scripts
# - This file: Provider setup, API enablement, GCS bucket
#
# USAGE:
#   cd infra/terraform
#   terraform init
#   terraform plan
#   terraform apply

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ── Enable Required GCP APIs ──
# These must be enabled before any resources can be created.
# The setup_gcp.sh script also enables these, but Terraform ensures they stay enabled.

resource "google_project_service" "pubsub" {
  service            = "pubsub.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "bigquery" {
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "dataflow" {
  service            = "dataflow.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "storage" {
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firestore" {
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "aiplatform" {
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudtrace" {
  service            = "cloudtrace.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "monitoring" {
  service            = "monitoring.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam" {
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

# ── GCS Bucket for Iceberg Parquet Files ──
# BigQuery Iceberg managed tables store their Parquet files in this bucket.
# CONNECTIONS:
#   - BigQuery orders table (bigquery.tf) references this as storage_uri
#   - Dataflow pipeline writes Parquet files here via BigQuery
resource "google_storage_bucket" "lakehouse" {
  name     = "${var.project_id}-ecommerce-lakehouse"
  location = var.region

  uniform_bucket_level_access = true
  force_destroy               = true  # Allow terraform destroy to delete non-empty bucket

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90  # Delete old Parquet files after 90 days
    }
  }
}

# ── GCS Bucket for Dataflow Temp/Staging ──
# Dataflow needs temp and staging locations for job execution.
# CONNECTIONS:
#   - dataflow.tf references this for temp_gcs_location and staging_location
resource "google_storage_bucket" "dataflow_temp" {
  name     = "${var.project_id}-dataflow-temp"
  location = var.region

  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 7  # Clean up temp files after 7 days
    }
  }
}
