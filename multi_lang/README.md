# JobHunterAI - Local-First Multi-Language Architecture

JobHunterAI has been rewritten to prioritize local execution, modularity, and deterministic rule-based logic across multiple programming languages. 

## Local-First Design Philosophy
Core features like resume parsing, job deduplication, and matching no longer rely on external AI/LLM APIs. By using local regex, keyword dictionaries, and HashSets, the system is faster, privacy-preserving, and offline-capable.

## Modules & Responsibilities
- **Scraper (Go):** Fast concurrent local scraping of job boards (REST API on `:8081`).
- **Normalizer (TS):** Cleans and standardized scraped data (REST API on `:8082`).
- **Deduplicator (Rust):** High-speed unique filtering using `HashSet` (CLI).
- **Parser (Python):** Local regex & keyword-based resume extraction (REST API on `:8084`).
- **Matcher (Python):** Deterministic Jaccard-style keyword overlap scoring (REST API on `:8085`).
- **Storage (Java):** JDBC/Flat-file persistence (CLI).
- **Exporter (C#):** Excel/CSV report generation (CLI).
- **UI (HTML/JS):** Lightweight vanilla dashboard.
- **Orchestrator (Node.js):** Coordinates cross-language flow using HTTP and sub-processes.

## Optional AI Integration
AI models (OpenRouter/Groq) are strictly isolated in `multi_lang/matcher/ai_matcher.py`. 
To enable nuanced semantic scoring, run the AI Matcher (REST API on `:8086`) and provide an `OPENROUTER_API_KEY`. If omitted, the system gracefully falls back to the deterministic local Matcher.

## GitHub Workflow & Interconnection
The repository maintains clean branch isolation for each feature module (`feature/go-scraper`, `feature/local-matcher`, etc.), merged sequentially into `main` with professional imperative commit messages. The Node.js orchestrator bridges these languages using standard `fetch` calls and `child_process.execSync` for CLI tools.
