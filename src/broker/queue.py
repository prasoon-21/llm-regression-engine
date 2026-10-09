"""Task broker and queue management using Redis with fallback support."""
import json
import logging
from typing import Optional, Tuple
import redis
import fakeredis

from src.broker.schemas import EvaluationJob, JobStatus, JobResult
from src.config import get_settings

logger = logging.getLogger(__name__)


class TaskBroker:
    def __init__(self, redis_url: Optional[str] = None):
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.REDIS_URL
        self.queue_name = self.settings.REDIS_QUEUE_NAME
        self.client = self._init_client()

    def _init_client(self):
        try:
            client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            client.ping()
            logger.info("Connected to real Redis broker at %s", self.redis_url)
            return client
        except Exception as e:
            logger.warning(
                "Could not connect to Redis at %s (%s). Falling back to FakeRedis in-memory broker.",
                self.redis_url, e
            )
            return fakeredis.FakeRedis(decode_responses=True)

    def check_rate_limit(self, identifier: str, max_requests: Optional[int] = None, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Token-bucket rate limiter per repo/org.
        Returns (is_allowed, current_count).
        """
        limit = max_requests or self.settings.RATE_LIMIT_PER_MINUTE
        rate_key = f"rate_limit:{identifier}"
        try:
            current = self.client.incr(rate_key)
            if current == 1:
                self.client.expire(rate_key, window_seconds)
            return current <= limit, current
        except Exception as e:
            logger.error("Rate limit check failed: %s", e)
            return True, 0

    def enqueue_job(self, job: EvaluationJob) -> bool:
        """Add job to Redis queue and store its state."""
        try:
            job_key = f"job:{job.job_id}"
            job_data = job.model_dump_json()

            # Save state
            self.client.set(job_key, job_data)
            # Add to queue
            self.client.rpush(self.queue_name, job.job_id)
            logger.info("Job %s enqueued successfully for repo %s", job.job_id, job.repository)
            return True
        except Exception as e:
            logger.error("Failed to enqueue job %s: %s", job.job_id, e)
            return False

    def dequeue_job(self, timeout_seconds: int = 2) -> Optional[EvaluationJob]:
        """Pop next job ID from queue and fetch job data."""
        try:
            res = self.client.blpop(self.queue_name, timeout=timeout_seconds)
            if not res:
                return None
            _, job_id = res
            return self.get_job(job_id)
        except Exception as e:
            logger.error("Error popping job from queue: %s", e)
            return None

    def get_job(self, job_id: str) -> Optional[EvaluationJob]:
        """Fetch job by ID."""
        try:
            data = self.client.get(f"job:{job_id}")
            if not data:
                return None
            return EvaluationJob.model_validate_json(data)
        except Exception as e:
            logger.error("Error retrieving job %s: %s", job_id, e)
            return None

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[JobResult] = None,
        error_message: Optional[str] = None
    ) -> Optional[EvaluationJob]:
        """Update job execution state in Redis."""
        job = self.get_job(job_id)
        if not job:
            return None

        job.status = status
        if result:
            job.result = result.model_dump()
        if error_message:
            job.error_message = error_message

        try:
            self.client.set(f"job:{job_id}", job.model_dump_json())
            return job
        except Exception as e:
            logger.error("Failed to update status for job %s: %s", job_id, e)
            return job


# Singleton helper
_broker_instance = None

def get_task_broker() -> TaskBroker:
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = TaskBroker()
    return _broker_instance
