"""Central configuration settings using Pydantic Settings."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Task Broker (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_QUEUE_NAME: str = "llm_eval_jobs"
    RATE_LIMIT_PER_MINUTE: int = 60

    # GitHub Integration
    GITHUB_WEBHOOK_SECRET: Optional[str] = "dev_secret_key"
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_APP_ID: Optional[str] = None
    GITHUB_APP_PRIVATE_KEY: Optional[str] = None
    GITHUB_BOT_NAME: str = "llm-regression-bot[bot]"

    # LangSmith Tracing
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_WORKSPACE_ID: Optional[str] = None
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_DEFAULT_PROJECT: str = "default"

    # LiteLLM Proxy / BYOK Gateway
    LITELLM_PROXY_URL: str = "http://localhost:4000"
    LITELLM_MASTER_KEY: str = "sk-litellm-proxy-master-key"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Persistent Storage
    DATABASE_URL: str = "sqlite+aiosqlite:///./regression_engine.db"

    # Telemetry
    POSTHOG_API_KEY: Optional[str] = None
    POSTHOG_HOST: str = "https://app.posthog.com"


@lru_cache()
def get_settings() -> Settings:
    """Return cached singleton settings instance."""
    return Settings()
