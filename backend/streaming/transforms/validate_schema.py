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
    
        """
        missing_fields = []
        extra_fields = []
        type_mismatches = {}
        
        required_fields = [k for k, v in schema.items() if isinstance(v, dict) and v.get("required", False)]
        
        for req_field in required_fields:
            if req_field not in event:
                missing_fields.append(req_field)
                
        for field in event:
            if field not in schema:
                extra_fields.append(field)
                
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }
        
        for field, value in event.items():
            if field in schema and isinstance(schema[field], dict):
                expected_type_str = schema[field].get("type", "string")
                expected_type = type_mapping.get(expected_type_str, str)
                if value is not None and not isinstance(value, expected_type):
                    if expected_type_str == "number" and isinstance(value, int):
                        continue
                    type_mismatches[field] = {
                        "expected": expected_type_str,
                        "got": type(value).__name__
                    }
                    
        schema_diff = {}
        if missing_fields: schema_diff["missing_fields"] = missing_fields
        if extra_fields: schema_diff["extra_fields"] = extra_fields
        if type_mismatches: schema_diff["type_mismatches"] = type_mismatches
        
        return (len(schema_diff) == 0, schema_diff if schema_diff else None)


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
        
        """
        event_type = element.get("event_type")
        schema = SCHEMA_REGISTRY.get(event_type)
        if not schema:
            yield pvalue.TaggedOutput(self.ERROR_TAG, {
                "original_event": element,
                "error_type": "unknown_event_type",
                "error_message": f"No schema found for event_type: {event_type}",
                "schema_diff": {},
                "stage": "validate_schema"
            })
            return
            
        is_valid, schema_diff = validate_against_schema(element, schema)
        if is_valid:
            yield element
        else:
            yield pvalue.TaggedOutput(self.ERROR_TAG, {
                "original_event": element,
                "error_type": "schema_drift",
                "error_message": "Schema validation failed",
                "schema_diff": schema_diff,
                "stage": "validate_schema"
            })
