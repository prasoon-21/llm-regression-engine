"""Schemas for broker tasks, jobs, and execution statuses."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REGRESSION_DETECTED = "regression_detected"


class EvaluationJob(BaseModel):
    job_id: str
    repository: str  # e.g., "owner/repo"
    pull_request_number: Optional[int] = None
    commit_sha: str
    branch: Optional[str] = None
    sender: Optional[str] = None
    event_type: str = "pull_request"

    # Evaluation targets
    langsmith_project: str = "default"
    langsmith_tags: List[str] = Field(default_factory=list)
    prompt_filter_tag: Optional[str] = None

    # Config & Models
    model_override: Optional[str] = None
    rubrics: List[str] = Field(default_factory=lambda: ["instruction_following", "factual_accuracy", "safety"])
    enable_adversarial: bool = True

    # State & Timestamps
    status: JobStatus = JobStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class JobResult(BaseModel):
    job_id: str
    status: JobStatus
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    regression_detected: bool
    schema_failures: int = 0
    judge_failures: int = 0
    adversarial_failures: int = 0
    token_usage_total: int = 0
    token_usage_delta_pct: float = 0.0
    latency_p95_ms: float = 0.0
    markdown_report: str = ""
    details: List[Dict[str, Any]] = Field(default_factory=list)
