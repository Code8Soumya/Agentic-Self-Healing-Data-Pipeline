"""Injects data quality anomalies into events for testing the DQ agent.

CONNECTIONS:
- Called by: generator.py (when anomaly injection is enabled)
              api/triggers.py (POST /api/triggers/anomaly endpoint)
- Output: Events with invalid data that will fail quality checks in the Beam pipeline.

ANOMALY TYPES:
  null_values: Sets required fields to None
  outlier_values: Extreme values (quantity=999999, price=-1)
  type_mismatches: Wrong types (string where int expected)
  duplicate_ids: Reuses event_id from a previous event
  future_timestamps: Timestamps far in the future
  empty_strings: Required string fields set to ""
"""
from typing import Any

ANOMALY_TYPES = [
    "null_values",
    "outlier_values",
    "type_mismatches",
    "duplicate_ids",
    "future_timestamps",
    "empty_strings",
]


def inject_anomaly(event_dict: dict, anomaly_type: str) -> dict:
    """Apply a specific data quality anomaly to an event dict.
    
    Args:
        event_dict: A valid event dict
        anomaly_type: Type of anomaly from ANOMALY_TYPES
    
    Returns:
        dict: Event dict with data quality issues injected.
    
    LOGIC NOTES for implementer:
        - "null_values": Set random required field to None
        - "outlier_values": Set quantity=999999 or unit_price=-100
        - "type_mismatches": Set quantity="not_a_number"
        - "duplicate_ids": Set event_id to a known duplicate value
        - "future_timestamps": Set timestamp to year 2099
        - "empty_strings": Set product_name="" or order_id=""
    
    Raises:
        ValueError: If anomaly_type is not in ANOMALY_TYPES
    """
    raise NotImplementedError("TODO: Implement anomaly injection with if/elif chain")


def inject_random_anomaly(event_dict: dict) -> tuple[dict, str]:
    """Apply a random anomaly type to an event.
    
    Returns:
        tuple[dict, str]: (mutated event, which anomaly type was applied)
    """
    raise NotImplementedError("TODO: Pick random anomaly, call inject_anomaly")
