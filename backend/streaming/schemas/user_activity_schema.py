"""User activity event schema definitions for the Beam pipeline.

CONNECTIONS:
- Used by: transforms/validate_schema.py, transforms/route_events.py
- Must match: app.models.events.UserActivityEvent, infra/terraform/bigquery.tf
"""

USER_ACTIVITY_SCHEMA: dict = {
    "event_id": {"type": "string", "required": True},
    "event_type": {"type": "string", "required": True, "description": "Must be 'user_activity'"},
    "timestamp": {"type": "string", "required": True},
    "customer_id": {"type": "string", "required": True},
    "session_id": {"type": "string", "required": True},
    "action": {"type": "string", "required": True, "description": "page_view/add_to_cart/etc"},
    "page_url": {"type": "string", "required": True},
    "device_type": {"type": "string", "required": True, "description": "mobile/desktop/tablet"},
    "referrer": {"type": "string", "required": False},
}

USER_ACTIVITY_BQ_SCHEMA: str = ",".join([
    "event_id:STRING",
    "timestamp:TIMESTAMP",
    "customer_id:STRING",
    "session_id:STRING",
    "action:STRING",
    "page_url:STRING",
    "device_type:STRING",
    "referrer:STRING",
    "ingested_at:TIMESTAMP",
])
