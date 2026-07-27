# System Architecture

JobHunterAI is built on a clean, layered architecture inspired by Domain-Driven Design (DDD) and Onion Architecture. This ensures that the core business logic is decoupled from external frameworks and AI providers.

## 1. High-Level Layers

### Client Layer (Frontend)
- Built with **React** and **TypeScript**.
- Communicates with the backend via RESTful APIs.
- Features specialized engines for:
    - **Resume Builder V2**: Multi-document management with live A4 preview.
    - **Cover Letter Builder**: Grounded draft generation with section-based editing.
    - **Interview Studio**: Stateful mock interview coaching with real-time feedback.
    - **Recruiter CRM**: Discovery and tracking of hiring decision-makers.

### API Gateway (Backend)
- **FastAPI** provides the routing and request handling.
- Includes middleware for:
    - **Request Policer**: Enforces size limits (5MB max) and quotas.
    - **PII Redactor**: Automatically masks sensitive data (Names, Emails, Phone Numbers) before cloud processing.

### Intelligence Core (Domain & Application)
- **3-Tier Smart Router**: Dynamically routes AI tasks based on capability:
    1. **Tier 1 (Reasoning)**: Groq (Llama 3.3).
    2. **Tier 2 (Logic)**: Google Gemini (1.5 Flash).
    3. **Tier 3 (Local)**: Sentence-Transformers / Ollama for zero-cost, offline fallback.

### Data Layer (Infrastructure)
- **PostgreSQL / SQLite** support for persistent document storage.
- **SQLAlchemy (Async)** for robust ORM management.
- **LLM Cache**: Optimized persistence to save latency and token costs.

## 2. Request Flow

1. User interacts with a specific tool (e.g., Interview Prep).
2. The UI sends a POST request to the relevant API endpoint.
3. The **PII Redactor** middleware masks personal info if configured.
4. The **Task Engine** orchestrates the business logic and calls the **Smart Router**.
5. The selected AI model processes the context and returns structured data.
6. The state is persisted in the DB and synced to the UI.

## 4. Future Scalability (v2.0+)

To support thousands of concurrent users, the architecture will transition to an **Event-Driven Microservices** model:

- **Distributed Workers**: Scrapers and complex AI reasoning will be moved to **Celery** workers. This prevents long-running HTTP requests from blocking the API.
- **Message Broker**: **Redis** or **RabbitMQ** will be introduced to handle task queuing and inter-service communication.
- **Stateless API**: The FastAPI service will become completely stateless, with session management handled via JWT and distributed caching.
- **Relational Scaling**: The Data Layer will migrate to **PostgreSQL** with Read Replicas and a dedicated caching layer for resume metadata.
