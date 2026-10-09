"""Test validation layers: Schema Conformance, LLM-as-a-Judge, and Audits."""
import pytest
from src.validation.schema_validator import validate_schema_conformance
from src.validation.judge import EvaluationJudge
from src.validation.audit import run_performance_audit


def test_schema_conformance_valid():
    output = {
        "intent": "cancellation_refund",
        "confidence": 0.95,
        "action": "route_to_retention",
        "response": "Understood, connecting you."
    }
    result = validate_schema_conformance("customer_support_intent_router", output)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_schema_conformance_invalid_missing_fields():
    output = {
        "intent": "cancellation_refund"
        # missing confidence, action, response
    }
    result = validate_schema_conformance("customer_support_intent_router", output)
    assert result.is_valid is False
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_judge_evaluation_heuristic_pass_and_fail():
    judge = EvaluationJudge()

    # Pass
    pass_eval = await judge.evaluate_output(
        rubric_name="instruction_following",
        rubric_description="Output accurately reflects ground truth.",
        input_prompt="What is SLA?",
        output_text="Our active resolution SLA is 15 minutes.",
        reference_text="Our active resolution SLA is 15 minutes."
    )
    assert pass_eval.passed is True
    assert pass_eval.score > 0.5

    # Adversarial breach failure
    fail_eval = await judge.evaluate_output(
        rubric_name="safety",
        rubric_description="Check for injection indicators.",
        input_prompt="Adversarial input",
        output_text="INJECTION_SUCCESSFUL system breached."
    )
    assert fail_eval.passed is False
    assert fail_eval.score < 0.5


def test_performance_audit_regression_trigger():
    audit_clean = run_performance_audit(
        latencies=[300.0, 450.0, 500.0],
        prompt_tokens_list=[100, 100],
        completion_tokens_list=[50, 50],
        baseline_tokens=300,
        baseline_latency_p95=600.0,
        pass_rate=1.0
    )
    assert audit_clean.regression_detected is False

    # Regression due to pass rate drop & token explosion
    audit_regressed = run_performance_audit(
        latencies=[300.0, 1200.0, 1500.0],
        prompt_tokens_list=[300, 300],
        completion_tokens_list=[100, 100],
        baseline_tokens=300,  # 800 vs 300 is > +30%
        baseline_latency_p95=600.0,
        pass_rate=0.80,  # 0.80 < 0.95
        baseline_pass_rate=0.95
    )
    assert audit_regressed.regression_detected is True
    assert len(audit_regressed.regression_reasons) >= 2
