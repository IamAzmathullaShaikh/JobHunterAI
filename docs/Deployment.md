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
