"""Trajectory scoring and agent step tracking models.

CONNECTIONS:
- Imported by: observability/trajectory_evaluator.py (scores trajectories)
              agents/state.py (steps list uses AgentStep)
              api/dashboard.py (returns trajectory data)
              services/bigquery_service.py (writes to trajectory_scores table)
- Depends on: None (standalone models)
- Stored in: BigQuery trajectory_scores table
- Displayed by: Frontend evaluation page (radar chart, MTTR trend)

METRICS (5-metric scoring system):
1. task_completion: Did the agent successfully fix the error? (0.0 or 1.0)
2. tool_selection_accuracy: Did the agent pick the right MCP tools? (0.0–1.0)
3. trajectory_efficiency: useful_steps / total_steps (0.0–1.0)
4. time_to_resolution_sec: Total wall-clock time to resolve
5. cost_per_heal_usd: Total LLM token cost for this healing event
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class AgentStep(BaseModel):
    """A single step in the agent's trajectory.
    
    Logged by each LangGraph node during execution.
    Aggregated into the trajectory list in PipelineHealingState.steps.
    
    Args:
        step_id: Auto-generated UUID
        node_name: LangGraph node that executed (e.g., "triage", "schema_evolution")
        action: What the node did (e.g., "called MCP tool get_schema")
        input_data: Input to the node (truncated for storage)
        output_data: Output from the node (truncated for storage)
        tool_calls: List of MCP tools invoked during this step
        input_tokens: Tokens consumed for this step's LLM call
        output_tokens: Tokens generated for this step's LLM call
        duration_ms: Wall-clock time for this step
        timestamp: When this step executed
        error: Optional error message if step failed
    """
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_name: str
    action: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    tool_calls: list[str] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class TrajectoryScore(BaseModel):
    """5-metric trajectory score — written to BigQuery trajectory_scores table.
    
    Computed by: observability/trajectory_evaluator.py after each healing event.
    
    Fields map 1:1 to the BigQuery trajectory_scores table columns.
    If you change fields here, update infra/terraform/bigquery.tf.
    """
    score_id: str = Field(default_factory=lambda: f"SCORE-{uuid.uuid4().hex[:10]}")
    healing_id: str  # FK to healing_events table
    task_completion: float = Field(ge=0.0, le=1.0, description="0.0=failed, 1.0=success")
    tool_selection_accuracy: float = Field(ge=0.0, le=1.0, description="correct_tools / total_tools")
    trajectory_efficiency: float = Field(ge=0.0, le=1.0, description="useful_steps / total_steps")
    time_to_resolution_sec: float = Field(ge=0.0)
    cost_per_heal_usd: float = Field(ge=0.0)
    safety_violations: int = Field(ge=0, default=0)
    scored_at: datetime = Field(default_factory=datetime.utcnow)
