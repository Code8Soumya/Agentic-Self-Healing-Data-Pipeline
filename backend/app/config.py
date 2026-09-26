"""Application configuration using Pydantic Settings.

CONNECTIONS:
- Imported by: ALL backend modules that need config values
- Reads from: .env file and environment variables
- Used in: main.py (FastAPI app startup), services/*.py, agents/*.py
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the entire backend application.

    All values are loaded from environment variables or a .env file.
    Use get_settings() to access a cached singleton instance.
    """

    # ── GCP Core ──
    gcp_project_id: str
    gcp_region: str = "asia-south1"
    gcp_zone: str = "asia-south1-a"

    # ── BigQuery ──
    bq_dataset: str = "ecommerce"
    bq_orders_table: str = "orders"
    bq_inventory_table: str = "inventory"
    bq_user_activity_table: str = "user_activity"
    bq_healing_table: str = "healing_events"
    bq_trajectory_table: str = "trajectory_scores"

    # ── Pub/Sub ──
    pubsub_raw_topic: str = "raw-ecommerce-events"
    pubsub_error_topic: str = "pipeline-errors"

    # ── GCS ──
    gcs_lakehouse_bucket: str = ""

    # ── Firestore ──
    firestore_database: str = "(default)"

    # ── Vertex AI / LLM ──
    vertex_ai_location: str = "us-central1"
    gemini_flash_model: str = "gemini-3.7-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    # ── Agent Thresholds ──
    auto_approve_confidence: float = 0.95
    escalation_confidence: float = 0.80
    max_retries: int = 3
    token_budget_per_heal: int = 100_000
    token_budget_per_hour: int = 1_000_000

    # ── API ──
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    cors_origins: list[str] = ["http://localhost:3000"]

    # ── Notifications ──
    slack_webhook_url: str = ""

    # ── GitHub ──
    github_token: str = ""
    github_repo: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Returns a cached singleton Settings instance.

    Returns:
        Settings: The application configuration object.

    Usage:
        from app.config import get_settings
        settings = get_settings()
        print(settings.gcp_project_id)
    """
    return Settings()
