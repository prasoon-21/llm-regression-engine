"""API Gateway FastAPI application."""
from typing import Any, Dict, Optional
import uuid
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.config import get_settings
from src.api.webhook import router as webhook_router
from src.broker.queue import get_task_broker
from src.broker.schemas import EvaluationJob, JobStatus

import os
import asyncio
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger("api-gateway")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On single-container free tiers (Render, HuggingFace, etc.), run worker alongside gateway
    run_worker = os.getenv("RUN_WORKER_IN_PROCESS", "true").lower() in ("true", "1", "yes")
    worker_task = None
    if run_worker:
        from src.worker import EvaluationWorker
        worker = EvaluationWorker()
        worker_task = asyncio.create_task(worker.run_worker_loop(poll_interval=1.0))
        logger.info("In-process Evaluation Worker started alongside API Gateway.")
    yield
    if worker_task:
        worker_task.cancel()

app = FastAPI(
    title="LLM CI/CD Regression & Red-Teaming Gateway",
    description="Automated LLM regression testing, red-teaming, and PR gating engine integrated with LangSmith and GitHub.",
    version="0.1.0",
    lifespan=lifespan
)

from fastapi.responses import HTMLResponse
from src.ui.dashboard import DASHBOARD_HTML

app.include_router(webhook_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard_view():
    """Interactive Web Dashboard for evaluations and monitoring."""
    return HTMLResponse(content=DASHBOARD_HTML)


class ManualTriggerRequest(BaseModel):
    repository: str
    commit_sha: str
    pull_request_number: Optional[int] = None
    branch: Optional[str] = "main"
    langsmith_project: str = "default"
    model_override: Optional[str] = "gpt-4o"
    enable_adversarial: bool = True


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """System container topology health inspection."""
    broker = get_task_broker()
    broker_ok = False
    try:
        broker.client.ping()
        broker_ok = True
    except Exception:
        pass

    return {
        "status": "healthy" if broker_ok else "degraded",
        "environment": settings.ENVIRONMENT,
        "services": {
            "task_broker": "connected" if broker_ok else "unavailable",
            "litellm_proxy": settings.LITELLM_PROXY_URL,
            "langsmith_endpoint": settings.LANGSMITH_ENDPOINT,
        }
    }


@app.post("/api/v1/jobs/trigger", status_code=status.HTTP_202_ACCEPTED, tags=["Jobs"])
async def manual_trigger_job(req: ManualTriggerRequest) -> Dict[str, Any]:
    """Manually dispatch an evaluation run for testing, ad-hoc red-teaming or CI actions."""
    broker = get_task_broker()
    job_id = f"manual-{uuid.uuid4().hex[:12]}"

    job = EvaluationJob(
        job_id=job_id,
        repository=req.repository,
        pull_request_number=req.pull_request_number,
        commit_sha=req.commit_sha,
        branch=req.branch,
        event_type="manual",
        langsmith_project=req.langsmith_project,
        model_override=req.model_override,
        enable_adversarial=req.enable_adversarial,
        status=JobStatus.PENDING
    )

    enqueued = broker.enqueue_job(job)
    if not enqueued:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue evaluation job."
        )

    return {
        "status": "queued",
        "job_id": job_id,
        "repository": req.repository,
        "commit_sha": req.commit_sha
    }


@app.get("/api/v1/jobs/{job_id}", tags=["Jobs"])
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Query current status, execution metrics, and Markdown report of a job."""
    broker = get_task_broker()
    job = broker.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return job.model_dump()
