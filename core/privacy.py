import re
import uuid
from typing import Dict, Tuple


class PIIRedactor:
    """
    Redacts and restores PII (Personally Identifiable Information) from text
    using atomic regex substitution and UUID placeholders to prevent collisions.
    """

    # Simple patterns for redaction
    PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "PHONE": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "ADDRESS": r"\d+\s+[a-zA-Z0-9\s,.]+?\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Court|Ct|Way|Lane|Ln|Trail|Trl|Circle|Cir|Zip|Parkway|Pkwy|Plaza|Plz)\b",
    }

    def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Redacts PII from text and returns the redacted text and a mapping to restore it.
        Uses atomic substitution to prevent partial redaction bugs.
        """
        if not text:
            return "", {}

        mapping = {}
        redacted_text = text

        def replacer(match):
            placeholder = f"[[REDACTED_{pii_type}_{uuid.uuid4().hex[:8]}]]"
            val = match.group(0)
            mapping[placeholder] = val
            return placeholder

        for pii_type, pattern in self.PATTERNS.items():
            redacted_text = re.sub(pattern, replacer, redacted_text, flags=re.IGNORECASE)

        return redacted_text, mapping

    def restore(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Restores redacted PII in the text using the provided mapping.
        """
        if not text or not mapping:
            return text

        restored_text = text
        # Sort placeholders by length descending to prevent partial replacement if any overlap
        for placeholder in sorted(mapping.keys(), key=len, reverse=True):
            restored_text = restored_text.replace(placeholder, mapping[placeholder])

        return restored_text


# Global singleton for easy access
redactor = PIIRedactor()
