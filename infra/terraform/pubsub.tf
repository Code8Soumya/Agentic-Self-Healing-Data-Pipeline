# ══════════════════════════════════════════════════════════════════════
# Pub/Sub Topics and Subscriptions
# ══════════════════════════════════════════════════════════════════════
#
# CONNECTIONS:
#   Topic 1 (raw-ecommerce-events):
#     - Published to by: data_generator/generator.py
#     - Subscribed by: Dataflow pipeline (streaming/pipeline.py)
#
#   Topic 2 (pipeline-errors):
#     - Published to by: Dataflow pipeline (error events from Beam DoFns)
#     - Subscribed by: FastAPI gateway (backend/app/api/events.py)
#       via push subscription to Cloud Run (Phase 3)

# ── Topic 1: Raw E-Commerce Events ──
# All generated events flow through this topic before entering the Beam pipeline.
resource "google_pubsub_topic" "raw_events" {
  name = var.pubsub_raw_topic

  depends_on = [google_project_service.pubsub]
}

# Subscription for Dataflow to pull events
# NOTE: The Beam pipeline uses topic-based ReadFromPubSub, but we create
# a subscription for monitoring and debugging in the GCP Console.
resource "google_pubsub_subscription" "raw_events_dataflow" {
  name  = "${var.pubsub_raw_topic}-dataflow-sub"
  topic = google_pubsub_topic.raw_events.id

  # Messages not ack'd within 60s are retried
  ack_deadline_seconds = 60

  # Keep undelivered messages for 7 days
  message_retention_duration = "604800s"

  # Enable exactly-once delivery for data integrity
  enable_exactly_once_delivery = true
}

# ── Topic 2: Pipeline Errors ──
# Invalid events detected by the Beam pipeline are published here.
# The healing agent subscribes to this topic to start diagnosis.
resource "google_pubsub_topic" "pipeline_errors" {
  name = var.pubsub_error_topic

  depends_on = [google_project_service.pubsub]
}

# Pull subscription for the error topic (Phase 1: for monitoring)
# In Phase 3, this will be replaced/augmented with a push subscription
# to the Cloud Run agent service.
resource "google_pubsub_subscription" "pipeline_errors_sub" {
  name  = "${var.pubsub_error_topic}-agent-sub"
  topic = google_pubsub_topic.pipeline_errors.id

  ack_deadline_seconds       = 120  # Agent needs more time to process
  message_retention_duration = "604800s"

  # Dead letter policy: after 5 failed attempts, send to dead letter topic
  # TODO (Phase 3): Create dead letter topic and uncomment
  # dead_letter_policy {
  #   dead_letter_topic     = google_pubsub_topic.dead_letter.id
  #   max_delivery_attempts = 5
  # }
}
