"""Healing result and approval request models.

CONNECTIONS:
- Imported by: agents/nodes/apply_fix.py, agents/nodes/escalate.py,
              api/approvals.py, api/dashboard.py,
              services/firestore_service.py, services/bigquery_service.py
- Depends on: models/enums.py
- Stored in: BigQuery (healing_events table), Firestore (pending_approvals collection)
- Displayed by: Frontend dashboard (agents page, approvals page)
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid

from app.models.enums import ErrorType, Severity, ApprovalStatus, ComplexityLevel


class HealingResult(BaseModel):
    """Complete record of a healing event — written to BigQuery healing_events table.
    
    This model represents the FULL lifecycle of a single error → diagnosis → fix → verify cycle.
    
    Fields map 1:1 to the BigQuery healing_events table columns.
    If you change fields here, update infra/terraform/bigquery.tf.
    """
    healing_id: str = Field(default_factory=lambda: f"HEAL-{uuid.uuid4().hex[:10]}")
    error_event_id: str
    error_type: ErrorType
    error_subtype: str  # e.g., "new_field", "null_values"
    severity: Severity
    complexity: ComplexityLevel
    model_used: str  # "gemini-2.0-flash" or "gemini-2.5-pro"
    diagnosis: str
    proposed_fix: str  # SQL DDL or remediation command
    rollback_statement: str  # Undo SQL
    confidence: float = Field(ge=0.0, le=1.0)
    approval_status: ApprovalStatus
    approved_by: Optional[str] = None
    fix_applied: bool = False
    verification_passed: bool = False
    time_to_resolution_ms: Optional[int] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    trajectory: Optional[list[dict]] = None  # Full agent step trace as JSON


class ApprovalRequest(BaseModel):
    """Pending approval stored in Firestore pending_approvals collection.
    
    Created by: agents/nodes/escalate.py when confidence < threshold
    Read by: api/approvals.py GET endpoint
    Updated by: api/approvals.py POST approve/reject endpoint
    Displayed by: Frontend approvals page
    """
    approval_id: str = Field(default_factory=lambda: f"APR-{uuid.uuid4().hex[:10]}")
    healing_id: str
    error_type: ErrorType
    error_subtype: str
    severity: Severity
    error_payload: dict  # Raw error event
    diagnosis: str
    proposed_fix: str
    rollback_statement: str
    agent_reasoning: list[dict]  # Step-by-step reasoning chain
    confidence: float = Field(ge=0.0, le=1.0)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    retry_count: int = 0


class ApprovalDetail(ApprovalRequest):
    """Extended approval info returned by GET /api/approvals/{id}.
    
    Inherits all ApprovalRequest fields and adds computed/joined data.
    """
    current_schema: Optional[dict] = None  # Current BQ table schema
    proposed_schema: Optional[dict] = None  # What schema would look like after fix
