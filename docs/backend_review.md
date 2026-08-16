# Backend Architecture & Codebase Review

This document provides a detailed review of the `backend` directory in the Agentic Self-Healing Data Pipeline project. It documents all files, their functions/classes, their purpose, and how they connect to the overall architecture.

## Overview
The `backend` currently consists of three main modules (Phase 1 implementation):
1. **`app/`**: Core configuration, Pydantic models (data domain, events, healing states), and enumerations.
2. **`data_generator/`**: A mock data generator simulating e-commerce traffic, capable of injecting schema drift and data quality anomalies.
3. **`streaming/`**: An Apache Beam pipeline that consumes from Pub/Sub, validates schemas, checks data quality, and routes valid events to BigQuery and errors to a separate Pub/Sub topic for the agent to heal.

---

## 1. `app/` Module
This module contains the domain models, shared enumerations, and configuration used across the entire backend.

### `app/config.py`
**Purpose**: Central application configuration using Pydantic Settings. Reads from environment variables or `.env` files.
- `Settings`: Pydantic class defining GCP core config, BigQuery tables, Pub/Sub topics, LLM settings, etc.
- `get_settings()`: Uses `@lru_cache` to return a singleton instance of the `Settings` class. Used by all other modules to fetch config (e.g., topic names).

### `app/models/enums.py`
**Purpose**: The single source of truth for all categorical values.
- `ErrorType`: Classifies pipeline errors (`SCHEMA_DRIFT`, `DATA_QUALITY`, `INFRA_FAILURE`).
- `DriftType`: Types of schema drift (`NEW_FIELD`, `RENAMED_FIELD`, `TYPE_CHANGE`, `DROPPED_FIELD`, `NESTED_CHANGE`).
- `Severity`: Error severities (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `ComplexityLevel`: Determines LLM routing (`SIMPLE` -> Gemini Flash, `COMPLEX` -> Gemini Pro).
- `EventType`: `ORDER`, `INVENTORY`, `USER_ACTIVITY`.
- `ApprovalStatus`: State of Human-In-The-Loop approvals (`PENDING`, `APPROVED`, `REJECTED`, etc.).

### `app/models/events.py`
**Purpose**: Defines Pydantic models for valid and invalid e-commerce events. These are used for validation in the Beam pipeline and generation in `data_generator/`.
- `ShippingAddress`: Sub-model for order addresses.
- `OrderEventV1`: The baseline expected order schema.
- `OrderEventV2`: Simulates Type A drift (new fields added).
- `InventoryEvent` / `UserActivityEvent`: Models for other event types.
- `ErrorEvent`: Wraps failed events routed to the `pipeline-errors` Pub/Sub topic to trigger the healing agent.

### `app/models/healing.py`
**Purpose**: Models for tracking agentic healing lifecycles and Human-in-the-Loop approvals.
- `HealingResult`: Full record of an agent's diagnosis, fix, and verification (saved to BigQuery `healing_events`).
- `ApprovalRequest`: Pending approvals stored in Firestore.
- `ApprovalDetail`: Extended info for the dashboard UI.

### `app/models/trajectory.py`
**Purpose**: Tracking agent steps for evaluation and observability.
- `AgentStep`: Tracks an individual execution step (node name, tool calls, token usage, duration).
- `TrajectoryScore`: Evaluates the agent's performance (task completion, efficiency, cost, etc.) and writes to BigQuery.

---

## 2. `data_generator/` Module
This module simulates real-world e-commerce data streams and intentionally injects errors (drift and anomalies) to test the agentic healing pipeline.

### `data_generator/order_events.py`
- `generate_order_event()`: Creates a single realistic `OrderEventV1` with randomly selected products, cities, and quantities.
- `generate_order_batch(count)`: Returns a list of generated order events.

### `data_generator/inventory_events.py`
- `generate_inventory_event()`: Creates an `InventoryEvent` mimicking warehouse updates.
- `generate_inventory_batch(count)`: Returns a list of generated inventory events.

### `data_generator/user_activity_events.py`
- `generate_user_activity_event()`: Creates a `UserActivityEvent` mimicking clickstream data.
- `generate_user_activity_batch(count)`: Returns a list of generated activity events.

### `data_generator/drift_injector.py`
**Purpose**: Mutates valid events into invalid ones to simulate schema drift.
- `inject_drift(event_dict, drift_type)`: Applies a specific `DriftType` mutation (e.g. adding a field, renaming a field, changing an int to a str).
- `inject_random_drift(event_dict)`: Picks a random drift type and applies it.

### `data_generator/anomaly_injector.py`
**Purpose**: Mutates valid events into invalid ones to simulate data quality anomalies.
- `inject_anomaly(event_dict, anomaly_type)`: Applies anomalies (e.g. setting required fields to null, negative prices, future timestamps).
- `inject_random_anomaly(event_dict)`: Picks a random anomaly type and applies it.

### `data_generator/scenarios.py`
**Purpose**: Pre-defined failure scenarios for end-to-end evaluation and demos.
- `ScenarioConfig`: Dataclass defining a scenario (name, drift/anomaly type, expected agent behavior, and expected confidence).
- `SCENARIOS`: A list of pre-configured scenarios used by the evaluator and `generator.py`.

### `data_generator/generator.py`
**Purpose**: The main orchestrator that uses the above files to generate continuous data traffic and publish it to Pub/Sub.
- `EventGeneratorOrchestrator`:
  - `generate_single_event()`: Uses a weighted mix to pick an event type, generates it, and optionally runs it through drift/anomaly injectors based on configured rates.
  - `publish_event(event_dict)`: Serializes and publishes the event to the `raw-ecommerce-events` topic.
  - `run(...)`: Runs a loop generating and publishing events at a specified rate (events/sec) for a duration.
  - `run_scenario(...)`: Specifically generates events for a pre-defined scenario from `scenarios.py`.
- `main()`: CLI entry point handling argument parsing (`--events-per-second`, `--drift-rate`, etc.) and executing the orchestrator.

---

## 3. `streaming/` Module
This module contains the Apache Beam pipeline that acts as the entry point of the data layer. It consumes the raw events, processes them, and routes them.

### `streaming/pipeline.py`
**Purpose**: The main Beam pipeline definition.
- `build_pipeline(options, project_id, region)`: Constructs the topology:
  1. `ReadFromPubSub` -> `ParseJsonDoFn`
  2. Main output -> `ValidateSchemaDoFn`
  3. Main output -> `CheckQualityDoFn`
  4. Main output -> `RouteValidEventsDoFn` -> `WriteToBigQuery`
  5. Error outputs from all three DoFns are flattened, formatted by `format_error_for_pubsub`, and routed to `WriteToPubSub` (`pipeline-errors` topic).
- `run()`: Entry point to build and execute the pipeline on either `DirectRunner` or `DataflowRunner`.

### `streaming/schemas/`
**Purpose**: JSON-schema-like dictionaries and BigQuery schema strings.
- **`order_schema.py`**: Defines `ORDER_SCHEMA` for runtime validation and `ORDER_BQ_SCHEMA` for BigQuery writes.
- **`inventory_schema.py`**: Schema for inventory.
- **`user_activity_schema.py`**: Schema for user activity.

### `streaming/transforms/parse_json.py`
- `ParseJsonDoFn.process(element)`: Parses raw bytes from Pub/Sub into a Python dictionary. If it fails (e.g. malformed JSON), it yields to the `ERROR_TAG` side-output.

### `streaming/transforms/validate_schema.py`
- `validate_against_schema(event, schema)`: Compares an event dictionary against the required fields and types defined in `streaming/schemas`. Returns a boolean and a `schema_diff`.
- `ValidateSchemaDoFn.process(element)`: Looks up the schema based on `event_type` and runs validation. Yields valid events to the main output, and schema drift failures to the `ERROR_TAG` side-output.

### `streaming/transforms/check_quality.py`
- `CheckQualityDoFn.process(element)`: Runs business logic validations (e.g., numeric boundaries, timestamp constraints, data consistency). Yields valid events to the main output, and data anomalies to the `ERROR_TAG` side-output.

### `streaming/transforms/route_events.py`
- `flatten_order_for_bq(event)`: BigQuery doesn't handle nested objects smoothly without strict schemas, so this function flattens `shipping_address` into `shipping_city`, `shipping_state`, etc.
- `format_error_for_pubsub(error)`: Converts the error dictionaries into JSON bytes.
- `RouteValidEventsDoFn.process(element)`: The final routing logic for valid events before they are passed to the `WriteToBigQuery` transform.

---

## Architecture Flow Summary
1. **Generation**: `generator.py` spins up events using models in `data_generator/` and publishes them as JSON strings to Pub/Sub (`raw-ecommerce-events`).
2. **Ingestion & Parsing**: `streaming/pipeline.py` reads these events using Dataflow (Beam). `ParseJsonDoFn` attempts to deserialize them.
3. **Validation**: `ValidateSchemaDoFn` ensures they match expected shapes (`streaming/schemas/`), rejecting `DriftType` mutations.
4. **Quality Checks**: `CheckQualityDoFn` enforces business rules, rejecting data anomalies.
5. **Routing**:
   - **Happy Path**: `RouteValidEventsDoFn` flattens data and writes directly to BigQuery (`ecommerce.orders`).
   - **Sad Path (Healing Trigger)**: All rejected events from parsing, validation, and quality checks are flattened and pushed to the `pipeline-errors` Pub/Sub topic, which acts as the trigger for the LangGraph/ADK healing agents (Phase 3).
