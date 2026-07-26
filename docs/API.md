# API Documentation

The JobHunterAI Backend provides a RESTful API for interacting with the core engines.

## 1. Authentication
Currently, the system is designed for single-user local-first use and does not require authentication headers for local development. For production deployments, we recommend placing the API behind a VPN or adding an API Gateway with OAuth2.

## 2. Core Endpoints

### Resumes (`/api/resumes`)
- `GET /`: List all resumes.
- `POST /`: Create a new resume.
- `GET /profile`: Get the master profile.
- `PUT /profile`: Update the master profile.
- `GET /{id}`: Get resume details.
- `PUT /{id}`: Update resume content/template.
- `POST /{id}/duplicate`: Duplicate an existing resume.
- `POST /tailor`: Optimize resume bullets for a job description.
- `POST /export`: Export a resume (PDF, DOCX, Markdown, HTML).
- `GET /download/{filename}`: Retrieve an exported file.

### Jobs (`/api/jobs`)
- `GET /`: List discovered jobs with advanced filtering.
- `POST /scrape`: Trigger a multi-provider scraper run.
- `POST /track`: Move a job listing into the CRM pipeline.
- `POST /analyze`: Perform a deep ATS match analysis.
- `GET /saved-searches`: CRUD for search configurations.

### Cover Letter (`/api/cover-letter`)
- `GET /`: List all cover letters.
- `POST /generate`: Generate a structured draft grounded in a resume.
- `POST /regenerate-section`: AI-optimized paragraph refinement.
- `POST /export`: Export a letter (PDF, HTML, Markdown).

### Interview Prep (`/api/interview`)
- `GET /sessions`: List prep sessions.
- `POST /sessions`: Launch a new stateful mock interview.
- `POST /questions/{id}/answer`: Submit an answer for AI evaluation.
- `POST /sessions/{id}/finalize`: Calculate overall session scores.
- `POST /sessions/{id}/export`: Export session summary.

### Recruiters (`/api/recruiters`)
- `POST /find`: Discover and rank recruiter leads for a company.
- `GET /contacts`: List contacts saved in the CRM.
- `POST /contacts`: Save a discovered lead to the CRM.
- `POST /generate-outreach`: Create styled LinkedIn/Email drafts.
- `GET /export`: Export CRM data to CSV/Excel.

### System
- `GET /api/health`: Check database and AI provider status.
- `GET /api/system/telemetry`: Performance and circuit breaker metrics.

## 3. Error Handling
The API uses a global error handling framework:
- `200 OK`: Success.
- `400 Bad Request`: Validation failure.
- `404 Not Found`: Resource not found.
- `413 Payload Too Large`: Request body exceeds 5MB.
- `429 Too Many Requests`: Cloud AI rate limit reached (triggers local fallback).
- `500 Internal Server Error`: Structured error with diagnostics.
