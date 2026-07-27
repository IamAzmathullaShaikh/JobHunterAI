# ADR 0002: Multi-Tenant Data Isolation Strategy

## Status
Accepted (Foundation Phase)

## Context
While JobHunterAI 1.0 is designed as a single-user "Pro" tool, the long-term vision is a multi-user SaaS platform. To avoid massive database migrations in the future, we need to prepare the data layer for multi-tenancy today.

## Decision
We will add an optional `user_id` field (UUID) to all core entities in the database schema:
- `resumes`
- `cover_letters`
- `job_applications`
- `interview_sessions`
- `job_listings`

In version 1.0, this field will remain nullable and will default to `None` for single-user local deployments.

## Consequences
- **Future-Proofing**: Version 2.0 can introduce authentication and authorization (RBAC) without altering the table structures.
- **Migration Path**: Existing single-user data can be assigned to the first registered user during a SaaS migration.
- **Clean Schema**: Even in local mode, the presence of `user_id` serves as a reminder to implement proper scoping in service/repository layers.
