# ══════════════════════════════════════════════════════════════════════
# Terraform Variables — Configurable Parameters
# ══════════════════════════════════════════════════════════════════════
#
# Override these in terraform.tfvars or via CLI: -var="project_id=my-project"

variable "project_id" {
  description = "GCP project ID where all resources will be created"
  type        = string
  # No default — must be provided
}

variable "region" {
  description = "GCP region for resource deployment"
  type        = string
  default     = "asia-south1"
}

variable "zone" {
  description = "GCP zone for zonal resources"
  type        = string
  default     = "asia-south1-a"
}

variable "bq_dataset" {
  description = "BigQuery dataset name for e-commerce data"
  type        = string
  default     = "ecommerce"
}

variable "pubsub_raw_topic" {
  description = "Pub/Sub topic for raw e-commerce events from generators"
  type        = string
  default     = "raw-ecommerce-events"
}

variable "pubsub_error_topic" {
  description = "Pub/Sub topic for pipeline error events that trigger the healing agent"
  type        = string
  default     = "pipeline-errors"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}
