# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-26

### Added
- **Production Resume Platform**: Multi-document vault with 10 professional A4 templates.
- **AI Interview Coach**: Stateful mock interviews with real-time scoring and STAR method feedback.
- **Recruiter CRM**: Discovery and tracking of decision-makers with AI-powered outreach drafting.
- **Unified Mission Control**: Career analytics dashboard with chronological activity timelines.
- **Smart AI Router**: 3-tier fallback and capability-based routing (Groq -> Gemini -> Local).
- **Job Discovery Engine**: Parallel multi-provider scraping with intelligent deduplication and AI enrichment.
- **High-Fidelity Export**: Pixel-perfect PDF (Playwright), DOCX, and Markdown resume/CL downloads.

### Changed
- **Architecture**: Decoupled AI models from business logic using a Capability-based system.
- **Database**: Migrated to a unified PostgreSQL schema with comprehensive Alembic versioning.
- **UI/UX**: Overhauled navigation, state management, and live document previews.

### Fixed
- Fixed critical `UndefinedColumnError` across multiple modules by unifying ORM and DB schemas.
- Eliminated `AttributeError` in Application status transitions.
- Resolved "Blank Preview" bug in the Resume Builder.
- Fixed rate-limit crashes by implementing automatic exponential backoff and jitter.

### Security
- **Data Protection**: Zero-trust PII redactor automatically masks sensitive data before cloud transmission.
- **API Guardrails**: Implemented 5MB request size limiting and hardened production CORS policies.
- **Error Handling**: Implemented a global structured exception framework to prevent data leaks via 500 errors.

### Performance
- Optimized dashboard aggregation queries, reducing load time by ~60%.
- Parallelized the Job Discovery pipeline, cutting scraping-to-display latency significantly.
