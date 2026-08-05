"""Main Apache Beam streaming pipeline.

CONNECTIONS:
- Uses all transforms: ParseJsonDoFn → ValidateSchemaDoFn → CheckQualityDoFn → RouteValidEventsDoFn
- Reads from: Pub/Sub topic 'raw-ecommerce-events'
- Writes to: BigQuery 'ecommerce.orders' (valid events)
- Publishes to: Pub/Sub topic 'pipeline-errors' (invalid events)
- Deployed via: infra/terraform/dataflow.tf (DataflowRunner)
- Tested via: Makefile 'make run-pipeline-local' (DirectRunner)

PIPELINE TOPOLOGY:
  PubSub Read → ParseJson → ValidateSchema → CheckQuality → RouteToBigQuery
                    ↓               ↓               ↓
              parse_errors    schema_errors    quality_errors
                    ↓               ↓               ↓
                    └───────────────┴───────────────┘
                                    ↓
                            Merge All Errors
                                    ↓
                          Format as JSON bytes
                                    ↓
                       Write to Pub/Sub error topic

RUNNERS:
  - DirectRunner: Local testing (make run-pipeline-local)
  - DataflowRunner: GCP deployment (make run-pipeline-gcp)

USAGE:
  # Local testing
  python -m streaming.pipeline --runner DirectRunner
  
  # GCP deployment
  python -m streaming.pipeline \
    --runner DataflowRunner \
    --project YOUR_PROJECT_ID \
    --region asia-south1 \
    --temp_location gs://YOUR_BUCKET/temp \
    --staging_location gs://YOUR_BUCKET/staging
"""
import argparse
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, GoogleCloudOptions
from apache_beam.io import ReadFromPubSub, WriteToBigQuery, WriteToPubSub

from streaming.transforms.parse_json import ParseJsonDoFn
from streaming.transforms.validate_schema import ValidateSchemaDoFn
from streaming.transforms.check_quality import CheckQualityDoFn
from streaming.transforms.route_events import RouteValidEventsDoFn, format_error_for_pubsub
from streaming.schemas import ORDER_BQ_SCHEMA

logger = logging.getLogger(__name__)


def build_pipeline(options: PipelineOptions, project_id: str, region: str = "asia-south1") -> beam.Pipeline:
    """Build and return the complete streaming pipeline (but don't run it).
    
    Args:
        options: Beam PipelineOptions (DirectRunner or DataflowRunner)
        project_id: GCP project ID for Pub/Sub and BigQuery
        region: GCP region (default: asia-south1)
    
    Returns:
        beam.Pipeline: Fully constructed pipeline ready to run.
    
        """
        p = beam.Pipeline(options=options)
        
        raw_messages = p | "ReadFromPubSub" >> ReadFromPubSub(
            topic=f"projects/{project_id}/topics/raw-ecommerce-events"
        )
        
        parse_result = raw_messages | "ParseJSON" >> beam.ParDo(ParseJsonDoFn()).with_outputs(
            ParseJsonDoFn.ERROR_TAG, main="parsed"
        )
        
        validate_result = parse_result.parsed | "ValidateSchema" >> beam.ParDo(ValidateSchemaDoFn()).with_outputs(
            ValidateSchemaDoFn.ERROR_TAG, main="valid_schema"
        )
        
        quality_result = validate_result.valid_schema | "CheckQuality" >> beam.ParDo(CheckQualityDoFn()).with_outputs(
            CheckQualityDoFn.ERROR_TAG, main="valid_quality"
        )
        
        bq_rows = quality_result.valid_quality | "RouteValidEvents" >> beam.ParDo(RouteValidEventsDoFn())
        bq_rows | "WriteToBigQuery" >> WriteToBigQuery(
            table=f"{project_id}:ecommerce.orders",
            schema=ORDER_BQ_SCHEMA,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
        )
        
        all_errors = (
            (parse_result[ParseJsonDoFn.ERROR_TAG],
             validate_result[ValidateSchemaDoFn.ERROR_TAG],
             quality_result[CheckQualityDoFn.ERROR_TAG])
            | "MergeErrors" >> beam.Flatten()
        )
        
        all_errors | "FormatErrors" >> beam.Map(format_error_for_pubsub) | "WriteErrorsToPubSub" >> WriteToPubSub(
            topic=f"projects/{project_id}/topics/pipeline-errors"
        )
        
        return p


def run() -> None:
    """Entry point: parse CLI args, build pipeline, and run.
    
    CLI Args:
        --project: GCP project ID
        --region: GCP region (default: asia-south1)
        Standard Beam args: --runner, --temp_location, --staging_location, etc.
    
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--project", required=True, help="GCP project ID")
        parser.add_argument("--region", default="asia-south1", help="GCP region")
        
        known_args, pipeline_args = parser.parse_known_args()
        
        options = PipelineOptions(pipeline_args)
        if options.view_as(StandardOptions).runner == "DataflowRunner":
            options.view_as(StandardOptions).streaming = True
            
        pipeline = build_pipeline(options, known_args.project, known_args.region)
        result = pipeline.run()
        
        if options.view_as(StandardOptions).runner != "DataflowRunner":
            result.wait_until_finish()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
