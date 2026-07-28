# Graph Report - .  (2026-07-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1467 nodes · 3030 edges · 136 communities (107 shown, 29 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 251 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e680d3d8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- JobListingCreate
- ProviderRegistry
- ApplicationStatus
- JobService
- recruiters.py
- LLMClient
- CircuitBreaker
- exceptions.py
- ProviderLifecycle
- dependencies.py
- models.py
- compilerOptions
- TelemetryEngine
- enricher.py
- providers/manager.py
- CircuitBreakerProxy
- test_rc7_verification.py
- interview.py
- matcher.py
- ApifyProvider
- TemplateEngine
- AnalyticsEngine
- dependencies
- AppLifecycleManager
- ResumeService
- devDependencies
- GroqAIProvider
- ProviderManager
- JobRepository
- profile.py
- AICache
- ScrapeRequest
- App.tsx
- types.ts
- FaultyAIProvider
- test_circuit_breaker.py
- ApifyClient
- api/jobs.py
- GroqMapper
- ApplicationRepository
- GroqClient
- JobRepository
- JobListing
- JobListing
- apify_provider.py
- BaseTelemetrySubscriber
- ResumeBuilder.tsx
- job_service.py
- AIAnalysisRepository
- groq_provider.py
- ProviderMetrics
- CandidateProfile
- Settings
- .__init__
- ProviderRequest
- ApifyActorRegistry
- apify_models.py
- scripts
- scripts
- env.py
- .discover_new_listings
- SystemValidationSuite
- main.py
- logging_config.py
- settings.py
- DeduplicationEngine
- route
- .evaluate_answer
- ErrorBoundary
- run.py
- test_scraper_normalizer.cjs
- global_exception_handler
- get_llm_client
- HealthStatus
- .normalize
- ValidProvider
- limit_request_size
- .generate
- ApifyRegistryClient
- ApifyHealthChecker
- AnalysisMatrix.tsx
- PartialProvider
- test_router
- 8a286fd41f58_v1_schema_recovery.py
- .health
- frontend/package.json
- telemetry
- stealth_async
- .search_live
- extract_text_from_file
- runScraper.test.ts
- .embed
- .shutdown
- jsdom
- tailwindcss
- @tailwindcss/line-clamp
- @tailwindcss/vite
- tsx
- @types/cors
- @types/node
- @types/react
- @vitejs/plugin-react
- scraperBridge.test.ts
- run_frontend_tests.sh
- run_smoke_trace.sh
- start_frontend_demo.sh
- verify_job_link.sh

