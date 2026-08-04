.PHONY: install test lint format generate-events run-pipeline-local run-pipeline-gcp terraform-init terraform-plan terraform-apply clean

install:
	cd backend && pip install -r requirements.txt

test:
	cd backend && pytest tests/unit/ -v

lint:
	cd backend && ruff check .

format:
	cd backend && ruff format .

generate-events:
	cd backend && python -m data_generator.generator

run-pipeline-local:
	cd backend && python -m streaming.pipeline --runner DirectRunner

run-pipeline-gcp:
	cd backend && python -m streaming.pipeline --runner DataflowRunner

terraform-init:
	cd infra/terraform && terraform init

terraform-plan:
	cd infra/terraform && terraform plan

terraform-apply:
	cd infra/terraform && terraform apply

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
