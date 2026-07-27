# ADR 0001: Multi-Tier AI Routing Strategy

## Status
Accepted

## Context
JobHunterAI requires highly intelligent reasoning for resume tailoring and interview coaching, but also needs to remain cost-effective and resilient to API outages. Relying on a single cloud provider (e.g., OpenAI or Groq) introduces a single point of failure and potential cost spikes.

## Decision
We will implement a **3-Tier AI Routing Architecture**:

1.  **Tier 1 (High Performance/Reasoning)**: Primary calls to Groq (Llama 3.3) for sub-second high-intelligence tasks.
2.  **Tier 2 (Fallback/Deep Logic)**: Secondary calls to Google Gemini (1.5 Flash) if Tier 1 is rate-limited or unavailable.
3.  **Tier 3 (Local/Zero-Cost)**: Local execution using Sentence-Transformers (MiniLM) or Ollama for basic semantic matching and offline capabilities.

## Consequences
- **Resilience**: The application remains functional even during major cloud AI outages.
- **Cost Optimization**: Developers can choose to use Tier 3 for local development to save on API credits.
- **Privacy**: Local fallback allows for potentially processing sensitive data without cloud transmission (if configured).
- **Complexity**: Requires maintaining multiple provider clients and mapping capabilities across different model schemas.
