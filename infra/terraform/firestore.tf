# ══════════════════════════════════════════════════════════════════════
# Firestore Database + Indexes
# ══════════════════════════════════════════════════════════════════════
#
# CONNECTIONS:
#   - Used by: Agent service (Phase 3) for HITL pending approvals
#   - Used by: DQ Rules Engine MCP Server (Phase 2) for rule storage
#   - Read by: Frontend dashboard (Phase 4) via backend API
#   - IAM: Agent SA has roles/datastore.user (see iam.tf)
#   - API: firestore.googleapis.com enabled (see main.tf)
#
# Collections:
#   - pending_approvals/{approval_id}  — HITL approval queue
#   - dq_rules/{table_name}/rules/{rule_id} — Data quality rules
#   - dq_violations/{table_name}/violations/{violation_id} — DQ violations
#   - schema_versions/{table_name}/versions/{version_id} — Schema history

# ── Firestore Database ──
# Using Native mode (not Datastore mode) for real-time listeners and
# subcollection support needed by the DQ rules engine.
resource "google_firestore_database" "main" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  project     = var.project_id

  # Concurrency mode for optimistic locking
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"

  # Delete protection off for dev — enable in production
  delete_protection_state = "DELETE_PROTECTION_DISABLED"

  depends_on = [google_project_service.firestore]
}

# ── Composite Indexes ──
# Required for queries that filter + sort on multiple fields.

# Index: pending_approvals — filter by status, sort by severity + created_at
resource "google_firestore_index" "approvals_by_status_severity" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "pending_approvals"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "severity"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# Index: pending_approvals — filter by status, sort by created_at
resource "google_firestore_index" "approvals_by_status_time" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "pending_approvals"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# Index: dq_violations — filter by table + time range
resource "google_firestore_index" "violations_by_table_time" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "dq_violations"

  fields {
    field_path = "table"
    order      = "ASCENDING"
  }

  fields {
    field_path = "detected_at"
    order      = "DESCENDING"
  }
}
