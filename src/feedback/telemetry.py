"""PostHog telemetry integration for LLM CI/CD regression metrics."""
import logging
from typing import Any, Dict, Optional
from src.config import get_settings

logger = logging.getLogger(__name__)


class TelemetryLogger:
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if self.settings.POSTHOG_API_KEY:
            try:
                import posthog
                posthog.api_key = self.settings.POSTHOG_API_KEY
                posthog.host = self.settings.POSTHOG_HOST
                self.client = posthog
                logger.info("Initialized PostHog telemetry client.")
            except Exception as e:
                logger.warning("Failed to initialize PostHog: %s", e)

    def log_evaluation_event(
        self,
        event_name: str,
        distinct_id: str,
        properties: Dict[str, Any]
    ) -> bool:
        """Send telemetry event to PostHog if configured."""
        if not self.client:
            logger.debug("[Mock Telemetry Event] %s (%s): %s", event_name, distinct_id, properties)
            return True

        try:
            self.client.capture(
                distinct_id=distinct_id,
                event=event_name,
                properties=properties
            )
            return True
        except Exception as e:
            logger.error("Failed to emit PostHog event: %s", e)
            return False
