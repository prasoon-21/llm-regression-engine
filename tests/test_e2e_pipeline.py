"""End-to-End integration test simulating the entire LLM CI/CD pipeline."""
import json
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app
from src.worker import EvaluationWorker
from src.broker.queue import get_task_broker
from src.broker.schemas import JobStatus
from src.security import compute_github_signature
from src.config import get_settings


@pytest.mark.asyncio
async def test_full_pipeline_e2e():
    settings = get_settings()
    broker = get_task_broker()
    broker.client.delete(broker.queue_name)

    # Step 1: Simulate PR Opened Webhook
    pr_payload = {
        "action": "opened",
        "repository": {"full_name": "acme-corp/support-bot", "name": "support-bot"},
        "pull_request": {
            "number": 42,
            "head": {"sha": "9f8e7d6c5b4a3120abcdef1234567890abcdef12", "ref": "prompt-update"}
        },
        "sender": {"login": "ai-engineer"}
    }
    payload_bytes = json.dumps(pr_payload).encode("utf-8")
    sig = compute_github_signature(payload_bytes, settings.GITHUB_WEBHOOK_SECRET or "")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        webhook_res = await client.post(
            "/api/v1/webhook",
            content=payload_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "pull_request"
            }
        )

    assert webhook_res.status_code == 202
    job_info = webhook_res.json()
    job_id = job_info["job_id"]
    assert job_info["status"] == "queued"

    # Step 2: Worker picks up and executes the job
    worker = EvaluationWorker(broker=broker)
    queued_job = broker.dequeue_job(timeout_seconds=2)
    assert queued_job is not None
    assert queued_job.job_id == job_id

    result = await worker.process_job(queued_job)

    # Step 3: Validate outcome
    assert result.job_id == job_id
    assert result.total_tests > 0
    assert result.pass_rate > 0.0
    assert len(result.markdown_report) > 0
    assert "LLM CI/CD Regression & Red-Teaming Report" in result.markdown_report

    # Step 4: Verify state in broker
    final_job = broker.get_job(job_id)
    assert final_job is not None
    assert final_job.status in (JobStatus.COMPLETED, JobStatus.REGRESSION_DETECTED)
    assert final_job.result is not None
