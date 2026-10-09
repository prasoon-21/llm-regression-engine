"""Worker execution engine: coordinates trace harvesting, synthesis, validation, and PR gating."""
import asyncio
import logging
import time
from typing import Optional

from src.broker.queue import get_task_broker, TaskBroker
from src.broker.schemas import EvaluationJob, JobStatus, JobResult
from src.harvesting.langsmith_extractor import LangSmithHarvester
from src.validation.runner import ValidationRunner
from src.feedback.github_checks import GitHubStatusManager
from src.feedback.pr_reporter import generate_markdown_report, PRCommentManager
from src.feedback.telemetry import TelemetryLogger
from src.storage.db import save_evaluation_record

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("eval-worker")


class EvaluationWorker:
    def __init__(self, broker: Optional[TaskBroker] = None):
        self.broker = broker or get_task_broker()
        self.harvester = LangSmithHarvester()
        self.runner = ValidationRunner()
        self.github_status = GitHubStatusManager()
        self.pr_reporter = PRCommentManager()
        self.telemetry = TelemetryLogger()

    async def process_job(self, job: EvaluationJob) -> JobResult:
        """Execute end-to-end evaluation pipeline for an incoming job."""
        start_time = time.perf_counter()
        logger.info("=== Starting evaluation for job %s (repo: %s, commit: %s) ===",
                    job.job_id, job.repository, job.commit_sha[:7])

        # 1. Update GitHub status check to 'pending' (in-progress)
        await self.github_status.set_commit_status(
            repo=job.repository,
            commit_sha=job.commit_sha,
            state="pending",
            description="LLM Regression & Red-Teaming test suite executing..."
        )
        self.broker.update_job_status(job.job_id, JobStatus.RUNNING)

        try:
            # 2. Phase 2: LangSmith Ingestion
            logger.info("Harvesting traces from LangSmith project '%s'...", job.langsmith_project)
            traces = self.harvester.fetch_traces(
                project_name=job.langsmith_project,
                tags=job.langsmith_tags,
                prompt_tag=job.prompt_filter_tag,
                limit=10
            )

            # 3. Phase 3: Validation Engine Execution
            logger.info("Executing validation runner with %d traces...", len(traces))
            summary = await self.runner.execute_validation(
                traces=traces,
                target_model=job.model_override or "gpt-4o",
                rubrics=job.rubrics,
                enable_adversarial=job.enable_adversarial,
                baseline_tokens=500,
                baseline_latency_p95=2000.0
            )

            # 4. Phase 4: Feedback Loop & CI/CD Gating
            model_name = job.model_override or "gpt-4o"
            markdown_report = generate_markdown_report(
                summary=summary,
                repo=job.repository,
                commit_sha=job.commit_sha,
                pr_number=job.pull_request_number,
                model_name=model_name
            )

            is_regression = summary.audit.regression_detected
            final_status = JobStatus.REGRESSION_DETECTED if is_regression else JobStatus.COMPLETED
            github_state = "failure" if is_regression else "success"
            github_desc = (
                f"LLM Regression check failed (Pass rate: {round(summary.pass_rate*100, 1)}%)"
                if is_regression
                else f"LLM Regression check passed ({round(summary.pass_rate*100, 1)}% pass rate)"
            )

            # Update GitHub commit status
            await self.github_status.set_commit_status(
                repo=job.repository,
                commit_sha=job.commit_sha,
                state=github_state,
                description=github_desc
            )

            # Post comment to PR if PR number is available
            if job.pull_request_number:
                await self.pr_reporter.post_or_update_comment(
                    repo=job.repository,
                    pr_number=job.pull_request_number,
                    markdown_content=markdown_report
                )

            # Emit Telemetry
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.telemetry.log_evaluation_event(
                event_name="llm_cicd_regression_run",
                distinct_id=job.repository,
                properties={
                    "job_id": job.job_id,
                    "repo": job.repository,
                    "commit_sha": job.commit_sha,
                    "pr_number": job.pull_request_number,
                    "pass_rate": summary.pass_rate,
                    "total_tests": summary.total_tests,
                    "regression_detected": is_regression,
                    "duration_ms": duration_ms,
                    "total_tokens": summary.audit.total_tokens,
                    "model": model_name
                }
            )

            result = JobResult(
                job_id=job.job_id,
                status=final_status,
                total_tests=summary.total_tests,
                passed_tests=summary.passed_tests,
                failed_tests=summary.failed_tests,
                pass_rate=summary.pass_rate,
                regression_detected=is_regression,
                schema_failures=summary.schema_failures,
                judge_failures=summary.judge_failures,
                adversarial_failures=summary.adversarial_failures,
                token_usage_total=summary.audit.total_tokens,
                token_usage_delta_pct=summary.audit.token_usage_delta_pct,
                latency_p95_ms=summary.audit.latency_p95_ms,
                markdown_report=markdown_report,
                details=[t.model_dump() for t in summary.test_results]
            )

            self.broker.update_job_status(job.job_id, final_status, result=result)
            try:
                save_evaluation_record(
                    job_id=job.job_id,
                    repo_name=job.repository,
                    commit_sha=job.commit_sha,
                    pr_number=job.pull_request_number,
                    result_dict=result.model_dump()
                )
            except Exception as dbe:
                logger.warning("Could not persist evaluation record to DB: %s", dbe)

            logger.info("Evaluation job %s finished with status: %s", job.job_id, final_status)
            return result

        except Exception as e:
            logger.exception("Error during job processing %s: %s", job.job_id, e)
            await self.github_status.set_commit_status(
                repo=job.repository,
                commit_sha=job.commit_sha,
                state="error",
                description=f"Evaluation failed: {str(e)[:100]}"
            )
            self.broker.update_job_status(job.job_id, JobStatus.FAILED, error_message=str(e))
            raise

    async def run_worker_loop(self, poll_interval: float = 1.0):
        """Continuous worker polling loop."""
        logger.info("Evaluation Worker loop started. Listening for evaluation tasks...")
        while True:
            job = self.broker.dequeue_job(timeout_seconds=2)
            if job:
                try:
                    await self.process_job(job)
                except Exception as e:
                    logger.error("Failed to process job: %s", e)
            await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    worker = EvaluationWorker()
    asyncio.run(worker.run_worker_loop())
