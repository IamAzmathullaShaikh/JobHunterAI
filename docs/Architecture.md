# System Architecture

JobHunterAI is built on a clean, layered architecture inspired by Domain-Driven Design (DDD) and Onion Architecture. This ensures that the core business logic is decoupled from external frameworks and AI providers.

## 1. High-Level Layers

### Client Layer (Frontend)
- Built with **React** and **TypeScript**.
- Communicates with the backend via RESTful APIs.
- State management handled by React hooks and context for local-first responsiveness.

### API Gateway (Backend)
- **FastAPI** provides the routing and request handling.
- Includes middleware for:
    - **Request Policer**: Enforces size limits and quotas.
    - **PII Redactor**: Automatically masks sensitive data (Names, Emails, Phone Numbers) using local Regex/NLP before data leaves the system.

### Intelligence Core (Domain & Application)
- **3-Tier Smart Router**: The brain of the system. It evaluates requests and routes them through:
    1. **Tier 1 (Performance)**: Groq (Llama 3.3).
    2. **Tier 2 (Logic)**: Google Gemini (1.5 Flash).
    3. **Tier 3 (Local)**: Sentence-Transformers / Ollama for zero-cost, offline fallback.

### Data Layer (Infrastructure)
- **SQLite** for lightweight local storage.
- **SQLAlchemy (Async)** for ORM and database management.
- **Local Response Cache**: In-memory and disk caching for repeating AI requests to save tokens and latency.

## 2. Request Flow

1. User uploads a resume via the React UI.
2. The UI sends a POST request to the `/api/resumes/parse` endpoint.
3. The **PII Redactor** middleware masks personal info.
4. The **Smart Router** selects the optimal AI model.
5. The model processes the resume and returns a structured JSON profile.
6. The data is persisted in the local DB and returned to the user.

## 3. Resilience Patterns
- **Circuit Breakers**: If an AI provider (e.g., Groq) returns consistent 5xx errors, the system automatically trips the breaker and routes traffic to Gemini or Local.
- **Exponential Backoff**: Integrated into all external API calls.
- **Fallback Strategies**: Defined per-capability (e.g., matching has a deterministic local fallback).
