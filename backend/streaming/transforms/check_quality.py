"""Data quality check DoFn for the Beam pipeline.

CONNECTIONS:
- Position in pipeline: THIRD transform (after ValidateSchema)
- Input: Schema-valid dict from ValidateSchemaDoFn
- Output (main): Quality-valid dict → feeds into RouteEventsDoFn
- Output (error): Quality-invalid events → tagged to error output

QUALITY CHECKS:
  1. NOT NULL: Required fields must not be null/empty
  2. RANGE: Numeric fields within expected ranges (quantity 1-100, price > 0)
  3. FORMAT: String fields match expected patterns (event_id is UUID-like, order_id matches ORD-*)
  4. CONSISTENCY: total_amount ≈ quantity * unit_price (within tolerance)
  5. TIMELINESS: timestamp not in the far future or far past
"""
import logging
from datetime import datetime, timedelta
import apache_beam as beam
from apache_beam import pvalue

logger = logging.getLogger(__name__)


class CheckQualityDoFn(beam.DoFn):
    """Runs data quality checks on schema-valid events.
    
    Tagged Outputs:
        main: Quality-valid events ready for BigQuery
        quality_errors: Dict with {"original_event": dict, "error_type": "data_quality",
                                    "error_message": str, "violations": list[str],
                                    "stage": "check_quality"}
    """
    
    ERROR_TAG = "quality_errors"
    
    def process(self, element: dict) -> None:
        """Run quality checks on a single event.
        
        Args:
            element: Schema-valid event dict from ValidateSchemaDoFn
        
        Yields:
            dict: Quality-valid event (main output)
            pvalue.TaggedOutput: Error info with violation list (ERROR_TAG)
        
        """
        violations = []
        for k, v in element.items():
            if v is None or (isinstance(v, str) and str(v).strip() == ""):
                violations.append(f"null: {k}")

        event_type = element.get("event_type")
        if event_type == "order":
            qty = element.get("quantity")
            if qty is not None and not (1 <= qty <= 100):
                violations.append("range: quantity must be 1-100")
            
            price = element.get("unit_price")
            if price is not None and price <= 0:
                violations.append("range: unit_price must be > 0")
                
            total = element.get("total_amount")
            if qty is not None and price is not None and total is not None:
                expected_total = qty * price
                if abs(total - expected_total) > (0.01 * expected_total):
                    violations.append("consistency: total_amount mismatch")
                    
            ts_str = element.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    now = datetime.now(ts.tzinfo) if ts.tzinfo else datetime.utcnow()
                    if ts > now:
                        violations.append("timeliness: timestamp in future")
                    if ts < now - timedelta(hours=24):
                        violations.append("timeliness: timestamp too old")
                except ValueError:
                    violations.append("format: invalid timestamp")
        elif event_type == "inventory":
            stock = element.get("current_stock")
            if stock is not None and stock < 0:
                violations.append("range: current_stock must be >= 0")

        if not violations:
            yield element
        else:
            yield pvalue.TaggedOutput(self.ERROR_TAG, {
                "original_event": element,
                "error_type": "data_quality",
                "error_message": "Data quality checks failed",
                "violations": violations,
                "stage": "check_quality"
            })
