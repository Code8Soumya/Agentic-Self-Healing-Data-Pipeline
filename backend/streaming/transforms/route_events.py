"""Event routing DoFn / transform for the Beam pipeline.

CONNECTIONS:
- Position in pipeline: FINAL transform — routes events to their destinations
- Input (valid): Quality-valid events from CheckQualityDoFn → writes to BigQuery
- Input (errors): Aggregated errors from all stages → publishes to error Pub/Sub topic

ROUTING LOGIC:
  Valid events → BigQuery Iceberg managed table (based on event_type)
  Error events → Pub/Sub pipeline-errors topic (as JSON, for the healing agent)

BIGQUERY WRITE:
  - Flattens nested objects (shipping_address → shipping_city, shipping_state, etc.)
  - Adds ingested_at timestamp
  - Uses streaming inserts or Storage Write API
"""
import json
import logging
from datetime import datetime

import apache_beam as beam

logger = logging.getLogger(__name__)


def flatten_order_for_bq(event: dict) -> dict:
    """Flatten a nested order event dict for BigQuery insertion.

    BigQuery tables store flat columns, so nested shipping_address must be
    flattened to shipping_city, shipping_state, shipping_pincode.

    Args:
        event: Parsed order event dict with nested shipping_address

    Returns:
        dict: Flat dict matching BigQuery orders table schema, with:
            - shipping_address removed
            - shipping_city, shipping_state, shipping_pincode added
            - ingested_at added as current UTC timestamp
            - event_type removed (not stored in BQ)

    """
    flat = event.copy()
    address = flat.pop("shipping_address", {})
    if isinstance(address, dict):
        flat["shipping_city"] = address.get("city", "")
        flat["shipping_state"] = address.get("state", "")
        flat["shipping_pincode"] = address.get("pincode", "")
    else:
        flat["shipping_city"] = ""
        flat["shipping_state"] = ""
        flat["shipping_pincode"] = ""
    flat.pop("event_type", None)
    flat["ingested_at"] = datetime.utcnow().isoformat()
    return flat


def format_error_for_pubsub(error: dict) -> bytes:
    """Serialize an error dict to JSON bytes for Pub/Sub publishing.

    Args:
        error: Error dict from any DoFn's error tagged output

    Returns:
        bytes: JSON-encoded error message ready for Pub/Sub

    """
    return json.dumps(error, default=str).encode("utf-8")


class RouteValidEventsDoFn(beam.DoFn):
    """Routes valid events to the correct BigQuery table.

    For order events: flattens nested address, writes to ecommerce.orders
    For inventory events: writes to ecommerce.inventory (if table exists)
    For user activity: writes to ecommerce.user_activity (if table exists)

    NOTE: In Phase 1, we only write orders to BigQuery.
    Inventory and user_activity tables are Phase 2+ additions.
    """

    def process(self, element: dict) -> None:
        """Route a valid event for BigQuery write.

        Args:
            element: Quality-valid event dict

        Yields:
            dict: Flattened dict ready for BigQuery WriteToBigQuery transform

        """
        event_type = element.get("event_type", "order")
        if event_type == "order":
            yield flatten_order_for_bq(element)
        else:
            flat = element.copy()
            flat["ingested_at"] = datetime.utcnow().isoformat()
            yield flat
