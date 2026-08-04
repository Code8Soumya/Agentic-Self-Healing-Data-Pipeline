"""Enumerations used across the entire pipeline.

CONNECTIONS:
- Imported by: models/events.py, models/healing.py, agents/state.py,
              agents/nodes/*.py, agents/edges/*.py, api/*.py, frontend types.ts
- These enums are the SINGLE SOURCE OF TRUTH for all categorical values.
  If you add a new enum value, you must also update the corresponding
  TypeScript type in frontend/src/lib/types.ts.
"""
from enum import Enum


class ErrorType(str, Enum):
    """Types of pipeline errors the healing agent can handle.
    
    Used by: Triage agent to classify errors, routing edges to select specialist agent.
    """
    SCHEMA_DRIFT = "schema_drift"
    DATA_QUALITY = "data_quality"
    INFRA_FAILURE = "infra_failure"


class DriftType(str, Enum):
    """Specific types of schema drift that can occur.
    
    Used by: drift_injector.py to generate test scenarios,
             schema_evolution agent to determine fix strategy.
    """
    NEW_FIELD = "new_field"           # Type A: upstream adds new columns
    RENAMED_FIELD = "renamed_field"   # Type B: column name changes
    TYPE_CHANGE = "type_change"       # Type C: data type changes (int → str)
    DROPPED_FIELD = "dropped_field"   # Type D: required field removed → HITL
    NESTED_CHANGE = "nested_change"   # Type E: object structure changes → HITL


class Severity(str, Enum):
    """Severity levels for pipeline errors.
    
    Used by: Triage agent output, confidence gate routing, dashboard display.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplexityLevel(str, Enum):
    """Complexity classification for determining which LLM to use.
    
    Used by: Triage agent output → routes to Gemini Flash (simple) or Pro (complex).
    """
    SIMPLE = "simple"
    COMPLEX = "complex"


class EventType(str, Enum):
    """Types of e-commerce events flowing through the pipeline.
    
    Used by: Data generators, Beam pipeline schema validation.
    """
    ORDER = "order"
    INVENTORY = "inventory"
    USER_ACTIVITY = "user_activity"


class ApprovalStatus(str, Enum):
    """Status of a human-in-the-loop approval request.
    
    Used by: Firestore documents, API endpoints, dashboard display.
    """
    AUTO_APPROVED = "auto_approved"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
