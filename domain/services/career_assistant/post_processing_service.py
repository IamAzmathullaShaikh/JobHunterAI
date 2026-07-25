import re
from typing import List


class ContentPostProcessingService:
    """
    Pure logic for cleaning and formatting AI-generated text.
    """

    @staticmethod
    def cleanup_formatting(text: str) -> str:
        """Removes markdown artifacts and extra whitespace."""
        # Remove repeated newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove trailing/leading whitespace
        text = text.strip()
        # Remove AI "chatter" if present (heuristic)
        chatter_patterns = [
            r"^Here is the tailored resume.*?\n",
            r"^Sure, I can help with that.*?\n",
            r"I hope this helps!.*$",
        ]
        for pattern in chatter_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
        return text.strip()

    @staticmethod
    def mask_sensitive_data(text: str, sensitive_terms: List[str]) -> str:
        """Simple masking for sensitive terms that shouldn't be in generated content."""
        processed = text
        for term in sensitive_terms:
            processed = processed.replace(term, "[MASKED]")
        return processed

    @staticmethod
    def enforce_word_limit(text: str, limit: int) -> str:
        words = text.split()
        if len(words) <= limit:
            return text
        return " ".join(words[:limit]) + "..."
