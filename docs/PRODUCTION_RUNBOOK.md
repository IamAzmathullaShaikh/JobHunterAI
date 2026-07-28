# JobHunterAI Production Runbook

This document provides operational guidelines for deploying and maintaining JobHunterAI in a production environment.

## 🚀 Deployment

### Docker (Recommended)
1. Ensure your `.env` file is configured for production (`ENVIRONMENT=production`).
2. Run `docker-compose up -d --build`.
3. The application will be available on the `PORT` specified (default 8000).

### Manual (Bare Metal)
1. Build frontend: `cd frontend && npm install && npm run build`.
2. Setup backend: `pip install -r backend/requirements.txt`.
3. Start server: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.

## 🛡️ Security
- **PII Redaction**: Ensure `redactor` is active in `core/privacy.py` for cloud AI requests.
- **Audit Logs**: Mutative actions are tracked in the `audit_logs` database table.
- **File Access**: The `/download` endpoint is hardened against path traversal.

## 📈 Monitoring & Observability
- **Logs**: Standard logs are in `logs/system.log`. AI specific metrics in `logs/ai.log`.
- **Request Tracing**: Use the `X-Request-ID` header to correlate logs across services.
- **Cost Tracking**: AI cost estimates are logged per completion in `ai.log`.

## 🆘 Troubleshooting
- **Database Outage**: verify `DATABASE_URL` connectivity.
- **AI Rate Limits**: The `smart_router` will automatically fallback to secondary tiers.
- **Scraper Blocks**: verify proxy settings or Apify Actor health.

## 💾 Backup & Recovery
- **SQLite**: Perform a filesystem copy of `jobhunter.db` daily.
- **PostgreSQL**: Use `pg_dump` for standard backups.
