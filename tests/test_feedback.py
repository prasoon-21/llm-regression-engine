"""Test feedback loop: Markdown reports, GitHub status and comments, and telemetry."""
import pytest
from src.feedback.pr_reporter import generate_markdown_report, PRCommentManager
from src.feedback.github_checks import GitHubStatusManager
from src.feedback.telemetry import TelemetryLogger
from src.validation.runner import ExecutionSummary, TestCaseResult
from src.validation.audit import PerformanceAudit


def test_markdown_report_formatting():
    audit = PerformanceAudit(
        total_tokens=450,
        prompt_tokens=300,
        completion_tokens=150,
        token_usage_delta_pct=-5.0,
        latency_p50_ms=350.0,
        latency_p95_ms=520.0,
        latency_delta_pct=2.5,
        regression_detected=False
    )
    summary = ExecutionSummary(
        total_tests=5,
        passed_tests=5,
        failed_tests=0,
        pass_rate=1.0,
        schema_failures=0,
        judge_failures=0,
        adversarial_failures=0,
        audit=audit,
        test_results=[
            TestCaseResult(
                name="test_intent_router",
                category="regression",
                passed=True,
                score=1.0,
                schema_valid=True
            )
        ]
    )

    report = generate_markdown_report(
        summary=summary,
        repo="acme/ai-bot",
        commit_sha="a1b2c3d4e5f6",
        pr_number=55,
        model_name="gpt-4o"
    )

    assert "PASSED — NO REGRESSION DETECTED" in report
    assert "acme/ai-bot" in report
    assert "100.0%" in report
    assert "520.0 ms" in report


@pytest.mark.asyncio
async def test_mock_github_status_and_comment():
    status_mgr = GitHubStatusManager(token=None)
    res_status = await status_mgr.set_commit_status(
        repo="test/repo",
        commit_sha="1234567890",
        state="success",
        description="Passed regression suite"
    )
    assert res_status is True

    comment_mgr = PRCommentManager(token=None)
    res_comment = await comment_mgr.post_or_update_comment(
        repo="test/repo",
        pr_number=10,
        markdown_content="### Evaluation passed"
    )
    assert res_comment is True


def test_telemetry_event_dispatch():
    telemetry = TelemetryLogger()
    res = telemetry.log_evaluation_event(
        event_name="test_event",
        distinct_id="repo-1",
        properties={"status": "success"}
    )
    assert res is True
