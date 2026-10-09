"""GitHub Checks API and Commit Status Check integration."""
import logging
from typing import Optional
import httpx
from src.config import get_settings

logger = logging.getLogger(__name__)


class GitHubStatusManager:
    def __init__(self, token: Optional[str] = None):
        self.settings = get_settings()
        token_to_use = token if token is not None else self.settings.GITHUB_TOKEN
        self.token = token_to_use
        self.base_url = "https://api.github.com"

    def _is_active(self) -> bool:
        return bool(self.token and "xxxx" not in self.token and not self.token.startswith("dummy"))

    def _headers(self):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._is_active():
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def set_commit_status(
        self,
        repo: str,
        commit_sha: str,
        state: str,  # pending, success, failure, error
        description: str,
        target_url: Optional[str] = None,
        context: str = "LLM Regression & Red-Teaming Engine"
    ) -> bool:
        """
        Updates GitHub commit status check:
        state: 'pending' (in-progress), 'success', or 'failure'
        """
        if not self._is_active() or repo.startswith("test/"):
            logger.info("[Mock GitHub Status] %s for %s @ %s: %s", state.upper(), repo, commit_sha[:7], description)
            return True

        url = f"{self.base_url}/repos/{repo}/statuses/{commit_sha}"
        payload = {
            "state": state,
            "description": description[:140],
            "context": context,
            "target_url": target_url or "https://github.com"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=self._headers(), json=payload)
                if res.status_code in (200, 201):
                    logger.info("Updated GitHub commit status to '%s' for %s", state, commit_sha[:7])
                    return True
                else:
                    logger.warning("Failed to update commit status: %s %s", res.status_code, res.text)
                    return False
        except Exception as e:
            logger.error("Error setting GitHub status: %s", e)
            return False

    async def create_check_run(
        self,
        repo: str,
        commit_sha: str,
        name: str = "LLM Regression Suite",
        status: str = "in_progress",  # queued, in_progress, completed
        conclusion: Optional[str] = None,  # success, failure, neutral, cancelled, timed_out
        summary: str = "",
        details_markdown: str = ""
    ) -> Optional[int]:
        """Creates or updates a rich GitHub Check Run."""
        if not self.token:
            logger.info("[Mock GitHub Check Run] %s: %s (conclusion=%s)", name, status, conclusion)
            return 12345

        url = f"{self.base_url}/repos/{repo}/check-runs"
        payload = {
            "name": name,
            "head_sha": commit_sha,
            "status": status,
        }
        if conclusion:
            payload["conclusion"] = conclusion
        if summary:
            payload["output"] = {
                "title": f"LLM CI/CD Check: {conclusion or status}",
                "summary": summary,
                "text": details_markdown
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=self._headers(), json=payload)
                if res.status_code in (200, 201):
                    return res.json().get("id")
                else:
                    logger.warning("Failed to create check run: %s %s", res.status_code, res.text)
                    return None
        except Exception as e:
            logger.error("Error creating check run: %s", e)
            return None
