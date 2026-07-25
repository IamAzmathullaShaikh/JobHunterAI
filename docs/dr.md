# Disaster Recovery Plan v1.0.0

## Recovery Objectives
- **RTO (Recovery Time Objective)**: < 1 hour.
- **RPO (Recovery Point Objective)**: < 24 hours.

## Data Backup
- **SQLite DB**: Daily automated snapshot of `jobhunter.db` to encrypted offsite storage.
- **Files**: Resume PDFs are stored in S3/R2 with versioning enabled.

## Recovery Procedures
1. **Infrastructure Failure**:
    - Re-deploy DI Container and FastAPI backend using Docker images from the registry.
2. **Database Corruption**:
    - Restore latest `jobhunter.db` snapshot.
    - Re-run `alembic upgrade head`.
3. **Provider Outage**:
    - Continuous Operation mode enabled via `FallbackContentGenerator`. No action required for basic functionality.

## Emergency Configuration
- If `.env` is lost, retrieve master keys from Vault and rebuild using `.env.example`.
