# Operational Runbook: Incident Response

## Provider Failure (AI/Scraper)
1. **Detection**: Telemetry Engine reports `CircuitStateChanged` to `OPEN`.
2. **Action**:
    - Verify API Keys in `Settings`.
    - Check Provider Status Page (Groq/Apify).
    - If provider is down, the system automatically uses Deterministic Fallbacks.
3. **Manual Reset**: Call `manager.reload_provider(id)` if the provider is recovered but the circuit is still open.

## Health Failures
1. **Detection**: `/api/health` returns `unhealthy` or `degraded`.
2. **Database down**: Check disk space and SQLite file permissions.
3. **Configuration missing**: Review startup logs for `PlatformValidationService` errors.

## Cache Invalidation
1. **Action**: If analytics or match scores are inconsistent, call `cache_coordinator.clear()`.
2. **Candidate Specific**: Call `invalidate_context(candidate_id)` if a specific profile is corrupt.

## Deployment Rollback
1. **Action**: Revert to the previous Git Tag.
2. **Database**: If migrations were applied, run `alembic downgrade -1`.
