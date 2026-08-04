"""Inventory event schema definitions for the Beam pipeline.

CONNECTIONS:
- Used by: transforms/validate_schema.py, transforms/route_events.py
- Must match: app.models.events.InventoryEvent, infra/terraform/bigquery.tf
"""

INVENTORY_SCHEMA: dict = {
    "event_id": {"type": "string", "required": True},
    "event_type": {"type": "string", "required": True, "description": "Must be 'inventory'"},
    "timestamp": {"type": "string", "required": True},
    "product_id": {"type": "string", "required": True},
    "warehouse_id": {"type": "string", "required": True},
    "action": {"type": "string", "required": True, "description": "restock/sold/returned/damaged"},
    "quantity_change": {"type": "integer", "required": True},
    "current_stock": {"type": "integer", "required": True},
    "reorder_threshold": {"type": "integer", "required": True},
}

INVENTORY_BQ_SCHEMA: str = ",".join([
    "event_id:STRING",
    "timestamp:TIMESTAMP",
    "product_id:STRING",
    "warehouse_id:STRING",
    "action:STRING",
    "quantity_change:INT64",
    "current_stock:INT64",
    "reorder_threshold:INT64",
    "ingested_at:TIMESTAMP",
])
