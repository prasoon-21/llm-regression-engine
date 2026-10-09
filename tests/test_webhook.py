"""Test GitHub Webhook ingestion endpoint."""
import json
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app
from src.security import compute_github_signature
from src.config import get_settings


@pytest.mark.asyncio
async def test_webhook_ping_event():
    settings = get_settings()
    payload = json.dumps({"zen": "Keep it logically awesome.", "hook_id": 12345}).encode("utf-8")
    sig = compute_github_signature(payload, settings.GITHUB_WEBHOOK_SECRET or "")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhook",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "ping"
            }
        )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["event"] == "ping"


@pytest.mark.asyncio
async def test_webhook_pull_request_opened_triggers_job():
    settings = get_settings()
    pr_payload = {
        "action": "opened",
        "repository": {"full_name": "acme-corp/chat-agent", "name": "chat-agent"},
        "pull_request": {
            "number": 104,
            "head": {"sha": "c0ffee1234567890abcdef1234567890abcdef12", "ref": "feat/new-prompt"}
        },
        "sender": {"login": "dev-alice"}
    }
    payload_bytes = json.dumps(pr_payload).encode("utf-8")
    sig = compute_github_signature(payload_bytes, settings.GITHUB_WEBHOOK_SECRET or "")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhook",
            content=payload_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "pull_request"
            }
        )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert "job-" in data["job_id"]
    assert data["repository"] == "acme-corp/chat-agent"
    assert data["pr_number"] == 104


@pytest.mark.asyncio
async def test_webhook_unauthorized_missing_or_bad_sig():
    payload_bytes = b'{"action": "opened"}'

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Missing signature
        response = await client.post(
            "/api/v1/webhook",
            content=payload_bytes,
            headers={"Content-Type": "application/json", "X-GitHub-Event": "pull_request"}
        )
        assert response.status_code in (401, 403)

        # Invalid signature
        response_bad = await client.post(
            "/api/v1/webhook",
            content=payload_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": "sha256=0000000000000000000000000000000000000000000000000000000000000000",
                "X-GitHub-Event": "pull_request"
            }
        )
        assert response_bad.status_code == 403
