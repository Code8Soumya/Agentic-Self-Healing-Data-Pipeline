"""E-commerce event data models.

CONNECTIONS:
- Imported by: data_generator/*.py (to create events)
              streaming/schemas/*.py (to validate events in Beam pipeline)
              streaming/transforms/*.py (type hints)
              api/events.py (request body parsing)
              mcp_servers/bigquery_catalog.py (schema comparison)
- Depends on: models/enums.py

SCHEMA VERSIONS:
- OrderEventV1: Baseline order schema
- OrderEventV2: After schema drift Type A (new fields added)
- If you change any model here, you MUST update:
  1. The corresponding Beam schema in streaming/schemas/
  2. The BigQuery table schema in infra/terraform/bigquery.tf
  3. The frontend TypeScript types in frontend/src/lib/types.ts
"""
from datetime import datetime, date
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field
import uuid


class ShippingAddress(BaseModel):
    """Shipping address embedded in order events.
    
    NOTE: Schema drift Type E (nested_change) may add new fields here
    like 'state' and 'pincode'. The agent must handle this.
    """
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State/province")
    pincode: str = Field(..., description="Postal/ZIP code")
    country: str = Field(default="IN", description="ISO country code")


class OrderEventV1(BaseModel):
    """Baseline order event schema (v1).
    
    This is the 'expected' schema that the BigQuery table is built for.
    When upstream systems add new fields, the pipeline detects schema drift
    and the healing agent must evolve the table schema.
    
    Args (all fields):
        event_id: UUID string, auto-generated if not provided
        event_type: Always "order" (literal)
        timestamp: ISO 8601 datetime of the event
        order_id: Format "ORD-2026-XXXXX"
        customer_id: Format "CUST-XXXXX"
        product_id: Format "PROD-XXXXX"
        product_name: Human-readable product name
        category: One of "electronics", "clothing", "home", "books", "sports"
        quantity: Integer 1-100
        unit_price: Float 0.01-9999.99
        currency: "INR", "USD", or "EUR"
        total_amount: quantity * unit_price
        payment_method: "credit_card", "upi", "cod", "debit_card"
        shipping_address: Nested ShippingAddress object
        status: "placed", "confirmed", "shipped", "delivered"
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: Literal["order"] = "order"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    order_id: str
    customer_id: str
    product_id: str
    product_name: str
    category: str
    quantity: int = Field(ge=1, le=100)
    unit_price: float = Field(ge=0.01, le=9999.99)
    currency: str = Field(default="INR")
    total_amount: float
    payment_method: str
    shipping_address: ShippingAddress
    status: str = Field(default="placed")


class OrderEventV2(OrderEventV1):
    """Schema-drifted order event (v2) — Type A drift: new fields added.
    
    Inherits all V1 fields and adds:
    - loyalty_points: Upstream loyalty system integration
    - discount_code: Promotional code applied
    - estimated_delivery: Delivery ETA
    
    The healing agent must detect these new fields and run:
    ALTER TABLE ecommerce.orders ADD COLUMN loyalty_points INT64;
    ALTER TABLE ecommerce.orders ADD COLUMN discount_code STRING;
    ALTER TABLE ecommerce.orders ADD COLUMN estimated_delivery DATE;
    """
    loyalty_points: int = Field(default=0, description="Loyalty points earned")
    discount_code: Optional[str] = Field(default=None, description="Promo code applied")
    estimated_delivery: Optional[date] = Field(default=None, description="Delivery ETA")


class InventoryEvent(BaseModel):
    """Inventory update event from warehouse systems.
    
    Args:
        event_id: UUID
        event_type: Always "inventory"
        timestamp: When the inventory change occurred
        product_id: Format "PROD-XXXXX"
        warehouse_id: Format "WH-MUM-01", "WH-BLR-02", etc.
        action: "restock", "sold", "returned", "damaged"
        quantity_change: Positive (restock/return) or negative (sold/damaged)
        current_stock: Resulting stock level after change
        reorder_threshold: Stock level that triggers reorder alert
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: Literal["inventory"] = "inventory"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    product_id: str
    warehouse_id: str
    action: str
    quantity_change: int
    current_stock: int = Field(ge=0)
    reorder_threshold: int = Field(ge=0)


class UserActivityEvent(BaseModel):
    """User clickstream/activity event.
    
    Args:
        event_id: UUID
        event_type: Always "user_activity"
        timestamp: When the activity occurred
        customer_id: Format "CUST-XXXXX"
        session_id: Browser session UUID
        action: "page_view", "add_to_cart", "checkout_start", "search"
        page_url: URL path of the page
        device_type: "mobile", "desktop", "tablet"
        referrer: Optional referrer URL
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: Literal["user_activity"] = "user_activity"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    customer_id: str
    session_id: str
    action: str
    page_url: str
    device_type: str
    referrer: Optional[str] = None


# Union type for any e-commerce event
EcommerceEvent = Union[OrderEventV1, InventoryEvent, UserActivityEvent]


class ErrorEvent(BaseModel):
    """Error event published to the pipeline-errors Pub/Sub topic.
    
    Created by the Beam pipeline when an event fails validation.
    Consumed by the FastAPI gateway to trigger the healing agent.
    
    Args:
        error_id: UUID for this error occurrence
        original_event: The raw event dict that failed
        error_type: Classification of the error
        error_message: Human-readable description
        failed_at_stage: Which Beam DoFn stage caught the error
        timestamp: When the error was detected
        schema_diff: Optional dict showing expected vs actual schema
    """
    error_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_event: dict
    error_type: str  # Will be classified by triage agent into ErrorType enum
    error_message: str
    failed_at_stage: str  # "parse_json", "validate_schema", "check_quality"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    schema_diff: Optional[dict] = None
