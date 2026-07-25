# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of JobHunterAI seriously. If you find a vulnerability, please do not disclose it publicly.

1. **Email us**: Send a detailed report to `security@jobhunterai.org`.
2. **Encrypted comms**: If necessary, we can provide a PGP key.
3. **Response**: You will receive an acknowledgment within 24 hours and a resolution plan within 72 hours.

## Security Practices
- All dependencies are monitored via **Dependabot**.
- PII is redacted locally before being sent to third-party AI providers.
- We do not store or transmit any raw API keys except via environment variables.
