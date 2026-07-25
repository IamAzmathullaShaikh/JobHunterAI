# Architecture Decision Records (ADR)

This folder contains records of significant architectural decisions made during the development of JobHunterAI.

## ADR 001: Local-First Strategy
- **Status**: Accepted
- **Context**: Users are sensitive about sharing their professional history and resumes.
- **Decision**: All primary data storage (SQLite) and initial processing will be local. Cloud AI is used only for intelligence, with local PII redaction.
- **Consequence**: High privacy, but users are responsible for their own backups.

## ADR 002: FastAPI over Django/Flask
- **Status**: Accepted
- **Context**: Need for high-performance, asynchronous API to handle streaming AI responses.
- **Decision**: Use FastAPI.
- **Consequence**: Native support for Pydantic and async/await, perfect for modern AI integrations.

## ADR 003: 3-Tier AI Routing
- **Status**: Accepted
- **Context**: Cloud AI can be expensive or suffer from outages.
- **Decision**: Implement a fallback router (Groq -> Gemini -> Local).
- **Consequence**: 100% availability and optimized costs.

## ADR 004: React with Vite
- **Status**: Accepted
- **Context**: Need for a fast development experience and small production bundles.
- **Decision**: Use Vite instead of Create React App.
- **Consequence**: Near-instant hot module replacement (HMR).
