"""Injects schema drift into events for testing the healing agent.

CONNECTIONS:
- Imports: app.models.enums.DriftType
- Called by: generator.py (when drift injection is enabled)
              api/triggers.py (POST /api/triggers/drift endpoint)
- Output: Modified events that will FAIL schema validation in the Beam pipeline,
          causing them to be routed to the pipeline-errors Pub/Sub topic,
          which triggers the healing agent.

DRIFT TYPES:
  A (new_field): Adds fields like loyalty_points, discount_code
  B (renamed_field): Renames unit_price -> price_per_unit
  C (type_change): Changes quantity from int to string
  D (dropped_field): Removes shipping_address entirely -> HITL escalation
  E (nested_change): Adds fields to shipping_address sub-object
"""
import random
from typing import Any
from app.models.enums import DriftType


def inject_drift(event_dict: dict, drift_type: DriftType) -> dict:
    """Apply a specific schema drift mutation to an event dict.
    
    Takes a valid event dict and mutates it to simulate upstream schema drift.
    The mutated event will fail validation in the Beam pipeline.
    
    Args:
        event_dict: A valid event serialized as dict (e.g., OrderEventV1.model_dump())
        drift_type: The type of drift to inject (DriftType enum)
    
    Returns:
        dict: The mutated event dict with schema drift applied.
              The dict is intentionally invalid against the current BigQuery schema.
    
    LOGIC NOTES for implementer:
        - DriftType.NEW_FIELD: Add {"loyalty_points": random_int, "discount_code": "SAVE10"}
        - DriftType.RENAMED_FIELD: Pop "unit_price", add "price_per_unit" with same value
        - DriftType.TYPE_CHANGE: Convert event_dict["quantity"] from int to str
        - DriftType.DROPPED_FIELD: Pop "shipping_address" entirely
        - DriftType.NESTED_CHANGE: Add new keys to shipping_address: {"landmark": ..., "floor": ...}
    
    Raises:
        ValueError: If drift_type is not a valid DriftType
    """
    mutated = event_dict.copy()
    if drift_type == DriftType.NEW_FIELD:
        mutated["loyalty_points"] = random.randint(10, 100)
        mutated["discount_code"] = "SAVE10"
    elif drift_type == DriftType.RENAMED_FIELD:
        if "unit_price" in mutated:
            mutated["price_per_unit"] = mutated.pop("unit_price")
    elif drift_type == DriftType.TYPE_CHANGE:
        if "quantity" in mutated:
            mutated["quantity"] = str(mutated["quantity"])
    elif drift_type == DriftType.DROPPED_FIELD:
        if "shipping_address" in mutated:
            mutated.pop("shipping_address")
    elif drift_type == DriftType.NESTED_CHANGE:
        if "shipping_address" in mutated:
            mutated["shipping_address"]["landmark"] = "Near Park"
            mutated["shipping_address"]["floor"] = random.randint(1, 10)
    else:
        raise ValueError(f"Unknown DriftType: {drift_type}")
    return mutated


def inject_random_drift(event_dict: dict) -> tuple[dict, DriftType]:
    """Apply a random drift type to an event.
    
    Args:
        event_dict: A valid event dict
    
    Returns:
        tuple[dict, DriftType]: (mutated event, which drift type was applied)
    """
    drift_type = random.choice(list(DriftType))
    return inject_drift(event_dict, drift_type), drift_type
