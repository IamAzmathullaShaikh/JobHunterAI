import re
from typing import Any, Dict, List, Optional


class ContentSafetyService:
    """
    Pure logic for detecting prompt leakage, sensitive data,
    and ensuring generated content safety.
    """

    @staticmethod
    def detect_prompt_leakage(content: str) -> bool:
        """Detects if the AI output contains parts of its own instructions."""
        leakage_keywords = [
            "you are an ai",
            "as a large language model",
            "here are your instructions",
            "system prompt",
            "the following context",
            "your task is to",
        ]
        lower_content = content.lower()
        return any(k in lower_content for k in leakage_keywords)

    @staticmethod
    def detect_pii(content: str) -> List[str]:
        """Detects potential PII leaks in generated content."""
        patterns = {
            "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        }
        found = []
        for label, pattern in patterns.items():
            if re.search(pattern, content):
                found.append(label)
        return found

    @staticmethod
    def validate_markdown(content: str) -> bool:
        """Basic check for valid markdown structure (e.g. balanced backticks)."""
        # Count occurrences of triple backticks
        return content.count("```") % 2 == 0

    @staticmethod
    def check_sensitive_content(content: str) -> List[str]:
        """Detects potentially sensitive or inappropriate terms."""
        # This would be a simple blocklist for a local engine or heuristic
        blocked = ["internal-only", "confidential-client-x", "password:"]
        found = []
        lower_content = content.lower()
        for term in blocked:
            if term in lower_content:
                found.append(term)
        return found
