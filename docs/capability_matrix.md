# JobHunterAI Capability Matrix v1.0.0

| Module | Capability | Version | Status | Dependencies | Stability | Public Interfaces |
|--------|------------|---------|--------|--------------|-----------|-------------------|
| **AI** | Chat Completion | 1.0.0 | ✅ Active | Groq/Gemini | Production | `IAIProvider.generate` |
| **AI** | Streaming | 1.0.0 | ✅ Active | Groq/Gemini | Production | `IAIProvider.stream` |
| **AI** | Context Building | 1.0.0 | ✅ Active | Domain Models | Stable | `CareerContextBuilder` |
| **Scraper** | Google Jobs | 1.0.0 | ✅ Active | Apify | Stable | `IScraperProvider.search` |
| **Scraper** | LinkedIn Jobs | 1.0.0 | ✅ Active | Apify | Stable | `IScraperProvider.search` |
| **Resume** | Extraction | 1.0.0 | ✅ Active | IFileParser | Stable | `ExtractResumeTextUseCase` |
| **Resume** | Parsing | 1.0.0 | ✅ Active | IResumeParser | Stable | `ParseResumeUseCase` |
| **Matching** | Deterministic Match | 1.0.0 | ✅ Active | Domain Services | Production | `JobMatchingService` |
| **Matching** | Batch Match | 1.0.0 | ✅ Active | Repositories | Stable | `BatchMatchJobsUseCase` |
| **Workflow** | State Machine | 1.0.0 | ✅ Active | Domain Events | Production | `Application.update_status` |
| **Analytics** | KPI Aggregation | 1.0.0 | ✅ Active | Workflow History | Stable | `DashboardService` |
| **Analytics** | Rec Engine | 1.0.0 | ✅ Active | Metrics Registry | Stable | `RecommendationEngineService` |
| **Platform** | Circuit Breaker | 1.0.0 | ✅ Active | Telemetry | Production | `CircuitBreakerProxy` |
| **Platform** | Telemetry | 1.0.0 | ✅ Active | Dispatcher | Production | `TelemetryEngine` |
| **Platform** | DI Container | 1.0.0 | ✅ Active | Lifecycle | Production | `DIContainer` |
