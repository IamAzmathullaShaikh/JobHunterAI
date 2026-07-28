import pytest
from core.utils.cost_tracker import CostTracker

def test_cost_calculation():
    # Groq Llama 3 70B: input 0.59, output 0.79 per 1M
    # 100k input, 100k output
    cost = CostTracker.estimate_cost_usd("groq", "llama-3.3-70b-versatile", 100_000, 100_000)
    # (0.1 * 0.59) + (0.1 * 0.79) = 0.059 + 0.079 = 0.138
    assert cost == 0.138

def test_cost_calculation_fallback():
    # Unknown model should use provider default
    cost = CostTracker.estimate_cost_usd("groq", "unknown-model", 1_000_000, 1_000_000)
    # Default 0.6 + 0.8 = 1.4
    assert cost == 1.4