## God Nodes (most connected - your core abstractions)
1. `JobService` - 74 edges
2. `ApplicationStatus` - 43 edges
3. `ProviderManager` - 38 edges
4. `ProviderRegistry` - 38 edges
5. `JobListingCreate` - 36 edges
6. `ProviderMetadata` - 34 edges
7. `ProviderLifecycle` - 30 edges
8. `ApifyProvider` - 29 edges
9. `GroqAIProvider` - 27 edges
10. `get_llm_client()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `FaultyAIProvider` --uses--> `AIProviderError`  [INFERRED]
  tests/integration/test_system_validation.py → core/exceptions.py
- `SystemValidationSuite` --uses--> `AIProviderError`  [INFERRED]
  tests/integration/test_system_validation.py → core/exceptions.py
- `InvalidProvider` --uses--> `ProviderRegistrationError`  [INFERRED]
  tests/unit/test_registry.py → core/exceptions.py
- `PartialProvider` --uses--> `ProviderRegistrationError`  [INFERRED]
  tests/unit/test_registry.py → core/exceptions.py
- `ValidProvider` --uses--> `ProviderRegistrationError`  [INFERRED]
  tests/unit/test_registry.py → core/exceptions.py

## Import Cycles
- None detected.

## Communities (136 total, 29 thin omitted)

### Community 0 - "JobListingCreate"
Cohesion: 0.05
Nodes (38): DatasetMapper, Normalizes inconsistent raw JSON items from various Apify actors into     the s, JobListingBase, JobListingCreate, BaseModel, Any, 9-Platform Multi-Scraper Engine.     Platforms: LinkedIn, Indeed, Glassdoor, Zi, ScraperEngine (+30 more)

### Community 1 - "ProviderRegistry"
Cohesion: 0.08
Nodes (23): ProviderRegistrationError, Raised when a provider fails the registration validation pipeline., ProviderLoader, Handles discovery and registration of providers into the registry.     Decouple, Discovers and registers every known provider., ProviderMetadata, Static metadata about a specific provider., ProviderRegistry (+15 more)

### Community 2 - "ApplicationStatus"
Cohesion: 0.15
Nodes (35): create_cover_letter(), duplicate_cover_letter(), export_cover_letter(), generate_cover_letter(), get_cover_letter(), list_cover_letters(), get, post (+27 more)

### Community 3 - "JobService"
Cohesion: 0.14
Nodes (35): delete_cover_letter(), delete, archive_resume(), Config, create_resume(), delete_resume(), download_resume(), duplicate_resume() (+27 more)

### Community 4 - "recruiters.py"
Cohesion: 0.10
Nodes (26): generate_outreach(), post, add_to_crm(), delete_contact(), export_crm(), find_recruiters(), generate_outreach(), list_contacts() (+18 more)

### Community 5 - "LLMClient"
Cohesion: 0.12
Nodes (10): GeminiLLMClient, GroqLLMClient, LLMClient, OllamaLLMClient, OpenRouterLLMClient, ABC, Any, Orchestrates multiple LLM providers with automatic fallback.     Utilizes 3-tie (+2 more)

### Community 6 - "CircuitBreaker"
Cohesion: 0.12
Nodes (17): CircuitState, ProviderBreakerState, BaseModel, Enum, str, Runtime state tracking for a single provider's circuit., Returns the state to healthy defaults., The three possible states of a circuit breaker. (+9 more)

### Community 7 - "exceptions.py"
Cohesion: 0.10
Nodes (27): AIProviderError, DatabaseError, DuplicateInstanceError, JobHunterException, ProviderInitializationError, ProviderNotFoundError, ProviderNotReadyError, Exception (+19 more)

### Community 8 - "ProviderLifecycle"
Cohesion: 0.10
Nodes (17): IAIProvider, Generates a vector embedding for the given input text.         Replaces local s, Predicts the USD cost for a generation request based on token estimates., Capability detection hook (e.g., 'vision', 'tool_calling', 'structured_output')., Abstract contract for AI (LLM) service providers.     Every implementation (Gro, ProviderCostEstimate, ProviderLifecycle, ABC (+9 more)

### Community 9 - "dependencies.py"
Cohesion: 0.09
Nodes (18): container, get_circuit_breaker(), get_container(), get_current_user_id(), get_provider_manager(), get_registry(), get_resume_engine(), Placeholder for future Auth integration.     Currently returns a static UUID fo (+10 more)

### Community 10 - "models.py"
Cohesion: 0.13
Nodes (24): Base, CompanySnapshot, CoverLetter, InterviewSession, MatchHistory, OutreachMessage, SQLAlchemy models for JobHunterAI – extended with all requested columns., Store the *exact* JSON payload each scraper returned – audit / replay. (+16 more)

### Community 11 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowImportingTsExtensions, allowSyntheticDefaultImports, esModuleInterop, isolatedModules, jsx, lib, module (+17 more)

### Community 12 - "TelemetryEngine"
Cohesion: 0.11
Nodes (16): get_telemetry_engine(), Enum, str, TelemetryEventType, ProviderStats, BaseModel, A point-in-time state of the entire platform telemetry., Aggregated operational metrics for a single provider. (+8 more)

### Community 13 - "enricher.py"
Cohesion: 0.14
Nodes (20): generate_cover_letter(), parse_resume(), Functional API returning source info and raw data., get_enricher(), cloud_find_decision_makers(), Enricher, find_decision_makers(), local_find_decision_makers() (+12 more)

### Community 14 - "providers/manager.py"
Cohesion: 0.22
Nodes (17): BaseTelemetryEvent, ProviderInitialized, ProviderInvocationCompleted, ProviderInvocationFailed, ProviderInvocationStarted, ProviderRegistered, ProviderReloaded, ProviderShutdown (+9 more)

### Community 15 - "CircuitBreakerProxy"
Cohesion: 0.11
Nodes (9): CircuitBreakerProxy, Any, Retrieves a provider instance, lazily initializing it if necessary.          A, Selects and returns the optimal provider based on metadata criteria., Intercepts calls to a provider instance to enforce circuit breaker state., Invalidates cache and re-initializes a provider., Gracefully shuts down all instantiated providers., Wraps the instance in proxy layers for Circuit Breaking and Telemetry. (+1 more)

### Community 16 - "test_rc7_verification.py"
Cohesion: 0.13
Nodes (14): ApifyActorSelector, Choose a single best actor., Returns top N actors suitable for the query, sorted by weighted priority., Chooses the best Apify actor for a given job search query., apify_scrape(), get_sample_jobs(), local_scrape(), Any (+6 more)

### Community 17 - "interview.py"
Cohesion: 0.15
Nodes (20): create_session(), delete_session(), export_session(), finalize_session(), get_session(), list_sessions(), delete, get (+12 more)

### Community 18 - "matcher.py"
Cohesion: 0.15
Nodes (17): cloud_analyze_fit(), cloud_optimize_bullet(), get_local_model(), JobMatcher, local_analyze_fit(), AIAnalysisCreate, Any, Backward-compatible class wrapper for tiered matching logic. (+9 more)

### Community 19 - "ApifyProvider"
Cohesion: 0.18
Nodes (12): ApifyConfig, BaseModel, Loads configuration from global application settings., Configuration for the Apify scraper provider., ApifyProvider, Canonical reference implementation for the Apify Scraper Provider., asyncio, run_all() (+4 more)

### Community 20 - "TemplateEngine"
Cohesion: 0.14
Nodes (12): Any, Export Engine for 10 Professional Resume Templates.     Supports pixel-perfect, Renders profile data into an HTML string based on a template., Renders cover letter content into a professional A4 HTML string., Renders an interview prep session into a professional HTML report., Renders cover letter into a clean Markdown document., Generates a PDF for a cover letter using playwright., Generates a PDF for an interview session using playwright. (+4 more)

### Community 21 - "AnalyticsEngine"
Cohesion: 0.16
Nodes (12): AnalyticsEngine, Any, AsyncSession, Collates recent events from all modules into a sorted timeline., Calculates job distribution metrics., Fetches historical ATS scores for trend analysis., Identifies top requested skills and current gaps., Unified Career Intelligence Engine.     Aggregates data from all modules to pro (+4 more)

### Community 22 - "dependencies"
Cohesion: 0.10
Nodes (21): cors, express, dependencies, cors, express, @google/genai, lodash, lucide-react (+13 more)

### Community 23 - "AppLifecycleManager"
Cohesion: 0.17
Nodes (14): DIContainer, Composition Root for the JobHunterAI platform.     Manages the lifecycle and re, Thread-safe singleton access to the container., AppLifecycleManager, Orchestrates the global startup and shutdown sequences for the platform.     En, Sequential startup of all platform infrastructure., Graceful cleanup of all resources., ApplicationReady (+6 more)

### Community 24 - "ResumeService"
Cohesion: 0.16
Nodes (14): get_ats_history(), match_ats(), optimize_bullet(), parse_pdf(), get, post, get_resume_service(), Any (+6 more)

### Community 25 - "devDependencies"
Cohesion: 0.12
Nodes (19): concurrently, esbuild, devDependencies, concurrently, esbuild, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+11 more)

### Community 26 - "GroqAIProvider"
Cohesion: 0.22
Nodes (14): GroqConfig, BaseModel, Loads configuration from global application settings., Configuration for the Groq LLM provider., GroqAIProvider, Estimated cost calculation for Groq requests., Canonical reference implementation for an AI Provider using Groq.     Orchestra, Placeholder for runtime metrics collection (M5.5). (+6 more)

### Community 27 - "ProviderManager"
Cohesion: 0.21
Nodes (11): ProviderManager, Runtime orchestrator responsible for instantiating, caching, and managing     t, Returns IDs of currently instantiated providers., MockAIProvider, asyncio, run_all(), test_cache_reuse(), test_initialization_failure_cleanup() (+3 more)

### Community 28 - "JobRepository"
Cohesion: 0.17
Nodes (11): JobRepository, AsyncSession, JobListingCreate, Persists a new scraped job listing to the database., Checks if a job has already been scraped using the unique site token., Fetches batch historical entries sorted by execution entry times., Applies parsed, normalized markdown text over noisy initial raw HTML strings., JobListingBase (+3 more)

### Community 29 - "profile.py"
Cohesion: 0.16
Nodes (13): get_profile(), parse_resume(), get, post, cloud_parse_resume(), local_parse_resume(), Any, Backward-compatible class wrapper for tiered parsing logic. (+5 more)

### Community 30 - "AICache"
Cohesion: 0.16
Nodes (10): AICache, Any, AsyncSession, Persistent cache for AI responses to minimize costs and latency., Retrieves a cached response if it exists., Caches a new response., LLMCache, Cache for the expensive Groq resume-parse call. (+2 more)

### Community 31 - "ScrapeRequest"
Cohesion: 0.13
Nodes (12): ApifyRequestMapper, Any, BaseModel, Handles translation between JobHunterAI internal models and Apify Actor inputs., Maps generic scrape request to actor-specific JSON schema., Internal model for job scraping requests., ScrapeRequest, Any (+4 more)

### Community 32 - "App.tsx"
Cohesion: 0.15
Nodes (7): EngineSource, Props, KanbanBoardProps, Props, ResumeDrawer(), ResumeWriter(), ApplicationStatus

### Community 33 - "types.ts"
Cohesion: 0.18
Nodes (10): ContactFinderProps, Props, RecruiterFinderProps, ContactFinderDTO, InterviewQuestion, InterviewSession, JobApplication, RecruiterContact (+2 more)

### Community 34 - "FaultyAIProvider"
Cohesion: 0.13
Nodes (5): CallRejectedError, CircuitBreakerError, Raised when a call is blocked because the circuit is currently OPEN., Base exception for circuit breaker related issues., FaultyAIProvider

### Community 35 - "test_circuit_breaker.py"
Cohesion: 0.21
Nodes (8): BreakerPolicy, BaseModel, Configuration policy for circuit breaker behavior., FailingProvider, asyncio, run_all(), test_circuit_breaker_flow(), test_half_open_to_closed()

### Community 36 - "ApifyClient"
Cohesion: 0.13
Nodes (9): ApifyClient, Any, Low-level wrapper for the Apify SDK.     Handles authentication, actor executio, Initializes the Apify SDK client., Cleans up the SDK resources., Verifies authentication with Apify., Starts an actor and waits for completion.         Returns the raw Run object., Retrieves all items from a completed dataset. (+1 more)

### Community 37 - "api/jobs.py"
Cohesion: 0.23
Nodes (14): analyze_job(), analyze_pending_jobs(), delete_saved_search(), get_jobs(), list_saved_searches(), delete, get, post (+6 more)

### Community 38 - "GroqMapper"
Cohesion: 0.15
Nodes (10): GroqMapper, Any, Handles translation between JobHunterAI internal models and Groq SDK objects., Maps internal request to Groq SDK dictionary., Maps Groq SDK response to internal ProviderResponse., Any, Provides real-time token streaming., Executes a structured JSON completion. (+2 more)

### Community 39 - "ApplicationRepository"
Cohesion: 0.27
Nodes (9): ApplicationRepository, AsyncSession, Pins a tracking context initialization onto an application pipeline route., Transitions application pipelines across state-machine boundaries dynamically., ApplicationStatusDTO, JobApplicationCreate, JobApplicationDTO, Enum (+1 more)

### Community 40 - "GroqClient"
Cohesion: 0.15
Nodes (8): GroqClient, Any, Low-level wrapper for the official Groq SDK.     Handles raw API communication,, Initializes the AsyncGroq client., Closes the underlying HTTP client., Lightweight check to verify authentication., Executes a single non-streaming chat completion., Executes a streaming chat completion.

### Community 41 - "JobRepository"
Cohesion: 0.23
Nodes (8): JobRepository, AsyncSession, JobListingCreate, Persists a new job listing DTO into the database layer., Saves new job listings while skipping items that already exist by job_id_raw., Retrieves a single listing by its raw external source ID., Fetches listings that do not have an associated AI analysis record yet., JobListingRead

### Community 42 - "JobListing"
Cohesion: 0.21
Nodes (6): JobDiscovery(), Props, JobsTableProps, ScraperFleetProps, JobListing, baseJob

### Community 43 - "JobListing"
Cohesion: 0.19
Nodes (8): AIAnalysis, JobListing, ExportService, AsyncSession, Queries database using SQLAlchemy 2.0 schema and builds a clean Pandas DataFrame, Generates a polished, minimal Excel spreadsheet bytes stream with openpyxl styli, Evaluates unanalyzed jobs against the user's profile using Groq LLM., DataFrame

### Community 44 - "apify_provider.py"
Cohesion: 0.23
Nodes (8): ActorMetadata, get_actor_metadata(), BaseModel, Retrieves metadata for a specific actor ID., Metadata about a specific Apify actor., Estimates the cost of a scrape based on the number of successfully harvested ite, Utility for projecting USD costs for scraping operations based on actor metadata, ScrapeCostCalculator

### Community 45 - "BaseTelemetrySubscriber"
Cohesion: 0.18
Nodes (8): Lightweight Pub/Sub hub for telemetry events.     Thread-safe distribution to m, Adds a new observer to the event stream., Broadcasts an event to all active subscribers., TelemetryDispatcher, BaseTelemetrySubscriber, ABC, Hook called by the Dispatcher whenever a new event is published., Interface for objects that wish to consume telemetry events.

### Community 46 - "ResumeBuilder.tsx"
Cohesion: 0.17
Nodes (7): DEFAULT_CONTENT, moveItem(), ResumeEditor(), EducationItem, ProjectItem, ResumeContent, WorkHistoryItem

### Community 47 - "job_service.py"
Cohesion: 0.23
Nodes (10): create_application(), delete_application(), get_analytics(), get_applications(), delete, get, post, Returns unified Career Intelligence data. (+2 more)

### Community 48 - "AIAnalysisRepository"
Cohesion: 0.24
Nodes (8): AIAnalysisRepository, AIAnalysisCreate, AsyncSession, Saves structured OpenAI output models mapped directly to an explicit target job, Retrieves structured scoring criteria reports for a specific job entry., AIAnalysisCreate, AIAnalysisDTO, BaseModel

### Community 49 - "groq_provider.py"
Cohesion: 0.23
Nodes (6): get_model_metadata(), ModelMetadata, BaseModel, Retrieves metadata for a specific model ID., Metadata about an LLM model available on Groq., Capability discovery based on model catalog.

### Community 50 - "ProviderMetrics"
Cohesion: 0.17
Nodes (7): ProviderMetrics, BaseModel, RateLimitStatus, Tracks operational performance metrics for a provider., Information about current provider quotas and throttling., Returns the current operational metrics for this provider., Returns the current throttle/quota state for this scraper.

### Community 51 - "CandidateProfile"
Cohesion: 0.20
Nodes (6): Props, ResumeBuilderProps, ResumeIngestionProps, CandidateProfile, CoverLetter, CoverLetterContent

### Community 52 - "Settings"
Cohesion: 0.20
Nodes (6): BaseSettings, Any, Centralized configuration management for JobHunterAI.     Loads settings from e, Settings, field_validator, model_validator

### Community 54 - "ProviderRequest"
Cohesion: 0.33
Nodes (8): ProviderRequest, ProviderResponse, ProviderStreamChunk, BaseModel, Standardized object for real-time token streaming., Internal model for AI generation requests., GroqUsageExtractor, Extracts and standardizes token usage and cost metrics from Groq responses.

### Community 56 - "apify_models.py"
Cohesion: 0.24
Nodes (9): ApifyRunMetadata, ApifyRunStatus, ApifyScrapeResult, BaseModel, Enum, str, Detailed metadata about a specific Apify actor run., Standardized container for scraper results and telemetry. (+1 more)

### Community 57 - "scripts"
Cohesion: 0.20
Nodes (10): scripts, build, dev, dev:all, dev:backend, dev:frontend, lint, preview (+2 more)

### Community 58 - "scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, backend, build, dev, lint, test (+1 more)

### Community 59 - "env.py"
Cohesion: 0.28
Nodes (8): Connection, do_run_migrations(), Run migrations in 'offline' mode., In-process async engine migration executor., Run migrations in 'online' mode using asyncio., run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 60 - ".discover_new_listings"
Cohesion: 0.22
Nodes (5): Maintenance routine:         1. Deletes duplicate job listings from the databas, Normalizes title/company strings for reliable duplicate detection., Returns sets of job_id_raw and (title_clean, company_clean) tuples for jobs, Scrapes jobs across all fleet engines, stripping out duplicates and applied jobs, JobListing

### Community 62 - "main.py"
Cohesion: 0.43
Nodes (5): lifespan(), get_db_session(), AsyncSession, Dependency provider hook for safe context-managed database pipelines., FastAPI

### Community 63 - "logging_config.py"
Cohesion: 0.29
Nodes (5): BaseHTTPMiddleware, configure_logging(), Request, RequestIDFilter, RequestIDMiddleware

### Community 65 - "DeduplicationEngine"
Cohesion: 0.32
Nodes (4): DeduplicationEngine, Heuristic-based duplicate detection., Filters out duplicates from a new batch against existing records., Identifies and merges duplicate job listings using multiple signals.

### Community 66 - "route"
Cohesion: 0.31
Nodes (8): Capability, _check_required_envs(), _is_api_key_set(), Any, Check if an API key is actually set (not None, not empty, not whitespace)., Validates required environment variables with AND/OR logic.     - list of strin, N-Tier Multi-Engine Router.     Sequentially attempts each tier function until, route()

### Community 67 - ".evaluate_answer"
Cohesion: 0.33
Nodes (4): Any, Analyzes response specifically for STAR method compliance., Generates 5 role-specific and resume-grounded interview questions., Provides detailed feedback and scoring for an interview answer.

### Community 68 - "ErrorBoundary"
Cohesion: 0.29
Nodes (3): ErrorBoundary, Props, State

### Community 69 - "run.py"
Cohesion: 0.71
Nodes (6): check_env(), deploy_server(), main(), print_styled(), run_local(), update_api_keys()

### Community 70 - "test_scraper_normalizer.cjs"
Cohesion: 0.29
Nodes (4): assert, portalId, res1, res2

### Community 71 - "global_exception_handler"
Cohesion: 0.47
Nodes (6): global_exception_handler(), jobhunter_exception_handler(), not_found_handler(), Exception, Request, exception_handler

### Community 72 - "get_llm_client"
Cohesion: 0.10
Nodes (18): cloud_generate_cover(), local_generate_cover(), Any, Generates a cover letter using cloud LLM., Generates a cover letter using a local Jinja2 template., get_llm_client(), Factory function for retrieving the configured LLM client., EnrichmentEngine (+10 more)

### Community 73 - "HealthStatus"
Cohesion: 0.33
Nodes (5): HealthStatus, Enum, str, Represents the operational state of a provider., Performs a detailed health check (e.g., ping or quota check).

### Community 74 - ".normalize"
Cohesion: 0.33
Nodes (4): Any, JobListingCreate, Executes a job search across supported boards.         Returns raw provider-spe, Maps raw provider results into the standardized JobHunterAI schema.         Ens

### Community 78 - "limit_request_size"
Cohesion: 0.40
Nodes (5): health_check(), limit_request_size(), AsyncSession, get, middleware

### Community 79 - ".generate"
Cohesion: 0.40
Nodes (3): Any, Executes a standard structured JSON completion.          Args:             me, Provides a real-time token stream for the UI.

### Community 80 - "ApifyRegistryClient"
Cohesion: 0.40
Nodes (3): ApifyRegistryClient, Any, Hardened wrapper around ApifyClientAsync.

### Community 81 - "ApifyHealthChecker"
Cohesion: 0.40
Nodes (3): ApifyHealthChecker, Monitors Apify actor health by checking recent run status., Verify if the actor is healthy. Caches results for 5 mins.

### Community 84 - "test_router"
Cohesion: 0.50
Nodes (4): post, Request, Demonstrates the 3-tier fallback logic.     Returns cloud result by default, lo, test_router()

### Community 87 - "frontend/package.json"
Cohesion: 0.50
Nodes (3): name, type, version

### Community 89 - "telemetry"
Cohesion: 0.67
Nodes (3): get, Simple telemetry check as requested., telemetry()

## Knowledge Gaps
- **88 isolated node(s):** `name`, `version`, `type`, `dev:frontend`, `dev:backend` (+83 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JobService` connect `JobService` to `JobListingCreate`, `ApplicationStatus`, `recruiters.py`, `api/jobs.py`, `dependencies.py`, `JobListing`, `job_service.py`, `interview.py`, `matcher.py`, `.search_live`, `.discover_new_listings`, `profile.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `JobListingCreate` connect `JobListingCreate` to `JobService`, `ProviderLifecycle`, `JobRepository`, `apify_provider.py`, `job_service.py`, `ApifyProvider`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `ProviderManager` connect `ProviderManager` to `FaultyAIProvider`, `test_circuit_breaker.py`, `CircuitBreaker`, `exceptions.py`, `dependencies.py`, `providers/manager.py`, `CircuitBreakerProxy`, `AppLifecycleManager`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `JobService` (e.g. with `Config` and `TailorRequest`) actually correct?**
  _`JobService` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `ApplicationStatus` (e.g. with `AnalyticsEngine` and `ApplicationRepository`) actually correct?**
  _`ApplicationStatus` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ProviderManager` (e.g. with `DIContainer` and `DuplicateInstanceError`) actually correct?**
  _`ProviderManager` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `JobListingCreate` (e.g. with `ApifyProvider` and `IScraperProvider`) actually correct?**
  _`JobListingCreate` has 17 INFERRED edges - model-reasoned connections that need verification._