"""Beam-compatible schema definitions for event validation.

These schemas mirror the Pydantic models in app.models.events but are
formatted as dicts/BigQuery schemas for Apache Beam compatibility.
"""
from streaming.schemas.inventory_schema import INVENTORY_BQ_SCHEMA, INVENTORY_SCHEMA
from streaming.schemas.order_schema import ORDER_BQ_SCHEMA, ORDER_SCHEMA
from streaming.schemas.user_activity_schema import USER_ACTIVITY_BQ_SCHEMA, USER_ACTIVITY_SCHEMA

__all__ = [
    "INVENTORY_BQ_SCHEMA",
    "INVENTORY_SCHEMA",
    "ORDER_BQ_SCHEMA",
    "ORDER_SCHEMA",
    "USER_ACTIVITY_BQ_SCHEMA",
    "USER_ACTIVITY_SCHEMA",
]
