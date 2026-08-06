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
import random

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
    mutated = event_dict.copy()
    if anomaly_type == "null_values":
        keys = list(mutated.keys())
        if keys:
            mutated[random.choice(keys)] = None
    elif anomaly_type == "outlier_values":
        if "quantity" in mutated:
            mutated["quantity"] = 999999
        elif "unit_price" in mutated:
            mutated["unit_price"] = -100.0
    elif anomaly_type == "type_mismatches":
        if "quantity" in mutated:
            mutated["quantity"] = "not_a_number"
    elif anomaly_type == "duplicate_ids":
        mutated["event_id"] = "DUPLICATE-UUID-1234"
    elif anomaly_type == "future_timestamps":
        mutated["timestamp"] = "2099-01-01T00:00:00Z"
    elif anomaly_type == "empty_strings":
        if "product_name" in mutated:
            mutated["product_name"] = ""
        if "order_id" in mutated:
            mutated["order_id"] = ""
    else:
        raise ValueError(f"Unknown anomaly type: {anomaly_type}")
    return mutated


def inject_random_anomaly(event_dict: dict) -> tuple[dict, str]:
    """Apply a random anomaly type to an event.

    Returns:
        tuple[dict, str]: (mutated event, which anomaly type was applied)
    """
    anomaly_type = random.choice(ANOMALY_TYPES)
    return inject_anomaly(event_dict, anomaly_type), anomaly_type
