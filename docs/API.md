# API Documentation

The JobHunterAI Backend provides a RESTful API for interacting with the core engines.

## 1. Authentication
Currently, the system is designed for single-user local-first use and does not require authentication headers for local development. For production deployments, we recommend placing the API behind a VPN or adding an API Gateway with OAuth2.

## 2. Core Endpoints

### Resumes
- `POST /api/resumes/parse`: Upload a resume file to generate a JSON profile.
- `GET /api/resumes/templates`: List available ATS templates.
- `POST /api/resumes/tailor`: Tailor a resume for a specific job ID.

### Jobs
- `GET /api/jobs`: List discovered jobs.
- `POST /api/jobs/scrape`: Trigger a scraper run.
- `POST /api/jobs/track`: Move a job into the CRM pipeline.

### Intelligence
- `POST /api/ats/analyze`: Perform a deep match analysis between a resume and a job.
- `POST /api/cover-letter/generate`: Generate a cover letter.
- `POST /api/interview/questions`: Generate mock interview questions based on a job.

### System
- `GET /api/health`: Check system status and AI provider availability.
- `GET /api/system/telemetry`: Retrieve performance metrics and circuit breaker states.

## 3. Error Handling
The API returns standard HTTP status codes:
- `200 OK`: Success.
- `400 Bad Request`: Validation error or missing parameters.
- `413 Payload Too Large`: Request body exceeds 5MB.
- `429 Too Many Requests`: AI provider rate limit reached.
- `500 Internal Server Error`: Critical system failure.
