# Release Notes: v1.0.0 "The Genesis Release"

We are proud to announce the first production-certified release of JobHunterAI. This version transforms the project from an experimental tool into a robust, enterprise-ready career automation platform.

## Highlights
- **Universal Job Discovery**: Support for 9+ major platforms out of the box.
- **Deterministic Matching**: A scientifically weighted scoring algorithm for role alignment.
- **Privacy-First Intelligence**: Local redaction ensures your sensitive data never hits the cloud raw.
- **Modular Core**: Easily swap AI providers or add new scrapers with our clean provider interface.

## Major Milestones
- **M6.10 Reached**: All engineering objectives for the v1.0 baseline have been met and verified.
- **100% Backend Coverage**: Core matching and intelligence logic is fully tested.
- **UI Refresh**: A complete overhaul of the dashboard for better usability and accessibility.

## Known Limitations
- Multi-user support is not yet implemented.
- Voice-to-text features are scheduled for v1.1.0.

## Migration Notes
If you were using an experimental v0.x branch:
1. Back up your `jobhunter.db`.
2. Run `alembic upgrade head` to apply new schema changes for the CRM.
3. Update your `.env` to include the new `AI_PROVIDER` flag.
