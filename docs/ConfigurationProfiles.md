# JobHunterAI Configuration Profiles

## Development (`.env.dev`)
- `DEBUG=True`
- `AI_PROVIDER=groq`
- `DATABASE_URL=sqlite+aiosqlite:///dev.db`
- `CORS_ORIGINS=["*"]`
- `LOG_LEVEL=DEBUG`

## Testing (`.env.test`)
- `DEBUG=True`
- `AI_PROVIDER=mock`
- `DATABASE_URL=sqlite+aiosqlite:///:memory:`
- `CORS_ORIGINS=["*"]`
- `LOG_LEVEL=CRITICAL`

## Staging (`.env.staging`)
- `DEBUG=False`
- `AI_PROVIDER=gemini`
- `DATABASE_URL=sqlite+aiosqlite:///staging.db`
- `CORS_ORIGINS=["https://staging.jobhunter.ai"]`
- `LOG_LEVEL=INFO`

## Production (`.env.prod`)
- `DEBUG=False`
- `AI_PROVIDER=groq`
- `DATABASE_URL=sqlite+aiosqlite:///prod.db`
- `CORS_ORIGINS=["https://app.jobhunter.ai"]`
- `LOG_LEVEL=WARNING`
- `MATCHING_CONFIG_VERSION=1.0.0`
