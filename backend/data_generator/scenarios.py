"""Pre-defined failure scenarios for testing and demos.

CONNECTIONS:
- Imported by: generator.py (to run specific failure scenarios)
              scripts/inject_drift.sh (to trigger specific scenarios)
              tests/evaluation/scenarios.json (references these scenario names)

Each scenario defines:
  - A name and description
  - Which event type to target
  - Which drift/anomaly type to inject
  - Expected agent behavior (for evaluation)
"""
from dataclasses import dataclass, field
from app.models.enums import DriftType, ErrorType


@dataclass
class ScenarioConfig:
    """Configuration for a single failure scenario.
    
    Args:
        name: Unique scenario identifier
        description: Human-readable description
        event_type: Which event type to generate ("order", "inventory", "user_activity")
        failure_mode: "drift" or "anomaly"
        drift_type: If failure_mode=="drift", which DriftType to inject
        anomaly_type: If failure_mode=="anomaly", which anomaly type
        expected_error_type: What the triage agent should classify this as
        expected_auto_heal: Whether the agent should auto-heal (True) or escalate (False)
        expected_confidence_min: Minimum expected confidence score
    """
    name: str
    description: str
    event_type: str = "order"
    failure_mode: str = "drift"  # "drift" or "anomaly"
    drift_type: DriftType | None = None
    anomaly_type: str | None = None
    expected_error_type: ErrorType = ErrorType.SCHEMA_DRIFT
    expected_auto_heal: bool = True
    expected_confidence_min: float = 0.8


# ── Pre-defined scenarios for demos and testing ──
SCENARIOS: list[ScenarioConfig] = [
    ScenarioConfig(
        name="drift_type_a_new_field",
        description="Upstream adds loyalty_points and discount_code fields to orders",
        drift_type=DriftType.NEW_FIELD,
        expected_auto_heal=True,
        expected_confidence_min=0.95,
    ),
    ScenarioConfig(
        name="drift_type_b_renamed_field",
        description="unit_price renamed to price_per_unit",
        drift_type=DriftType.RENAMED_FIELD,
        expected_auto_heal=True,
        expected_confidence_min=0.85,
    ),
    ScenarioConfig(
        name="drift_type_c_type_change",
        description="quantity field changed from INT to STRING",
        drift_type=DriftType.TYPE_CHANGE,
        expected_auto_heal=True,
        expected_confidence_min=0.80,
    ),
    ScenarioConfig(
        name="drift_type_d_dropped_field",
        description="shipping_address field removed entirely",
        drift_type=DriftType.DROPPED_FIELD,
        expected_error_type=ErrorType.SCHEMA_DRIFT,
        expected_auto_heal=False,  # Should escalate to HITL
        expected_confidence_min=0.50,
    ),
    ScenarioConfig(
        name="drift_type_e_nested_change",
        description="New fields added to shipping_address sub-object",
        drift_type=DriftType.NESTED_CHANGE,
        expected_auto_heal=False,  # Should escalate to HITL
        expected_confidence_min=0.60,
    ),
    ScenarioConfig(
        name="dq_null_values",
        description="Required fields set to null",
        failure_mode="anomaly",
        anomaly_type="null_values",
        expected_error_type=ErrorType.DATA_QUALITY,
        expected_auto_heal=True,
        expected_confidence_min=0.90,
    ),
    ScenarioConfig(
        name="dq_outlier_values",
        description="Extreme values in numeric fields",
        failure_mode="anomaly",
        anomaly_type="outlier_values",
        expected_error_type=ErrorType.DATA_QUALITY,
        expected_auto_heal=True,
        expected_confidence_min=0.85,
    ),
]
