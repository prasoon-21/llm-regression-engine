"""GitHub webhook ingestion router."""
import json
import logging
import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from src.security import validate_webhook_request
from src.broker.schemas import EvaluationJob, JobStatus
from src.broker.queue import get_task_broker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhooks"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def handle_github_webhook(
    raw_body: bytes = Depends(validate_webhook_request),
    x_github_event: str = Header("pull_request", alias="X-GitHub-Event"),
    x_github_delivery: str = Header(None, alias="X-GitHub-Delivery")
) -> Dict[str, Any]:
    """
    Ingest GitHub Webhook events.
    Verifies cryptographic HMAC signature, parses payload, enforces rate limits,
    and enqueues evaluation jobs.
    """
    broker = get_task_broker()

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    logger.info("Received GitHub webhook event: %s (delivery: %s)", x_github_event, x_github_delivery)

    # 1. Ping event
    if x_github_event == "ping":
        return {
            "status": "acknowledged",
            "event": "ping",
            "zen": payload.get("zen"),
            "hook_id": payload.get("hook_id")
        }

    # 2. Pull Request event
    if x_github_event == "pull_request":
        action = payload.get("action")
        # Trigger on PR opened, synchronized (new commits pushed), or reopened
        if action not in ("opened", "synchronize", "reopened"):
            return {
                "status": "ignored",
                "message": f"PR action '{action}' does not trigger regression checks."
            }

        repo_info = payload.get("repository", {})
        repo_name = repo_info.get("full_name", "unknown/unknown")
        pr_data = payload.get("pull_request", {})
        pr_number = pr_data.get("number")
        commit_sha = pr_data.get("head", {}).get("sha")
        branch = pr_data.get("head", {}).get("ref")
        sender = payload.get("sender", {}).get("login")

        if not commit_sha:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing PR commit sha.")

        # Rate limiting check
        is_allowed, current_count = broker.check_rate_limit(repo_name)
        if not is_allowed:
            logger.warning("Rate limit exceeded for repository %s (current count: %d)", repo_name, current_count)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for repository '{repo_name}'. Please retry later."
            )

        job_id = f"job-{uuid.uuid4().hex[:12]}"
        job = EvaluationJob(
            job_id=job_id,
            repository=repo_name,
            pull_request_number=pr_number,
            commit_sha=commit_sha,
            branch=branch,
            sender=sender,
            event_type="pull_request",
            langsmith_project=repo_info.get("name", "default"),
            langsmith_tags=[f"pr-{pr_number}", branch] if pr_number and branch else [],
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
            "repository": repo_name,
            "pr_number": pr_number,
            "commit_sha": commit_sha
        }

    # Other events
    return {
        "status": "ignored",
        "message": f"Event type '{x_github_event}' not monitored."
    }
