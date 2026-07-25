import re
from typing import List, Optional


class ContentValidationService:
    """
    Pure logic for validating AI-generated career content.
    Ensures quality and safety before content reaches the user.
    """

    @staticmethod
    def validate_length(
        content: str, min_chars: int = 10, max_chars: int = 5000
    ) -> bool:
        return min_chars <= len(content) <= max_chars

    @staticmethod
    def detect_placeholders(content: str) -> List[str]:
        """Detects common AI-generated placeholders like [Name] or {{Company}}."""
        patterns = [
            r"\[.*?\]",
            r"\{{.*?\}}",
            r"\<.*?\>",
            r"INSERT\s+[A-Z_]+",
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, content))
        return list(set(matches))

    @staticmethod
    def check_mandatory_keywords(content: str, keywords: List[str]) -> List[str]:
        """Returns a list of missing mandatory keywords."""
        missing = []
        lower_content = content.lower()
        for kw in keywords:
            if kw.lower() not in lower_content:
                missing.append(kw)
        return missing

    @staticmethod
    def calculate_quality_score(
        content: str, placeholders: List[str], missing_keywords: List[str]
    ) -> float:
        """Calculates a heuristic quality score (0.0 to 1.0)."""
        score = 1.0

        # Penalize placeholders heavily
        score -= len(placeholders) * 0.2

        # Penalize missing keywords
        if missing_keywords:
            score -= len(missing_keywords) * 0.1

        # Penalize very short content
        if len(content) < 50:
            score -= 0.3

        return max(0.0, min(1.0, round(score, 2)))
