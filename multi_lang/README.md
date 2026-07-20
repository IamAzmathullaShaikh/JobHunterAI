# Multi-Language JobHunterAI

This directory contains the polyglot microservice implementation of JobHunterAI.
Each module runs independently and communicates via REST or CLI.

## Modules
- **Scraper**: Go (REST API)
- **Normalizer**: TypeScript (Express REST API)
- **Deduplicator**: Rust (CLI logic)
- **Storage**: Java (JDBC logic)
- **Matcher**: Python (REST API - Optional AI integration via Groq/OpenRouter)
- **Exporter**: C# (CLI logic)
- **Orchestrator**: Node.js/JavaScript (Coordinates cross-language modules)

## AI Usage
AI models are exclusively used in the Python Matcher module and only execute if an API key is provided, falling back to local heuristic matching by default.
