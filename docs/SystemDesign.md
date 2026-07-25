# System Design

JobHunterAI is designed with modularity and extensibility as core principles.

## 1. Domain Model
The core domain is centered around the `CandidateProfile` and the `JobListing`.

- **CandidateProfile**: A structured representation of a user's resume, including skills, experience, education, and professional summary.
- **JobListing**: A standardized entity for roles found across different platforms.
- **Application**: Tracks the state of a job within the CRM pipeline (Interested, Applied, Interviewing, Offer, Rejected).

## 2. Intelligence Engines

### Resume Engine
- **Parser**: Converts PDF/DOCX to text and then into a `CandidateProfile` using AI.
- **Tailor**: Takes a `CandidateProfile` and a `JobListing` to suggest specific bullet point modifications.
- **Writer**: Generates professional summaries and cover letters based on the match.

### Matching Engine
- Uses a weighted scoring algorithm to compare `CandidateProfile` against `JobListing`.
- **Factors**: Skill match (35%), Experience relevance (25%), Keyword density (15%), Education (10%), Location (10%), Salary (5%).
- Provides a "Match Score" and a "Skill Gap Analysis".

### Scraper Fleet
- Orchestrates multiple scrapers (LinkedIn, Indeed, etc.).
- Uses **Apify** as a primary provider and custom Selenium/Playwright scripts as fallbacks.
- Deduplicates jobs using a title + company + location fingerprinting algorithm.

## 3. Data Integrity
- **Migrations**: Handled via **Alembic**.
- **Validation**: Strict schema validation using **Pydantic** on all API boundaries.
- **Audit Logs**: Telemetry system tracks AI performance, latencies, and success rates.
