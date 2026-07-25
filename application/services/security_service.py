import logging
import re
from typing import List, Optional

from domain.services.career_assistant.safety_service import \
    ContentSafetyService

logger = logging.getLogger(__name__)


class SecurityService:
    """
    Application-level security layer.
    Handles PII enforcement, sanitization, and audit logging.
    """

    def __init__(self, safety_domain: ContentSafetyService):
        self._safety = safety_domain

    def sanitize_input(self, text: str) -> str:
        """Removes potentially dangerous characters or scripts."""
        if not text:
            return ""
        # Basic HTML/Script tag removal
        clean = re.sub(r"<[^>]*?>", "", text)
        return clean.strip()

    def validate_content_safety(self, content: str) -> List[str]:
        """Runs multi-stage safety checks on generated content."""
        issues = []

        if self._safety.detect_prompt_leakage(content):
            issues.append("Prompt instructions leaked into output.")

        pii = self._safety.detect_pii(content)
        if pii:
            issues.append(f"Potential PII detected: {', '.join(pii)}")

        sensitive = self._safety.check_sensitive_content(content)
        if sensitive:
            issues.append(f"Sensitive content detected: {', '.join(sensitive)}")

        return issues

    def record_security_event(self, event_type: str, actor_id: str, details: str):
        """Logs security-significant occurrences for audit trails."""
        logger.warning(
            f"SECURITY EVENT | type={event_type} | actor={actor_id} | {details}"
        )
