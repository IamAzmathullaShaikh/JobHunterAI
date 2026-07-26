# Deployment Guide

JobHunterAI is designed to be deployed in various environments, from a local workstation to a production cloud server.

## 1. Docker Deployment (Recommended)

The easiest way to deploy JobHunterAI is using Docker Compose.

```bash
# Build and start all services
docker-compose up --build -d
```

This will spin up:
- **Backend**: FastAPI service on port 8000.
- **Frontend**: Nginx serving the static React build on port 80.
- **Database**: SQLite volume persisted at `/app/data`.

## 2. Production Hardening

When deploying to a public server, ensure the following:

### Environment Variables
Set `NODE_ENV=production` in your `.env` file. This disables Swagger UI and enables stricter CORS policies.

### Reverse Proxy
It is recommended to use **Nginx** or **Traefik** as a reverse proxy in front of the application to handle SSL/TLS termination.

### Database
For high-traffic production use, we recommend migrating from SQLite to **PostgreSQL**. Update the `DATABASE_URL` in your `.env`:
`DATABASE_URL=postgresql+asyncpg://user:password@localhost/jobhunter`

## 3. Cloud Provider Setup

### Groq / Gemini
Ensure your API keys are set as environment variables in your deployment platform (e.g., Vercel, AWS ECS, Railway).

### Storage
Persistent storage must be configured for the `jobhunter.db` file if using SQLite, otherwise, data will be lost on container restart.

## 4. Production Launch Checklist

Before declaring a production deployment "Live", verify the following:

- [ ] `ENVIRONMENT=production` is set.
- [ ] `CORS_ORIGINS` is configured with explicit domains (no `*`).
- [ ] Database is migrated to latest head (`alembic upgrade head`).
- [ ] Health endpoint `/api/health` returns `healthy`.
- [ ] AI API keys (Groq/Gemini) are valid and have sufficient quota.
- [ ] Backup schedule is established for the database.
- [ ] Log rotation is configured to prevent disk exhaustion.

## 5. Backup & Restore

### SQLite Backup (Local)
To backup the local database, simply copy the `jobhunter.db` file:
```bash
cp /app/data/jobhunter.db /backups/jobhunter_$(date +%F).db
```

### PostgreSQL Backup
If using PostgreSQL, use `pg_dump`:
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore
To restore, replace the `jobhunter.db` file (SQLite) or run the SQL script (Postgres).
