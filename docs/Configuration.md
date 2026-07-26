# Configuration Guide

JobHunterAI uses a central configuration system powered by `Pydantic Settings`.

## 1. Environment Variables (`.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | `development` or `production`. Aliases: `NODE_ENV`. |
| `DEBUG` | `True` | Enables debug logging and Swagger UI |
| `DATABASE_URL` | `sqlite:///jobhunter.db` | SQLAlchemy connection string |
| `AI_PROVIDER` | `groq` | Primary provider (`groq`, `gemini`, `openai`, `ollama`, `auto`) |
| `DEFAULT_AI_PROVIDER`| `groq` | Used when `AI_PROVIDER=auto` |
| `FALLBACK_AI_PROVIDER`| `gemini` | Used when `AI_PROVIDER=auto` and default fails |
| `LOCAL_AI_PROVIDER` | `ollama` | Used when `AI_PROVIDER=auto` and fallback fails |
| `CORS_ORIGINS` | `["*"]` | Allowed origins (CSV or JSON array) |
| `GROQ_API_KEY` | - | Required for Groq AI features |
| `GEMINI_API_KEY` | - | Required for Gemini AI features |
| `APIFY_API_TOKEN` | - | Required for cloud scraping |

## 2. Matching Weights
You can adjust the importance of different matching factors in `core/config/settings.py` or via environment variables if configured:

```json
{
  "skills": 0.35,
  "experience": 0.25,
  "education": 0.10,
  "keywords": 0.15,
  "location": 0.10,
  "salary": 0.05
}
```

## 3. AI Model Selection
The system allows configuring specific models per provider:
- `GROQ_MODEL`: Default `llama-3.3-70b-versatile`
- `GEMINI_MODEL`: Default `gemini-1.5-flash`
- `OLLAMA_MODEL`: Default `qwen2.5-coder:7b`

## 4. Privacy Settings
- **PII Redaction**: Can be toggled in the system settings. When enabled, the system uses a local regex engine to mask sensitive data before sending it to cloud providers.
