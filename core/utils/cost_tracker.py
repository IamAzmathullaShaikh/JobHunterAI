import logging
from typing import Dict, Optional

logger = logging.getLogger("jobhunterai.cost_tracker")

class CostTracker:
    """
    Estimates the financial cost of AI completions based on token usage.
    Pricing as of July 2026 (Estimates).
    """

    PRICING = {
        "groq": {
            "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79}, # per 1M tokens
            "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08}
        },
        "gemini": {
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00}
        },
        "openai": {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60}
        }
    }

    @staticmethod
    def estimate_cost_usd(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculates estimated USD cost for a completion."""
        provider = provider.lower()
        model = model.lower()

        rates = CostTracker.PRICING.get(provider, {}).get(model)
        if not rates:
            # Fallback to provider defaults if model not found
            if provider == "groq": rates = {"input": 0.6, "output": 0.8}
            elif provider == "gemini": rates = {"input": 0.1, "output": 0.4}
            else: return 0.0 # Unknown

        cost = (input_tokens / 1_000_000 * rates["input"]) + (output_tokens / 1_000_000 * rates["output"])
        return round(cost, 6)

    @staticmethod
    def log_completion(provider: str, model: str, usage: Dict[str, int], request_id: Optional[str] = None):
        """Standardized log for AI completions with cost tracking."""
        in_t = usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0)
        out_t = usage.get("completion_tokens", 0) or usage.get("output_tokens", 0)

        cost = CostTracker.estimate_cost_usd(provider, model, in_t, out_t)

        msg = f"AI Completion | Provider: {provider} | Model: {model} | Tokens: {in_t + out_t} | Cost: ${cost:.6f}"
        if request_id:
            msg = f"[{request_id}] {msg}"

        logger.info(msg)
        return cost
