# Operations & Monitoring

This guide covers how to monitor and maintain a running instance of JobHunterAI.

## 1. Health Checks
The `/api/health` endpoint provides a comprehensive status of the system:
- **Database Connectivity**: Status of the SQLite/Postgres connection.
- **AI Providers**: Checks if API keys are configured and if providers are reachable.
- **Scraper Status**: Readiness of the scraping fleet.

## 2. Telemetry & Metrics
The `/api/system/telemetry` endpoint returns real-time metrics:
- **AI Latency**: Average response time per provider.
- **Circuit Breakers**: Status of the fallback system (Open/Closed/Half-Open).
- **Token Usage**: Estimated usage across providers.
- **Success Rates**: Percentage of successful vs failed AI generations.

## 3. Logging
Logs are stored in the directory specified by `LOG_DIR` (default: `logs/`).
- `app.log`: General application events and errors.
- `ai.log`: Detailed traces of AI prompts and responses (sensitive data redacted).
- `scraper.log`: Detailed traces of job discovery runs.

## 4. Database Maintenance
- **Backups**: Since the system uses SQLite by default, a simple file copy of `jobhunter.db` is sufficient for backups.
- **Pruning**: We recommend periodic pruning of old job listings (older than 90 days) to keep the database size manageable.
