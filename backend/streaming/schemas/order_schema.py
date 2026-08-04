"""Order event schema definitions for the Beam pipeline.

CONNECTIONS:
- Used by: transforms/validate_schema.py (to validate incoming events)
           transforms/route_events.py (to write to correct BigQuery table)
- Must match: app.models.events.OrderEventV1 (Pydantic model)
              infra/terraform/bigquery.tf (BigQuery table definition)
- If you add a field here, you MUST also add it to:
  1. app/models/events.py (OrderEventV1)
  2. infra/terraform/bigquery.tf (orders table)
"""

# Schema used for validation in the Beam pipeline
# Maps field_name -> {"type": python_type, "required": bool, "description": str}
ORDER_SCHEMA: dict = {
    "event_id": {"type": "string", "required": True, "description": "UUID"},
    "event_type": {"type": "string", "required": True, "description": "Must be 'order'"},
    "timestamp": {"type": "string", "required": True, "description": "ISO 8601 datetime"},
    "order_id": {"type": "string", "required": True, "description": "ORD-2026-XXXXX"},
    "customer_id": {"type": "string", "required": True, "description": "CUST-XXXXX"},
    "product_id": {"type": "string", "required": True, "description": "PROD-XXXXX"},
    "product_name": {"type": "string", "required": True, "description": "Product name"},
    "category": {"type": "string", "required": True, "description": "Product category"},
    "quantity": {"type": "integer", "required": True, "description": "1-100"},
    "unit_price": {"type": "number", "required": True, "description": "0.01-9999.99"},
    "currency": {"type": "string", "required": True, "description": "INR/USD/EUR"},
    "total_amount": {"type": "number", "required": True, "description": "qty * price"},
    "payment_method": {"type": "string", "required": True, "description": "Payment type"},
    "shipping_address": {"type": "object", "required": True, "description": "Nested address",
        "fields": {
            "city": {"type": "string", "required": True},
            "state": {"type": "string", "required": True},
            "pincode": {"type": "string", "required": True},
            "country": {"type": "string", "required": False},
        }
    },
    "status": {"type": "string", "required": True, "description": "Order status"},
}

# BigQuery table schema for writing order events
# Used by route_events.py to construct BigQuery write transform
ORDER_BQ_SCHEMA: str = ",".join([
    "event_id:STRING",
    "timestamp:TIMESTAMP",
    "order_id:STRING",
    "customer_id:STRING",
    "product_id:STRING",
    "product_name:STRING",
    "category:STRING",
    "quantity:INT64",
    "unit_price:FLOAT64",
    "currency:STRING",
    "total_amount:FLOAT64",
    "payment_method:STRING",
    "shipping_city:STRING",
    "shipping_state:STRING",
    "shipping_pincode:STRING",
    "status:STRING",
    "ingested_at:TIMESTAMP",
])
