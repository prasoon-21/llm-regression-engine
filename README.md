# LLM CI/CD Regression & Red-Teaming Engine

An automated regression testing, red-teaming, and CI/CD gating platform for LLM systems integrated with **LangSmith**, **Promptfoo**, **FastAPI**, **LiteLLM**, and **GitHub**.

---

## 🏗️ Architecture & Topology

```
                  ┌───────────────────────────────────────────────┐
                  │                 GitHub PR                     │
                  │ (Webhooks, Status Checks, Markdown Comments)  │
                  └───────┬───────────────────────────────▲───────┘
                          │ Webhook Payload               │ Commit Status &
                          │ (HMAC SHA-256)                │ PR Comments
                          ▼                               │
                ┌──────────────────┐                      │
                │   API Gateway    │                      │
                │    (FastAPI)     │                      │
                └─────────┬────────┘                      │
                          │ Pushes Job                    │
                          ▼                               │
                ┌──────────────────┐                      │
                │   Task Broker    │                      │
                │  (Redis 7 / TTL) │                      │
                └─────────┬────────┘                      │
                          │ Pops Job                      │
                          ▼                               │
                ┌──────────────────┐                      │
                │Evaluation Worker │──────────────────────┘
                │  (Python + Node) │
                └────┬───────────┬─┘
                     │           │
     Queries Traces  │           │ Evaluates via BYOK
                     ▼           ▼
        ┌──────────────────┐   ┌───────────────────────────┐
        │    LangSmith     │   │   Unified Model Proxy     │
        │(Trace Harvesting)│   │  (LiteLLM / OpenAI / etc) │
        └──────────────────┘   └───────────────────────────┘
```

---

## 🚀 Key Capabilities

1. **GitHub Webhook Ingestion & Cryptographic Security:**
   - Verifies `X-Hub-Signature-256` HMAC-SHA256 signatures to block forged requests.
   - Handles `pull_request` (`opened`, `synchronize`, `reopened`) and `ping` events.
   - Enforces per-repository token-bucket rate limiting.

2. **LangSmith Trace Harvesting:**
   - Filters traces by project, prompt tags, and execution status.
   - Extracts input payloads, reasoning steps, tool calls, and ground-truth references.

3. **Adversarial Red-Teaming & Test Synthesis:**
   - Generates automated adversarial mutations: prompt injections, delimiter breakouts, malformed JSON, and safety probes.
   - Compiles structured test suites ready for Promptfoo execution.

4. **Multi-Layer Validation Engine:**
   - **Schema Conformance:** Strict Pydantic / Instructor validation ensuring structured JSON response integrity.
   - **LLM-as-a-Judge:** Semantic rubric evaluation for instruction following, factual accuracy, and safety.
   - **Performance & Safety Audits:** P50/P95/P99 latency tracking, token consumption delta gating, and regression detection.

5. **CI/CD Gating & Feedback Loop:**
   - Sets GitHub Commit Status Check (`pending` → `success` or `failure`).
   - Automatically posts formatted Markdown regression reports directly into GitHub Pull Request comments.
   - Dispatches execution telemetry to PostHog.

---

## 📁 Repository Structure

```
p:/langSmith/
├── docker-compose.yml              # 5-container topology (Gateway, Redis, LiteLLM, Worker, Postgres)
├── Dockerfile.gateway               # API Gateway container
├── Dockerfile.worker                # Hybrid Python 3.11 + Node 20 Worker container
├── litellm_config.yaml              # Unified Model Proxy config (OpenAI, Anthropic, Gemini)
├── requirements.txt                 # Core dependencies
├── requirements-lock.txt            # Frozen exact dependency versions
├── .env.example                     # Environment template
├── src/
│   ├── config.py                    # Pydantic Settings
│   ├── security.py                  # HMAC SHA256 webhook validator
│   ├── api/
│   │   ├── main.py                  # FastAPI gateway, health checks, manual trigger
│   │   └── webhook.py               # GitHub Webhook handler
│   ├── broker/
│   │   ├── queue.py                 # Redis queue manager & rate limiting
│   │   └── schemas.py               # EvaluationJob & JobResult models
│   ├── harvesting/
│   │   └── langsmith_extractor.py   # LangSmith trace extractor
│   ├── synthesis/
│   │   ├── adversarial.py           # Synthetic adversarial payload generator
│   │   └── test_suite_builder.py    # Promptfoo test suite compiler
│   ├── validation/
│   │   ├── schema_validator.py      # Instructor / Pydantic schema validation
│   │   ├── judge.py                 # LLM-as-a-Judge semantic rubric evaluator
│   │   ├── audit.py                 # Token & latency regression auditor
│   │   └── runner.py                # Pipeline execution coordinator & Promptfoo CLI
│   ├── feedback/
│   │   ├── github_checks.py         # GitHub Commit Status & Check Runs
│   │   ├── pr_reporter.py           # Markdown PR comment reporter
│   │   └── telemetry.py             # PostHog analytics logger
│   ├── storage/
│   │   └── db.py                    # Relational schema (Postgres / Supabase / SQLite)
│   └── worker.py                    # Worker loop coordinating full evaluation workflow
└── tests/
    ├── test_security.py             # Webhook signature tests
    ├── test_webhook.py              # Ingestion & rate-limiting tests
    ├── test_queue.py                # Broker queue & state tests
    ├── test_langsmith_harvest.py    # Trace extraction tests
    ├── test_synthesis.py            # Promptfoo config & adversarial tests
    ├── test_validation.py           # Schema conformance & Judge tests
    ├── test_feedback.py             # GitHub comment & status tests
    └── test_e2e_pipeline.py         # Complete end-to-end integration test
```

---

## 🛠️ Local Development & Testing

### 1. Initialize Virtual Environment & Dependencies
```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 2. Configure Environment
```powershell
cp .env.example .env
```

### 3. Run Test Suite
```powershell
.venv\Scripts\pytest -v
```

### 4. Run the API Gateway Locally
```powershell
.venv\Scripts\uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Run the Worker Locally
```powershell
.venv\Scripts\python -m src.worker
```

---

## 🐳 Docker Deployment

To launch all 5 containers in the bridge network topology:
```bash
docker compose up --build -d
```
