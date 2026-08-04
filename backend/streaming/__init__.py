"""Apache Beam streaming pipeline for e-commerce event processing.

This package implements the Dataflow pipeline that:
1. Reads events from Pub/Sub (raw-ecommerce-events topic)
2. Parses JSON messages
3. Validates against registered schemas
4. Checks data quality rules
5. Routes valid events to BigQuery and invalid events to error topic
"""
