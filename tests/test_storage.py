"""Test persistent database storage of evaluation runs and test case records."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.storage.db import Base, EvaluationRun, TestCaseRecord, Repository, save_evaluation_record


def test_save_and_retrieve_evaluation_record():
    # Use SQLite in-memory engine for test isolation
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    sample_result = {
        "status": "completed",
        "pass_rate": 0.98,
        "total_tests": 12,
        "passed_tests": 11,
        "failed_tests": 1,
        "regression_detected": False,
        "latency_p95_ms": 420.5,
        "token_usage_total": 1250,
        "markdown_report": "### Evaluation Report Passed",
        "details": [
            {
                "name": "test_case_1",
                "category": "regression",
                "passed": True,
                "score": 1.0,
                "schema_valid": True,
                "schema_errors": [],
                "judge_reasoning": "High quality"
            },
            {
                "name": "test_case_2",
                "category": "adversarial",
                "passed": False,
                "score": 0.2,
                "schema_valid": True,
                "schema_errors": [],
                "judge_reasoning": "Injection slipped"
            }
        ]
    }

    save_evaluation_record(
        job_id="test-run-101",
        repo_name="acme/ai-engine",
        commit_sha="abcd12345678",
        pr_number=50,
        result_dict=sample_result,
        engine=engine
    )

    Session = sessionmaker(bind=engine)
    session = Session()

    run = session.query(EvaluationRun).filter_by(id="test-run-101").first()
    assert run is not None
    assert run.repo_name == "acme/ai-engine"
    assert run.pass_rate == 0.98
    assert run.total_tests == 12
    assert run.token_usage == 1250

    cases = session.query(TestCaseRecord).filter_by(run_id="test-run-101").all()
    assert len(cases) == 2
    assert cases[0].passed is True
    assert cases[1].passed is False

    session.close()
