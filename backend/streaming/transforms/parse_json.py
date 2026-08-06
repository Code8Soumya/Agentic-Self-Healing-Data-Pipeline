"""JSON parsing DoFn for the Beam pipeline.

CONNECTIONS:
- Position in pipeline: FIRST transform after Pub/Sub read
- Input: Raw bytes from Pub/Sub message
- Output (main): Parsed dict → feeds into ValidateSchemaDoFn
- Output (error): Unparseable messages → tagged to error output for the error topic

ERROR HANDLING:
  If JSON parsing fails, the message is tagged to a side output ('parse_errors')
  and published to the pipeline-errors Pub/Sub topic by the router.
"""
import json
import logging

import apache_beam as beam
from apache_beam import pvalue

logger = logging.getLogger(__name__)


class ParseJsonDoFn(beam.DoFn):
    """Parses raw Pub/Sub message bytes into Python dicts.

    Beam DoFn that:
    1. Decodes bytes to UTF-8 string
    2. Parses JSON string to dict
    3. Yields the dict to main output
    4. On failure, yields error info to tagged output 'parse_errors'

    Tagged Outputs:
        main: Successfully parsed dict
        parse_errors: Dict with {"raw_message": str, "error": str, "stage": "parse_json"}
    """

    # Define tagged output for errors
    ERROR_TAG = "parse_errors"

    def process(self, element: bytes) -> None:
        """Parse a single Pub/Sub message.

        Args:
            element: Raw bytes from Pub/Sub ReadFromPubSub

        Yields:
            dict: Parsed event dict (main output)
            pvalue.TaggedOutput: Error info (ERROR_TAG output)

        """
        try:
            decoded = element.decode("utf-8")
            parsed = json.loads(decoded)
            yield parsed
        except Exception as e:
            if isinstance(element, bytes):
                raw_msg = element.decode("utf-8", errors="replace")[:1000]
            else:
                raw_msg = str(element)[:1000]
            yield pvalue.TaggedOutput(self.ERROR_TAG, {
                "raw_message": raw_msg,
                "error": str(e),
                "stage": "parse_json"
            })
