"""Database models and persistence layer for historical regressions and repository configurations."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from src.config import get_settings

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    repositories = relationship("Repository", back_populates="organization")


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    full_name = Column(String(200), unique=True, nullable=False)  # owner/repo
    webhook_secret = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="repositories")
    evaluations = relationship("EvaluationRun", back_populates="repository")


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True)  # job_id
    repo_name = Column(String(200), ForeignKey("repositories.full_name"), nullable=False)
    commit_sha = Column(String(40), nullable=False)
    pr_number = Column(Integer, nullable=True)
    status = Column(String(30), nullable=False)
    pass_rate = Column(Float, default=0.0)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    regression_detected = Column(Boolean, default=False)
    latency_p95_ms = Column(Float, default=0.0)
    token_usage = Column(Integer, default=0)
    markdown_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    repository = relationship("Repository", back_populates="evaluations")
    test_cases = relationship("TestCaseRecord", back_populates="evaluation_run", cascade="all, delete-orphan")


class TestCaseRecord(Base):
    __test__ = False

    __tablename__ = "test_case_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), ForeignKey("evaluation_runs.id"), nullable=False)
    test_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # regression, adversarial
    passed = Column(Boolean, nullable=False)
    score = Column(Float, default=0.0)
    schema_valid = Column(Boolean, default=True)
    error_details = Column(Text, nullable=True)

    evaluation_run = relationship("EvaluationRun", back_populates="test_cases")


def get_sync_engine(db_url: Optional[str] = None):
    settings = get_settings()
    url = db_url or settings.DATABASE_URL
    # For sync operations/local SQLite fallback
    if url.startswith("sqlite+aiosqlite:"):
        url = url.replace("sqlite+aiosqlite:", "sqlite:")
    elif url.startswith("postgresql+asyncpg:"):
        url = url.replace("postgresql+asyncpg:", "postgresql+psycopg2:")
    return create_engine(url, echo=False)


def init_db(engine=None):
    if engine is None:
        engine = get_sync_engine()
    Base.metadata.create_all(engine)
    return engine


def save_evaluation_record(job_id: str, repo_name: str, commit_sha: str, pr_number: Optional[int], result_dict: dict, engine=None):
    """Persist completed evaluation run and its test cases to the database."""
    engine = engine or init_db()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Ensure repository exists
        repo = session.query(Repository).filter_by(full_name=repo_name).first()
        if not repo:
            repo = Repository(id=repo_name, full_name=repo_name)
            session.add(repo)
            session.commit()

        # Check or create evaluation run
        run = session.query(EvaluationRun).filter_by(id=job_id).first()
        if not run:
            run = EvaluationRun(
                id=job_id,
                repo_name=repo_name,
                commit_sha=commit_sha,
                pr_number=pr_number,
                status=result_dict.get("status", "completed"),
                pass_rate=result_dict.get("pass_rate", 0.0),
                total_tests=result_dict.get("total_tests", 0),
                passed_tests=result_dict.get("passed_tests", 0),
                failed_tests=result_dict.get("failed_tests", 0),
                regression_detected=result_dict.get("regression_detected", False),
                latency_p95_ms=result_dict.get("latency_p95_ms", 0.0),
                token_usage=result_dict.get("token_usage_total", 0),
                markdown_report=result_dict.get("markdown_report", "")
            )
            session.add(run)

        # Add test case records
        details = result_dict.get("details", [])
        for d in details:
            tc = TestCaseRecord(
                run_id=job_id,
                test_name=d.get("name", "unnamed"),
                category=d.get("category", "regression"),
                passed=d.get("passed", False),
                score=d.get("score", 0.0),
                schema_valid=d.get("schema_valid", True),
                error_details="; ".join(d.get("schema_errors", [])) if d.get("schema_errors") else d.get("judge_reasoning", "")
            )
            session.add(tc)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

