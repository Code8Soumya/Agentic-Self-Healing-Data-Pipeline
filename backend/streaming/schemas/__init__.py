"""Beam-compatible schema definitions for event validation.

These schemas mirror the Pydantic models in app.models.events but are
formatted as dicts/BigQuery schemas for Apache Beam compatibility.
"""
from streaming.schemas.order_schema import ORDER_SCHEMA, ORDER_BQ_SCHEMA
from streaming.schemas.inventory_schema import INVENTORY_SCHEMA, INVENTORY_BQ_SCHEMA
from streaming.schemas.user_activity_schema import USER_ACTIVITY_SCHEMA, USER_ACTIVITY_BQ_SCHEMA
