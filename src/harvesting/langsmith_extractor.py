"""LangSmith trace harvester: extracts inputs, intermediate reasoning steps, and expected outputs."""
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.config import get_settings

logger = logging.getLogger(__name__)


class ExtractedTrace(BaseModel):
    run_id: str
    name: str
    run_type: str
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    intermediate_steps: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    latency_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    reference_output: Optional[str] = None


class LangSmithHarvester:
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.LANGSMITH_API_KEY
        self.endpoint = endpoint or self.settings.LANGSMITH_ENDPOINT
        self.client = self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("No LANGSMITH_API_KEY provided; LangSmithHarvester will use synthetic golden traces.")
            return None
        try:
            import os
            from langsmith import Client

            workspace_id = self.settings.LANGSMITH_WORKSPACE_ID or os.getenv("LANGSMITH_WORKSPACE_ID")
            if not workspace_id:
                try:
                    import httpx
                    res = httpx.get(
                        f"{self.endpoint.rstrip('/')}/api/v1/workspaces",
                        headers={"X-API-Key": self.api_key},
                        timeout=5.0
                    )
                    if res.status_code == 200 and res.json():
                        workspace_id = res.json()[0].get("id")
                except Exception:
                    pass

            if workspace_id:
                os.environ["LANGSMITH_WORKSPACE_ID"] = workspace_id
                logger.info("Connecting to LangSmith with workspace ID %s", workspace_id)
                return Client(api_key=self.api_key, api_url=self.endpoint, workspace_id=workspace_id)

            return Client(api_key=self.api_key, api_url=self.endpoint)
        except Exception as e:
            logger.warning("Failed to initialize LangSmith client: %s. Using synthetic fallback.", e)
            return None

    def fetch_traces(
        self,
        project_name: str,
        tags: Optional[List[str]] = None,
        prompt_tag: Optional[str] = None,
        limit: int = 20
    ) -> List[ExtractedTrace]:
        """
        Query LangSmith runs filtered by project and tags, extracting inputs,
        intermediate reasoning, and outputs.
        """
        if not self.client:
            return self._generate_mock_traces(project_name, tags, prompt_tag, limit)

        try:
            filter_conditions = []
            if prompt_tag:
                filter_conditions.append(f'has(tags, "{prompt_tag}")')
            if tags:
                for tag in tags:
                    filter_conditions.append(f'has(tags, "{tag}")')

            filter_str = " and ".join(filter_conditions) if filter_conditions else None

            runs_iterator = self.client.list_runs(
                project_name=project_name,
                filter=filter_str,
                run_type="chain",
                is_root=True,
                limit=limit
            )

            traces: List[ExtractedTrace] = []
            for run in runs_iterator:
                # Extract intermediate steps from child runs if available
                intermediate = []
                try:
                    child_runs = list(self.client.list_runs(parent_run_id=run.id, limit=10))
                    for child in child_runs:
                        intermediate.append({
                            "name": child.name,
                            "run_type": child.run_type,
                            "inputs": child.inputs,
                            "outputs": child.outputs
                        })
                except Exception:
                    pass

                latency = None
                if run.end_time and run.start_time:
                    latency = (run.end_time - run.start_time).total_seconds() * 1000

                token_usage = run.total_tokens if hasattr(run, "total_tokens") else None
                ref_out = None
                if run.outputs:
                    ref_out = run.outputs.get("output") or run.outputs.get("text") or str(run.outputs)

                traces.append(ExtractedTrace(
                    run_id=str(run.id),
                    name=run.name or "unnamed_run",
                    run_type=run.run_type or "chain",
                    inputs=run.inputs or {},
                    outputs=run.outputs or {},
                    intermediate_steps=intermediate,
                    tags=run.tags or [],
                    latency_ms=latency,
                    total_tokens=token_usage,
                    reference_output=ref_out
                ))

            logger.info("Successfully fetched %d traces from LangSmith project '%s'", len(traces), project_name)
            return traces

        except Exception as e:
            logger.error("Error querying LangSmith API: %s. Reverting to synthetic traces.", e)
            return self._generate_mock_traces(project_name, tags, prompt_tag, limit)

    def _generate_mock_traces(
        self,
        project_name: str,
        tags: Optional[List[str]] = None,
        prompt_tag: Optional[str] = None,
        limit: int = 5
    ) -> List[ExtractedTrace]:
        """Provides realistic golden reference traces for local testing and offline verification."""
        applied_tags = (tags or []) + ([prompt_tag] if prompt_tag else ["production-v1"])
        samples = [
            ExtractedTrace(
                run_id="run-trace-001",
                name="customer_support_intent_router",
                run_type="chain",
                inputs={
                    "query": "I would like to cancel my enterprise subscription and request a refund.",
                    "user_tier": "enterprise",
                    "user_id": "usr_9981"
                },
                outputs={
                    "intent": "cancellation_refund",
                    "confidence": 0.98,
                    "action": "route_to_retention_specialist",
                    "response": "I understand you wish to cancel your enterprise subscription. I am connecting you with our dedicated retention team."
                },
                intermediate_steps=[
                    {"name": "sentiment_analysis", "run_type": "llm", "outputs": {"sentiment": "neutral_negative"}},
                    {"name": "policy_checker", "run_type": "tool", "outputs": {"eligible_for_refund": True}}
                ],
                tags=applied_tags,
                latency_ms=420.5,
                prompt_tokens=140,
                completion_tokens=45,
                total_tokens=185,
                reference_output="I understand you wish to cancel your enterprise subscription. I am connecting you with our dedicated retention team."
            ),
            ExtractedTrace(
                run_id="run-trace-002",
                name="structured_invoice_extractor",
                run_type="chain",
                inputs={
                    "document_text": "Invoice #INV-2026-994. Billed to Acme Corp for Cloud Hosting. Amount: $4,500.00. Due Date: Nov 1, 2026."
                },
                outputs={
                    "invoice_id": "INV-2026-994",
                    "vendor": "Acme Corp",
                    "amount": 4500.00,
                    "currency": "USD",
                    "due_date": "2026-11-01"
                },
                intermediate_steps=[
                    {"name": "ocr_cleanup", "run_type": "tool", "outputs": {"cleaned": True}},
                    {"name": "entity_extraction", "run_type": "llm", "outputs": {"confidence": 0.99}}
                ],
                tags=applied_tags,
                latency_ms=610.0,
                prompt_tokens=220,
                completion_tokens=60,
                total_tokens=280,
                reference_output='{"invoice_id": "INV-2026-994", "amount": 4500.00}'
            ),
            ExtractedTrace(
                run_id="run-trace-003",
                name="rag_knowledge_synthesizer",
                run_type="chain",
                inputs={
                    "user_question": "What is our SLA for P1 database outages?",
                    "context": "P1 database outages carry an active resolution SLA of 15 minutes with 24/7 on-call dispatch."
                },
                outputs={
                    "answer": "Our active resolution SLA for P1 database outages is 15 minutes, supported by 24/7 on-call dispatch."
                },
                intermediate_steps=[],
                tags=applied_tags,
                latency_ms=315.2,
                prompt_tokens=95,
                completion_tokens=32,
                total_tokens=127,
                reference_output="Our active resolution SLA for P1 database outages is 15 minutes, supported by 24/7 on-call dispatch."
            )
        ]
        return samples[:limit]
