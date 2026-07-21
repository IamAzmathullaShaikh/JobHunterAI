import re
from typing import Dict, Tuple

class PIIRedactor:
    """
    Redacts and restores PII (Personally Identifiable Information) from text
    to protect user privacy when sending data to external AI providers.
    """

    # Simple patterns for redaction
    PATTERNS = {
        "EMAIL": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        "PHONE": r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        "ADDRESS": r'\d+\s+[a-zA-Z0-9\s,.]+?\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Court|Ct|Way|Lane|Ln|Trail|Trl|Circle|Cir|Zip|Parkway|Pkwy|Plaza|Plz)\b'
    }

    def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Redacts PII from text and returns the redacted text and a mapping to restore it.
        """
        if not text:
            return "", {}

        mapping = {}
        redacted_text = text

        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, redacted_text, re.IGNORECASE)
            for i, match in enumerate(matches):
                # Ensure we don't double redact or miss similar patterns
                placeholder = f"[[REDACTED_{pii_type}_{i}]]"
                mapping[placeholder] = match
                redacted_text = redacted_text.replace(match, placeholder)

        return redacted_text, mapping

    def restore(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Restores redacted PII in the text using the provided mapping.
        """
        if not text or not mapping:
            return text

        restored_text = text
        for placeholder, original in mapping.items():
            restored_text = restored_text.replace(placeholder, original)

        return restored_text

# Global singleton for easy access
redactor = PIIRedactor()
