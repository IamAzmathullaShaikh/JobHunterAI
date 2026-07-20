# JobHunterAI 🕵️‍♂️💼

Welcome to **JobHunterAI**, a fully modular, multi-language system designed for intelligent resume parsing, automated job matching, and comprehensive job tracking. 

## Project Intention

JobHunterAI was built with a strict **local-first, AI-optional** design philosophy. The core system relies entirely on deterministic, rule-based logic—such as regular expressions, keyword dictionaries, and fuzzy matching—to handle the bulk of its operations. 

We believe that core functionality shouldn't be gated behind third-party AI APIs or rate limits. External AI models (like OpenRouter, Groq, or Gemini) are treated strictly as **optional enhancements** for nuanced tasks like semantic equivalence scoring. If API keys are missing or rate limits are hit, the system seamlessly falls back to reliable local heuristics.

---

## Architecture & Modules

The project is structured as a polyglot microservice architecture. Each task is isolated into a tiny, independent module, allowing for seamless substitution or extension without breaking the pipeline.

- **Scraper (Go):** High-speed, concurrent scraping of job boards returning structured JSON.
- **Normalizer (TypeScript/Node.js):** Cleans and standardizes raw scraped data into a unified schema.
- **Deduplicator (Rust):** Memory-safe, high-performance unique filtering using HashSets (CLI).
- **Parser (Python):** Local regex and keyword-based resume extraction (REST API).
- **Matcher (Python):** Deterministic Jaccard-style keyword overlap scoring (REST API). 
- **Storage (Java):** JDBC/Flat-file persistence layer.
- **Exporter (C#):** Fast Excel/CSV report generation.
- **UI (Vanilla HTML/JS):** Lightweight frontend dashboard.
- **Orchestrator (Node.js):** Coordinates cross-language flow using HTTP and sub-processes.

---

## Installation & Requirements

To run the full polyglot pipeline, you will need the corresponding runtimes installed:

### Prerequisites
- **Python 3.10+** (For Parser & Matcher)
- **Node.js 18+** (For Orchestrator & Normalizer)
- **Go 1.20+** (For Scraper)
- **Rust (Cargo)** (For Deduplicator)
- **Java 17+ (JDK)** (For Storage)
- **.NET SDK 7.0+ / Mono** (For C# Exporter)

### Dependencies
- **Python:** Standard libraries only for local parsing. (Optional AI module may require `requests`).
- **Node.js:** `express`, `child_process`.
- **UI:** No external framework required.

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/IamAzmathullaShaikh/JobHunterAI.git
   cd JobHunterAI/multi_lang
   ```

2. **Python Services (Parser/Matcher):**
   ```bash
   python multi_lang/parser/parser.py &
   python multi_lang/matcher/local_matcher.py &
   ```

3. **Node.js Normalizer:**
   ```bash
   npm install express
   node multi_lang/normalizer/normalizer.ts &
   ```

4. **Go Scraper:**
   ```bash
   cd multi_lang/scraper
   go run scraper.go &
   ```

---

## Instructions & Usage

### Running the Orchestrator

The system can be fully automated using the Node.js orchestrator script, which chains the local modules together:

```bash
cd multi_lang/orchestrator
node orchestrator.js
```

### Manual Module Usage Examples

**1. Parse a Resume Locally (Python)**
```bash
curl -X POST http://localhost:8084/parse \
  -H "Content-Type: text/plain" \
  -d "I am a Software Engineer with 5 years of experience in Python and React."
```

**2. Scrape Jobs (Go)**
```bash
curl http://localhost:8081/scrape
```

**3. Deduplicate (Rust)**
```bash
rustc multi_lang/deduplicator/deduplicator.rs -o dedup
./dedup "dataset_string"
```

**4. Export to CSV (C#)**
```bash
csc multi_lang/exporter/Exporter.cs
./Exporter.exe
```

### Enabling Optional AI Features

If you want to use the nuanced semantic AI matcher instead of the local heuristic matcher:

1. Obtain an API key from OpenRouter, Groq, or Gemini.
2. Set the environment variable: `export OPENROUTER_API_KEY=your_key`
3. Run the AI Matcher service:
   ```bash
   python multi_lang/matcher/ai_matcher.py &
   ```

---

## Commit & GitHub Workflow

We maintain a clean, readable git history. All commits must follow professional conventions.

### Branch Naming
- `feature/module-name` (e.g., `feature/go-scraper`)
- `fix/bug-description` (e.g., `fix/local-fallback`)
- `docs/readme-update`

### Commit Message Format
Every commit must contain:
1. **A short imperative summary** (Max 50 characters).
2. **A detailed description** explaining *What*, *Why*, and the *Impact*.

**Example Commit Message Template:**
```text
feat(parser): add local rule-based resume parser

Implemented a Python REST service for parsing resumes locally.
Utilizes regex and keyword dictionaries instead of AI.
Ensures fast, deterministic extraction of skills and experience without rate limits.
```

---

## Contribution Guidelines

We welcome contributions! To ensure system stability and modularity, please follow these rules:

1. **Keep it Local-First:** New core features must not depend on paid or rate-limited APIs. Always provide a deterministic fallback.
2. **Microservice Isolation:** If you add a new module (e.g., an Interview Prep module), make it a standalone service with a clear I/O interface.
3. **Multi-Language Parity:** Feel free to implement a module in a new language (e.g., a Ruby Scraper or a C++ Deduplicator).
4. **Detailed Commits:** Squashed PRs must use the detailed commit message template outlined above.

---

## Credits

- **Maintainer:** IamAzmathullaShaikh
- Built using open-source, local-first logic patterns.
- Optional AI capabilities powered by OpenRouter / Groq / Gemini.

---

## License

This project is licensed under the **MIT License**.
