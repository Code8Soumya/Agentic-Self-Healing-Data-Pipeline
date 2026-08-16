lakehouse_bucket = "tough-volt-504614-q6-ecommerce-lakehouse"

bq_dataset_id = "ecommerce"

agent_service_account_email = "healing-agent-sa@tough-volt-504614-q6.iam.gserviceaccount.com"

dataflow_service_account_email = "dataflow-pipeline-sa@tough-volt-504614-q6.iam.gserviceaccount.com"
dataflow_temp_bucket = "tough-volt-504614-q6-dataflow-temp"

raw_events_topic = "projects/tough-volt-504614-q6/topics/raw-ecommerce-events"
error_events_topic = "projects/tough-volt-504614-q6/topics/pipeline-errors"


gcloud auth login
gcloud auth application-default login


source .venv/bin/activate



