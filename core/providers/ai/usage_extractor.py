from typing import Any, Dict, Optional


class GroqUsageExtractor:
    """
    Extracts and standardizes token usage and cost metrics from Groq responses.
    """

    @staticmethod
    def extract(response: Any) -> Dict[str, Any]:
        """
        Pulls usage metadata from a Groq ChatCompletion object.
        """
        usage = getattr(response, "usage", None)
        if not usage:
            return {}

        prompt_tokens = getattr(usage, "prompt_tokens", 0)
        completion_tokens = getattr(usage, "completion_tokens", 0)
        total_tokens = getattr(usage, "total_tokens", 0)

        # Approximate cost calculation for Groq (currently mostly free/low-cost)
        # Placeholder values for enterprise tracking
        estimated_cost = 0.0

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
        }
