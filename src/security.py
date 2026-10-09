"""Cryptographic security utilities for webhook signature verification."""
import hmac
import hashlib
from typing import Optional
from fastapi import Header, HTTPException, Request, status
from src.config import get_settings


def verify_github_signature(payload_bytes: bytes, signature_header: Optional[str], secret: Optional[str]) -> bool:
    """
    Verify GitHub Webhook HMAC SHA256 signature.
    Signature header format: sha256=<hex_digest>
    """
    if not secret:
        # If no secret is configured in dev mode, reject if signature was required
        return False
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_signature = signature_header.split("sha256=")[-1]
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)


def compute_github_signature(payload_bytes: bytes, secret: str) -> str:
    """Helper to compute valid sha256 signature header value for testing and client requests."""
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


async def validate_webhook_request(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
) -> bytes:
    """FastAPI dependency to extract and cryptographically verify webhook payload."""
    settings = get_settings()
    body = await request.body()

    # In development/test mode without a secret, skip verification if explicitly desired
    if settings.ENVIRONMENT == "development" and not settings.GITHUB_WEBHOOK_SECRET:
        return body

    if not x_hub_signature_256:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Hub-Signature-256 header."
        )

    is_valid = verify_github_signature(
        payload_bytes=body,
        signature_header=x_hub_signature_256,
        secret=settings.GITHUB_WEBHOOK_SECRET
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid cryptographic webhook signature."
        )

    return body
