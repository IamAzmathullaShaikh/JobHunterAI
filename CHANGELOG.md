# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-25

### Added
- **Smart AI Router**: 3-tier fallback logic (Groq -> Gemini -> Local).
- **Resume Intelligence**: Automated parsing and tailoring engine.
- **Job Scraper Fleet**: Multi-platform job discovery (LinkedIn, Indeed, etc.).
- **Application CRM**: Kanban-style job tracking system.
- **Privacy Layer**: Local PII redaction for cloud AI requests.
- **Analytics Dashboard**: Conversion and velocity tracking.
- **Enterprise UI**: Modern React-based dashboard with Tailwind CSS.

### Changed
- Refactored core logic into clean, domain-driven modules.
- Modernized documentation and project structure.

### Fixed
- Improved scraper resilience against layout changes.
- Fixed token overflow issues on large resumes.

### Security
- Implemented zero-trust data masking.
- Restricted CORS policies for production.
