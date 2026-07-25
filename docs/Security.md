# Security Policy

JobHunterAI is designed with a "Local First, Privacy Always" philosophy.

## 1. Zero-Trust Data Handling
- **Local PII Redaction**: Before any data is sent to a cloud AI provider (Groq, OpenAI, etc.), it passes through an on-device redaction layer. This layer identifies and masks:
    - Personal names
    - Email addresses
    - Phone numbers
    - Physical addresses
- **PII Recovery**: The system maintains a local mapping to de-mask the data once it returns from the AI, ensuring the user sees their own info while the cloud provider never does.

## 2. Infrastructure Security
- **FastAPI Security**: The backend uses standard security headers and prevents common attacks like SQL Injection (via SQLAlchemy ORM) and XSS (via Pydantic validation).
- **CORS Policy**: In `production` mode, CORS is restricted to specific domains.
- **Request Limiting**: A built-in middleware limits request sizes to 5MB to prevent Denial of Service (DoS) attacks via massive file uploads.

## 3. Secret Management
- We strictly follow the rule of never hardcoding API keys.
- All secrets are managed via `.env` files or environment variables.
- `.gitignore` is configured to prevent accidental commits of sensitive files.

## 4. Vulnerability Reporting
If you discover a security vulnerability, please send an email to `security@jobhunterai.org` or open a confidential issue. We aim to respond to all security concerns within 48 hours.
