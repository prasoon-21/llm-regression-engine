"""Markdown regression report formatting and GitHub PR comment dispatch."""
import logging
from typing import Optional
import httpx
from src.validation.runner import ExecutionSummary
from src.config import get_settings

logger = logging.getLogger(__name__)


def generate_markdown_report(
    summary: ExecutionSummary,
    repo: str,
    commit_sha: str,
    pr_number: Optional[int],
    model_name: str = "gpt-4o"
) -> str:
    """
    Format evaluation and red-teaming metrics into a clean GitHub PR markdown report.
    """
    audit = summary.audit
    status_emoji = "✅" if not audit.regression_detected else "❌"
    status_text = "PASSED — NO REGRESSION DETECTED" if not audit.regression_detected else "FAILED — REGRESSION DETECTED"

    delta_color = "🟢" if audit.token_usage_delta_pct <= 0 else "🟡" if audit.token_usage_delta_pct <= 15 else "🔴"
    latency_color = "🟢" if audit.latency_delta_pct <= 0 else "🟡" if audit.latency_delta_pct <= 25 else "🔴"

    report = f"""## {status_emoji} LLM CI/CD Regression & Red-Teaming Report

> **Repository:** `{repo}` | **Commit:** `{commit_sha[:7]}` | **Model:** `{model_name}`  
> **Status:** **{status_text}**

### 📊 Summary Metrics

| Metric | Target / Result | Status |
| :--- | :--- | :--- |
| **Pass Rate** | `{round(summary.pass_rate * 100, 1)}%` ({summary.passed_tests}/{summary.total_tests}) | {'✅ Pass' if summary.pass_rate >= 0.95 else '❌ Fail'} |
| **Schema Conformance** | `{summary.total_tests - summary.schema_failures}/{summary.total_tests}` valid | {'✅ Strict' if summary.schema_failures == 0 else '❌ Schema Failures'} |
| **Semantic Judge Score** | `{summary.total_tests - summary.judge_failures}/{summary.total_tests}` passed | {'✅ High' if summary.judge_failures == 0 else '⚠️ Rubric Failures'} |
| **Red-Team Defense** | `{summary.total_tests - summary.adversarial_failures}/{summary.total_tests}` resisted | {'🛡️ Defended' if summary.adversarial_failures == 0 else '🚨 Injection Breaches'} |
| **P95 Latency** | `{audit.latency_p95_ms} ms` ({latency_color} `{audit.latency_delta_pct:+.1f}%` delta) | {'✅ Fast' if audit.latency_delta_pct <= 25 else '⚠️ Slow'} |
| **Token Consumption** | `{audit.total_tokens}` tokens ({delta_color} `{audit.token_usage_delta_pct:+.1f}%` delta) | {'✅ Optimal' if audit.token_usage_delta_pct <= 20 else '⚠️ High Delta'} |

"""

    if audit.regression_reasons:
        report += "### ⚠️ Regression Alert Reasons\n\n"
        for reason in audit.regression_reasons:
            report += f"- ❌ {reason}\n"
        report += "\n"

    # Add detailed breakdown of failures if any
    failed_cases = [c for c in summary.test_results if not c.passed]
    if failed_cases:
        report += "<details><summary><b>🔍 View Failed Test Cases (" + str(len(failed_cases)) + ")</b></summary>\n\n"
        report += "| Test Case | Category | Schema Error | Judge Evaluation |\n"
        report += "| :--- | :--- | :--- | :--- |\n"
        for failure in failed_cases:
            schema_err_str = "<br>".join(failure.schema_errors) if failure.schema_errors else "None"
            report += f"| `{failure.name}` | `{failure.category}` | {schema_err_str} | {failure.judge_reasoning} |\n"
        report += "\n</details>\n\n"

    report += "---\n*Automated evaluation executed by **LangSmith CI/CD Regression Engine**.*"
    return report


class PRCommentManager:
    def __init__(self, token: Optional[str] = None):
        self.settings = get_settings()
        token_to_use = token if token is not None else self.settings.GITHUB_TOKEN
        self.token = token_to_use
        self.base_url = "https://api.github.com"

    def _is_active(self) -> bool:
        return bool(self.token and "xxxx" not in self.token and not self.token.startswith("dummy"))

    async def post_or_update_comment(
        self,
        repo: str,
        pr_number: int,
        markdown_content: str
    ) -> bool:
        """Post evaluation report directly as a comment on the GitHub PR."""
        if not self._is_active() or repo.startswith("test/"):
            logger.info("[Mock PR Comment] Repo: %s | PR #%d\n%s", repo, pr_number, markdown_content[:200])
            return True

        url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json={"body": markdown_content})
                if res.status_code in (200, 201):
                    logger.info("Successfully posted regression report comment on PR #%d", pr_number)
                    return True
                else:
                    logger.warning("Failed to post PR comment: %s %s", res.status_code, res.text)
                    return False
        except Exception as e:
            logger.error("Error posting PR comment: %s", e)
            return False
