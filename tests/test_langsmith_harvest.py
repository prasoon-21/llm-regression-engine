"""Test LangSmith trace harvesting workflows."""
import pytest
from src.harvesting.langsmith_extractor import LangSmithHarvester


def test_harvest_traces_filtering():
    harvester = LangSmithHarvester()

    traces = harvester.fetch_traces(
        project_name="customer-support",
        tags=["production-v1"],
        limit=3
    )

    assert len(traces) > 0
    first = traces[0]
    assert first.run_id is not None
    assert "query" in first.inputs or "document_text" in first.inputs or "user_question" in first.inputs
    assert first.outputs is not None
    assert first.latency_ms is not None
    assert first.total_tokens is not None
