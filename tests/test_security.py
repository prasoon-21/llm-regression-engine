"""Test cryptographic HMAC SHA256 webhook signature verification."""
import pytest
from src.security import verify_github_signature, compute_github_signature


def test_signature_verification_success():
    secret = "super_secret_webhook_key_123"
    payload = b'{"action": "opened", "pull_request": {"number": 42}}'

    sig_header = compute_github_signature(payload, secret)
    assert sig_header.startswith("sha256=")

    assert verify_github_signature(payload, sig_header, secret) is True


def test_signature_verification_tampered_payload():
    secret = "super_secret_webhook_key_123"
    payload = b'{"action": "opened", "pull_request": {"number": 42}}'
    tampered_payload = b'{"action": "opened", "pull_request": {"number": 999}}'

    sig_header = compute_github_signature(payload, secret)
    assert verify_github_signature(tampered_payload, sig_header, secret) is False


def test_signature_verification_wrong_secret():
    payload = b'{"hello": "world"}'
    sig_header = compute_github_signature(payload, "secret_a")

    assert verify_github_signature(payload, sig_header, "secret_b") is False


def test_signature_verification_malformed_header():
    secret = "any_secret"
    payload = b'{"test": 1}'

    assert verify_github_signature(payload, "invalid_header_without_sha256_prefix", secret) is False
    assert verify_github_signature(payload, None, secret) is False
