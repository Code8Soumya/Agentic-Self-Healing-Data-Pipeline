#!/bin/bash
set -e

# Takes PROJECT_ID as argument or reads from env
PROJECT_ID=${1:-$PROJECT_ID}

if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID is not set. Please provide it as an argument or set the PROJECT_ID environment variable."
  exit 1
fi

echo "Setting gcloud project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo "Enabling GCP APIs..."
gcloud services enable \
  compute.googleapis.com \
  pubsub.googleapis.com \
  dataflow.googleapis.com \
  bigquery.googleapis.com \
  storage-component.googleapis.com \
  run.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  cloudtrace.googleapis.com \
  monitoring.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com

echo "Successfully enabled GCP APIs for project $PROJECT_ID"
