"""Schema validation DoFn for the Beam pipeline.

CONNECTIONS:
- Position in pipeline: SECOND transform (after ParseJson)
- Input: Parsed dict from ParseJsonDoFn
- Output (main): Schema-valid dict → feeds into CheckQualityDoFn
- Output (error): Schema-invalid events → tagged to error output for pipeline-errors topic
- Uses: streaming/schemas/*.py for schema definitions

VALIDATION LOGIC:
  1. Determine event_type from the dict
  2. Look up the corresponding schema (ORDER_SCHEMA, INVENTORY_SCHEMA, etc.)
  3. Check all required fields are present
  4. Check field types match expected types
  5. Detect extra fields (potential schema drift)
  6. If validation fails → tag to error output with schema_diff info
"""
import logging
from typing import Optional
import apache_beam as beam
from apache_beam import pvalue

from streaming.schemas import ORDER_SCHEMA, INVENTORY_SCHEMA, USER_ACTIVITY_SCHEMA

logger = logging.getLogger(__name__)

# Map event_type string to its schema
SCHEMA_REGISTRY: dict[str, dict] = {
    "order": ORDER_SCHEMA,
    "inventory": INVENTORY_SCHEMA,
    "user_activity": USER_ACTIVITY_SCHEMA,
}


def validate_against_schema(event: dict, schema: dict) -> tuple[bool, Optional[dict]]:
    """Validate an event dict against a schema definition.
    
    Args:
        event: The parsed event dict
        schema: Schema dict from streaming/schemas/
    
    Returns:
        tuple[bool, Optional[dict]]:
            (True, None) if valid
            (False, schema_diff) if invalid, where schema_diff contains:
                {
                    "missing_fields": ["field1", "field2"],
                    "extra_fields": ["unknown_field"],
                    "type_mismatches": {"field": {"expected": "int", "got": "str"}},
                }
    
    LOGIC for implementer:
        1. Get required fields from schema where required==True
        2. Check each required field exists in event
        3. Check no unexpected fields in event (fields not in schema)
        4. For each present field, check type matches schema type
        5. Build schema_diff dict with any issues found
        6. Return (len(issues) == 0, schema_diff or None)
    """
    raise NotImplementedError("TODO: Implement schema validation logic")


class ValidateSchemaDoFn(beam.DoFn):
    """Validates event dicts against registered schemas.
    
    Tagged Outputs:
        main: Schema-valid events
        schema_errors: Dict with {"original_event": dict, "error_type": "schema_drift",
                                   "error_message": str, "schema_diff": dict,
                                   "stage": "validate_schema"}
    """
    
    ERROR_TAG = "schema_errors"
    
    def process(self, element: dict) -> None:
        """Validate a single event against its schema.
        
        Args:
            element: Parsed event dict from ParseJsonDoFn
        
        Yields:
            dict: Valid event (main output)
            pvalue.TaggedOutput: Error info (ERROR_TAG output)
        
        LOGIC for implementer:
            1. event_type = element.get("event_type")
            2. schema = SCHEMA_REGISTRY.get(event_type)
            3. If no schema found → yield error (unknown event type)
            4. is_valid, schema_diff = validate_against_schema(element, schema)
            5. If valid → yield element
            6. If invalid → yield TaggedOutput with error details + schema_diff
        """
        raise NotImplementedError("TODO: Implement schema validation DoFn")
