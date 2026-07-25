# Administration Guide

This document is for system administrators managing enterprise-level deployments of JobHunterAI.

## 1. User Management
The current version of JobHunterAI is designed for single-user scenarios. For multi-user administrative needs, we recommend:
- Deploying unique instances per user using a container orchestrator (Kubernetes/Docker Swarm).
- Using an external auth provider (e.g., Authelia, Keycloak) at the proxy level.

## 2. Prompt Engineering
The AI prompts are located in `backend/prompts/`. Administrators can modify these `.j2` (Jinja2) templates to fine-tune:
- `resume_tailoring.j2`: How the AI suggests resume changes.
- `cover_letter_gen.j2`: The tone and structure of generated letters.
- `interview_questions.j2`: The difficulty and type of mock questions.

## 3. Scraper Configuration
Scrapers can be fine-tuned via `configs/scraper_config.json`.
- **Concurrency**: Limit the number of simultaneous scraper workers to avoid IP bans.
- **Rotation**: If using cloud scrapers (Apify), configure proxy rotation in the settings.

## 4. System Updates
To update JobHunterAI:
1. Pull the latest code from the repository.
2. Run migrations: `alembic upgrade head`.
3. Re-install dependencies: `pip install -r requirements.txt` and `npm install`.
4. Rebuild frontend: `npm run build`.
