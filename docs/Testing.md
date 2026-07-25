# Testing Strategy

JobHunterAI maintains high code quality through a comprehensive testing suite.

## 1. Backend Testing (Pytest)

### Unit Tests
Located in `tests/unit/`. These test individual components like the matching algorithm and PII redactor in isolation.
`pytest tests/unit`

### Integration Tests
Located in `tests/integration/`. These test the interaction between the FastAPI app, the database, and the AI router fallbacks.
`pytest tests/integration`

### Mocking
We use `unittest.mock` to simulate AI provider responses and scraper outputs to ensure tests are fast, deterministic, and cost-free.

## 2. Frontend Testing (Vitest)

### Component Tests
Located in `tests/components/`. We use **Vitest** and **React Testing Library** to verify UI component behavior.
`npm run test:ui`

### Smoke Tests
A basic set of tests to ensure the main dashboard renders and navigation works.

## 3. End-to-End (E2E) Testing
For E2E flows (e.g., Upload Resume -> Analyze -> Generate Cover Letter), we use a custom script located at `scripts/run_smoke_trace.sh`.

## 4. Continuous Integration
All tests are automatically run on every Pull Request via **GitHub Actions**.
- **Lint**: Ensures code follows PEP 8 and ESLint rules.
- **Test**: Runs the full suite of backend and frontend tests.
- **Build**: Verifies the project compiles and the Docker image builds correctly.
