# AI & Intelligence

JobHunterAI is "AI-Native", meaning AI is integrated into the core of almost every feature.

## 1. The Smart Router
The Smart Router is a custom implementation that manages model selection and fallbacks.

- **Objective**: Balance cost, latency, and quality.
- **Logic**: 
    - Complexity < 0.3 -> Use Local (Sentence-Transformers).
    - Complexity > 0.3 AND Latency-Sensitive -> Use Groq (Llama 3.3).
    - Complexity > 0.8 -> Use Gemini (1.5 Flash) for deeper reasoning.
- **Circuit Breaker**: If a provider fails 3 times in a row, it is temporarily disabled for 5 minutes.

## 2. Prompt Management
All AI prompts are stored as **Jinja2 templates** in `backend/prompts/`. This allows:
- **Versioned Prompts**: Tracking how prompt changes affect output quality.
- **Dynamic Context**: Injecting user profile data and job details into the prompt at runtime.
- **Structured Output**: Forcing the AI to return valid JSON using specialized system instructions.

## 3. Local Intelligence
For users who prefer 100% offline usage, JobHunterAI supports **Ollama**.
- By setting `AI_PROVIDER=ollama`, the system will use a local Llama or Qwen model for all reasoning tasks.
- **Embeddings**: Local skill matching is performed using `sentence-transformers` running on your CPU/GPU.
