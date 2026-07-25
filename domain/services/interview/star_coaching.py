from typing import List, Optional

from domain.shared.value_objects import STARAnalysis


class STARCoachingService:
    """
    Pure logic for analyzing an answer using the STAR method (Situation, Task, Action, Result).
    Uses rule-based heuristics to identify missing components.
    """

    @staticmethod
    def analyze_answer(text: str) -> STARAnalysis:
        # Heuristic keywords for each component
        keywords = {
            "situation": ["when", "during", "while", "at my last", "context"],
            "task": ["assigned", "tasked", "responsible", "goal", "objective"],
            "action": ["i did", "i created", "i built", "i implemented", "i managed"],
            "result": [
                "resolved",
                "outcome",
                "result",
                "saved",
                "increased",
                "decreased",
                "%",
            ],
        }

        lower_text = text.lower()

        has_s = any(k in lower_text for k in keywords["situation"])
        has_t = any(k in lower_text for k in keywords["task"])
        has_a = any(k in lower_text for k in keywords["action"])
        has_r = any(k in lower_text for k in keywords["result"])

        found_count = sum([has_s, has_t, has_a, has_r])
        score = found_count / 4.0

        suggestions = []
        if not has_s:
            suggestions.append("Start by describing the specific context or situation.")
        if not has_t:
            suggestions.append(
                "Clearly state what your specific task or challenge was."
            )
        if not has_a:
            suggestions.append(
                "Detail the specific actions YOU took to address the challenge."
            )
        if not has_r:
            suggestions.append(
                "Always include the final result or outcome, ideally with data/metrics."
            )

        feedback = (
            "Great start!"
            if score > 0.7
            else "Your response is missing some key STAR components."
        )

        return STARAnalysis(
            has_situation=has_s,
            has_task=has_t,
            has_action=has_a,
            has_result=has_r,
            completeness_score=score,
            feedback=feedback,
            suggestions=suggestions,
        )
