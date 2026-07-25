# Frequently Asked Questions (FAQ)

### Is JobHunterAI free to use?
Yes! The core software is open-source under the MIT license. You only pay for the AI tokens you use from providers like Groq or Gemini (many have free tiers).

### Does my data stay private?
Absolutely. JobHunterAI is local-first. Your resume, job listings, and tracking data are stored on your machine in a SQLite database. We also provide built-in PII redaction for cloud AI requests.

### Can I use it for multiple people?
The current version is optimized for a single user. To support multiple users, you can deploy separate instances.

### Which AI provider is the best?
- **Groq** is best for speed and "Resume Tailoring".
- **Gemini** is best for complex "Interview Prep" and large document analysis.
- **Ollama** is best for 100% private, zero-cost usage.

### How do I add a new job site to the scraper?
You can contribute by adding a new scraper class to `core/scrapers/`. See `LinkedInScraper` as a reference.
