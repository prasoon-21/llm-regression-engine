"""Test task broker queue operations, state transitions, and rate limiting."""
import pytest
from src.broker.queue import TaskBroker
from src.broker.schemas import EvaluationJob, JobStatus, JobResult


def test_enqueue_dequeue_and_status():
    broker = TaskBroker()
    broker.queue_name = "test_queue_isolated"
    broker.client.delete(broker.queue_name)

    job = EvaluationJob(
        job_id="test-job-999",
        repository="test-org/test-repo",
        pull_request_number=12,
        commit_sha="abcd1234efgh5678",
        status=JobStatus.PENDING
    )

    # 1. Enqueue
    assert broker.enqueue_job(job) is True

    # 2. Inspect state
    fetched = broker.get_job("test-job-999")
    assert fetched is not None
    assert fetched.status == JobStatus.PENDING
    assert fetched.repository == "test-org/test-repo"

    # 3. Dequeue
    popped = broker.dequeue_job(timeout_seconds=1)
    assert popped is not None
    assert popped.job_id == "test-job-999"

    # 4. Update status
    result = JobResult(
        job_id="test-job-999",
        status=JobStatus.COMPLETED,
        total_tests=10,
        passed_tests=10,
        failed_tests=0,
        pass_rate=1.0,
        regression_detected=False
    )
    updated = broker.update_job_status("test-job-999", JobStatus.COMPLETED, result=result)
    assert updated is not None
    assert updated.status == JobStatus.COMPLETED
    assert updated.result["pass_rate"] == 1.0


def test_rate_limiting():
    broker = TaskBroker()
    repo = "rate-limited-org/repo"

    # Allow up to 3 requests in short window
    allowed1, _ = broker.check_rate_limit(repo, max_requests=2, window_seconds=60)
    allowed2, _ = broker.check_rate_limit(repo, max_requests=2, window_seconds=60)
    allowed3, _ = broker.check_rate_limit(repo, max_requests=2, window_seconds=60)

    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is False  # Exceeded limit
