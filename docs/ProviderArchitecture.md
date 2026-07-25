# Provider Architecture

JobHunterAI uses a "Provider Pattern" to ensure it can easily support new AI services and scrapers.

## 1. AI Provider Interface
Located in `domain/providers/ai.py`. All AI providers must implement:
- `generate_text(prompt: str) -> str`
- `generate_json(prompt: str, schema: dict) -> dict`
- `get_token_usage() -> int`

Current Implementations:
- `GroqAIProvider`: Ultra-fast inference.
- `GeminiAIProvider`: Large context and reasoning.
- `OpenAIProvider`: Industry standard.
- `OllamaProvider`: Local inference.

## 2. Scraper Provider Interface
Located in `domain/providers/scraper.py`.
- `search_jobs(query: str, location: str) -> List[JobListing]`
- `get_job_details(job_id: str) -> JobListing`

Current Implementations:
- `ApifyScraper`: Cloud-based robust scraping.
- `LocalBridge`: Integrates with locally running Puppeteer/Selenium scripts.

## 3. Telemetry Provider
Tracks the health and performance of all providers.
- Records success/failure.
- Measures time-to-first-token.
- Manages the circuit breaker state.
