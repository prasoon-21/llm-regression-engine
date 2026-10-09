"""Test adversarial synthesis and Promptfoo test suite compilation."""
import pytest
from src.synthesis.adversarial import synthesize_adversarial_cases
from src.synthesis.test_suite_builder import TestSuiteBuilder
from src.harvesting.langsmith_extractor import ExtractedTrace


def test_adversarial_synthesis():
    base_input = {"query": "I need help with my account billing details."}
    mutations = synthesize_adversarial_cases(base_input)

    assert len(mutations) >= 3
    categories = {m.category for m in mutations}
    assert "prompt_injection" in categories
    assert "format_breaking" in categories
    assert "jailbreak" in categories

    for m in mutations:
        assert "query" in m.mutated_input
        assert len(m.safety_assertions) > 0


def test_promptfoo_suite_compilation():
    builder = TestSuiteBuilder(litellm_url="http://litellm-proxy:4000")
    sample_trace = ExtractedTrace(
        run_id="trace-test-1",
        name="test_agent",
        run_type="chain",
        inputs={"query": "Calculate 2+2"},
        outputs={"result": 4},
        reference_output="4"
    )

    suite = builder.build_promptfoo_suite(
        traces=[sample_trace],
        target_model="gpt-4o",
        rubrics=["instruction_following", "safety"],
        include_adversarial=True
    )

    assert "providers" in suite
    assert suite["providers"][0]["id"] == "openai:gpt-4o"
    assert suite["providers"][0]["config"]["apiBaseUrl"] == "http://litellm-proxy:4000/v1"
    assert len(suite["tests"]) > 1  # 1 regression + adversarial tests
