"""Safety and performance audits: token usage deltas, latency percentiles, regression detection."""
import statistics
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PerformanceAudit(BaseModel):
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    baseline_tokens: Optional[int] = None
    token_usage_delta_pct: float = 0.0

    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    baseline_latency_p95_ms: Optional[float] = None
    latency_delta_pct: float = 0.0

    regression_detected: bool = False
    regression_reasons: List[str] = Field(default_factory=list)


def calculate_percentile(data: List[float], percentile: float) -> float:
    if not data:
        return 0.0
    if len(data) == 1:
        return data[0]
    sorted_data = sorted(data)
    idx = int((percentile / 100.0) * len(sorted_data))
    return sorted_data[min(idx, len(sorted_data) - 1)]


def run_performance_audit(
    latencies: List[float],
    prompt_tokens_list: List[int],
    completion_tokens_list: List[int],
    baseline_tokens: Optional[int] = None,
    baseline_latency_p95: Optional[float] = None,
    pass_rate: float = 1.0,
    baseline_pass_rate: float = 0.95
) -> PerformanceAudit:
    """
    Compute performance metrics, token deltas, and audit against regression gates.
    """
    total_p_tokens = sum(prompt_tokens_list)
    total_c_tokens = sum(completion_tokens_list)
    total_tokens = total_p_tokens + total_c_tokens

    p50 = calculate_percentile(latencies, 50.0)
    p95 = calculate_percentile(latencies, 95.0)
    p99 = calculate_percentile(latencies, 99.0)

    token_delta_pct = 0.0
    if baseline_tokens and baseline_tokens > 0:
        token_delta_pct = round(((total_tokens - baseline_tokens) / baseline_tokens) * 100, 2)

    latency_delta_pct = 0.0
    if baseline_latency_p95 and baseline_latency_p95 > 0:
        latency_delta_pct = round(((p95 - baseline_latency_p95) / baseline_latency_p95) * 100, 2)

    reasons = []
    # Regression gates:
    # 1. Pass rate regression
    if pass_rate < baseline_pass_rate:
        reasons.append(f"Pass rate ({round(pass_rate*100, 1)}%) dropped below baseline ({round(baseline_pass_rate*100, 1)}%)")

    # 2. Token cost explosion (> 30% increase)
    if token_delta_pct > 30.0:
        reasons.append(f"Token usage surged by +{token_delta_pct}% relative to baseline")

    # 3. Latency spike (> 50% increase)
    if latency_delta_pct > 50.0:
        reasons.append(f"P95 latency spiked by +{latency_delta_pct}% relative to baseline")

    return PerformanceAudit(
        total_tokens=total_tokens,
        prompt_tokens=total_p_tokens,
        completion_tokens=total_c_tokens,
        baseline_tokens=baseline_tokens,
        token_usage_delta_pct=token_delta_pct,
        latency_p50_ms=round(p50, 1),
        latency_p95_ms=round(p95, 1),
        latency_p99_ms=round(p99, 1),
        baseline_latency_p95_ms=baseline_latency_p95,
        latency_delta_pct=latency_delta_pct,
        regression_detected=len(reasons) > 0,
        regression_reasons=reasons
    )
