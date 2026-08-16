# Phase 1: GCP Foundation + Data Layer Detailed Implementation Plan

## Overview
This document breaks down the implementation of **Phase 1** of the Agentic Self-Healing Data Pipeline project. It details the responsibilities split between the AI (coding) and the User (GCP Console, CLI execution), providing a step-by-step roadmap for Week 1-2.

**Goal:** Establish a working Dataflow streaming pipeline that reads events from Pub/Sub, validates schemas, writes clean data to BigQuery (Iceberg), and routes error events to an error topic.

---

## Task Allocation Breakdown

### 🤖 To Be Done by AI (Code Generation)
The AI assistant will write the necessary code, scripts, and configurations for the following tasks:
1. **Bootstrap Scripts:**
   - `scripts/setup_gcp.sh`: Script to enable required GCP APIs.
2. **Infrastructure as Code (Terraform):**
   - `infra/terraform/main.tf`: Provider setup and GCS buckets.
   - `infra/terraform/pubsub.tf`: Topics (`raw-ecommerce-events`, `pipeline-errors`) and subscriptions.
   - `infra/terraform/bigquery.tf`: Datasets and Iceberg managed tables (`orders`, `healing_events`, `trajectory_scores`).
   - `infra/terraform/iam.tf`: Service accounts and roles for Dataflow and Cloud Run.
   - `infra/terraform/dataflow.tf`: Deployment configs for the Dataflow pipeline.
3. **Data Event Generators (Python):**
   - Data models (`backend/app/models/events.py`).
   - Generators for orders, inventory, and user activity (`backend/data_generator/*.py`).
   - Drift and anomaly injectors for testing (`drift_injector.py`, `anomaly_injector.py`).
   - Generator orchestrator (`generator.py`).
4. **Dataflow Streaming Pipeline (Python / Apache Beam):**
   - Beam schemas and transforms (parse, validate, route).
   - Main pipeline definition (`backend/streaming/pipeline.py`).

### 👤 To Be Done by User (GCP Console, CLI, Execution)
The user will handle tasks requiring manual authentication, GCP Console interaction, and local execution:
1. **GCP Project Setup (Console):**
   - Create a new Google Cloud Project.
   - Ensure a Billing Account is linked to the project.
2. **Local Environment Setup (CLI):**
   - Install `gcloud` CLI, `terraform`, and `python` locally.
   - Authenticate with Google Cloud: 
     ```bash
     gcloud auth login
     gcloud auth application-default login
     gcloud config set project YOUR_PROJECT_ID
     ```
3. **Running the Scripts (CLI):**
   - Execute the setup script written by AI: `bash scripts/setup_gcp.sh`.
4. **Applying Infrastructure (CLI):**
   - Navigate to the terraform directory.
   - Run `terraform init`.
   - Run `terraform plan` and review changes.
   - Run `terraform apply` to provision GCP resources.
5. **Testing and Verification (Console & CLI):**
   - Run the Python data generator to produce mock events.
   - Monitor the **Cloud Dataflow** job status in the GCP Console.
   - Query **BigQuery** in the GCP Console to verify clean events arrive.
   - Check the **Pub/Sub** `pipeline-errors` topic for rejected events.

---

## Step-by-Step Execution Plan

### Step 1: Initial Setup
- **User:** Create a GCP Project and enable billing in the GCP Console. Note the `PROJECT_ID`.
- **AI:** Write `scripts/setup_gcp.sh` to enable APIs (Compute, Pub/Sub, Dataflow, BigQuery, IAM).
- **User:** Authenticate locally and run `scripts/setup_gcp.sh`.

### Step 2: Infrastructure Provisioning
- **AI:** Write all Terraform files in `infra/terraform/`.
- **User:** Run `terraform apply` to create Pub/Sub topics, BigQuery tables, GCS buckets, and IAM roles.

### Step 3: Data Generator Implementation
- **AI:** Write Python classes for event generation (`backend/data_generator/`).
- **User:** Set up Python virtual environment (`.venv`), install dependencies (e.g., `google-cloud-pubsub`, `pydantic`), and verify the generator script runs without errors.

### Step 4: Dataflow Pipeline Implementation
- **AI:** Write the Apache Beam pipeline in `backend/streaming/`.
- **User:** Deploy the Dataflow job via CLI (`python pipeline.py --runner DataflowRunner ...`).

### Step 5: End-to-End Testing
- **User:** Run the event generator in the background.
- **User:** Observe the Dataflow pipeline topology in the GCP Console.
- **User:** Verify that `ecommerce.orders` in BigQuery is populating.
- **User:** Use the AI-built drift injector to send a malformed event.
- **User:** Verify the malformed event appears in the `pipeline-errors` Pub/Sub topic.

---

> **Note to User:** Once you approve this plan, we can begin executing Step 1 and Step 2 by having the AI write the initialization script and the Terraform configurations.
