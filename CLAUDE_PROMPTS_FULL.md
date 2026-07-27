# 🤖 PROMPTS FOR CLAUDE/COPILOT TO EXECUTE FULL IMPLEMENTATION

This document contains copy-paste prompts you can send to Claude or GitHub Copilot to execute the entire implementation plan automatically.

---

## 📋 Table of Contents

1. **Phase 0: Critical Bug Fixes** (3 prompts)
2. **Phase 1: Smart Router Refactor** (3 prompts)
3. **Phase 2: Apify Registry** (5 prompts)
4. **Phase 3: Polish & Production** (4 prompts)

**Total: 15 prompts to complete everything**

---

## ⏱️ Estimated Time by Phase

- Phase 0: 2-3 hours (3 independent fixes)
- Phase 1: 2-3 hours (router + tests)
- Phase 2: 3-4 hours (registry + selector + tests)
- Phase 3: 2-3 hours (integration + docs)

**Total: ~10-13 hours of execution time**

---

# PHASE 0: CRITICAL BUG FIXES

## Prompt 0.1: Database Initialization

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Fix database initialization so tables are auto-created on app startup.

CURRENT PROBLEM:
- App starts but crashes with "table 'job_listings' does not exist" on first API call
- No database initialization in AppLifecycleManager.startup()

WHAT YOU NEED TO DO:
1. Open core/lifecycle.py
2. Replace AppLifecycleManager.startup() with this code that:
   - Imports Base from core.database.models
   - Imports async_engine from core.database.connection
   - Calls Base.metadata.create_all() via async connection
   - Logs success/failure
3. Create tests/unit/test_database_init.py with:
   - Test that startup creates tables
   - Test that startup is idempotent (safe to call twice)
   - Use SQLAlchemy text() queries to verify tables exist
4. Run pytest tests/unit/test_database_init.py -v and verify all tests pass
5. Commit with message: "fix: database initialization on app startup"

REFERENCE CODE:
See QUICK_START_PHASE_0.md section "Phase 0.1: Database Initialization Fix" for exact code to use.

OUTPUT:
Show me:
1. The updated core/lifecycle.py file
2. The new tests/unit/test_database_init.py file
3. Test run output showing all tests passing
```

---

## Prompt 0.2: Environment Variable Validation

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Fix environment variable validation bug in smart router.

CURRENT PROBLEM:
- config_dict.get(env) returns falsy for None values
- Cannot distinguish between "not set" and "set to empty string"
- Router incorrectly skips tiers or falls back prematurely

WHAT YOU NEED TO DO:
1. Open core/ai/smart_router.py
2. Add two new helper functions:
   - _is_api_key_set(config_dict: dict, key: str) -> bool
     * Check: value is not None AND str(value).strip() != ""
   - _check_required_envs(required_envs: List[Any], config_dict: dict) -> bool
     * Support AND logic (list items must all exist)
     * Support OR logic (list of lists, any one can exist)
3. Update the route() function to use _check_required_envs
4. Create tests/unit/test_settings_validation.py with:
   - Test missing key detected
   - Test empty string treated as missing
   - Test whitespace treated as missing
   - Test valid key detected
   - Test OR logic (at least one exists)
   - Test AND logic (all must exist)
   - Test mixed AND/OR logic
5. Run pytest tests/unit/test_settings_validation.py -v
6. Commit with message: "fix: environment variable validation for OR logic"

REFERENCE CODE:
See QUICK_START_PHASE_0.md section "Phase 0.2: Fix Environment Variable Validation"

OUTPUT:
Show me:
1. Updated core/ai/smart_router.py with new functions
2. New tests/unit/test_settings_validation.py
3. All tests passing
```

---

## Prompt 0.3: PII Redactor Hardening

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Fix PII redactor to use atomic regex substitution instead of unsafe .replace()

CURRENT PROBLEM:
- Using .replace() can cause partial replacements
- Example: redacting "John" might affect "Johnson"
- No UUID collision prevention
- Fragile and unpredictable

WHAT YOU NEED TO DO:
1. Open core/privacy.py
2. Replace entire file with updated PIIRedactor class that:
   - Uses re.sub() with callback function
   - Generates UUID for each placeholder
   - Stores mapping as it redacts
   - Has atomic substitution per pattern type
3. Create tests/unit/test_pii_redaction.py with:
   - Test email redaction
   - Test phone redaction
   - Test address redaction
   - Test multiple PII types together
   - Test no collisions on multiple instances
   - Test empty text handling
   - Test text with no PII
   - Test case insensitive matching
   - Test partial redaction prevention
   - Test unicode handling
   - Test mapping bidirectionality
4. Run pytest tests/unit/test_pii_redaction.py -v
5. Commit with message: "fix: atomic PII redaction with UUID collision prevention"

REFERENCE CODE:
See QUICK_START_PHASE_0.md section "Phase 0.3: Harden PII Redactor"

OUTPUT:
Show me:
1. Updated core/privacy.py
2. New tests/unit/test_pii_redaction.py
3. All tests passing
4. Example redaction/restore output
```

---

## ✅ Phase 0 Verification

After completing all 3 prompts above, run:

```bash
pytest tests/unit/test_database_init.py tests/unit/test_settings_validation.py tests/unit/test_pii_redaction.py -v --tb=short
```

Expected: **25+ tests all passing ✓**

Push to GitHub:
```bash
git push origin feature/architecture-stabilization
```

---

# PHASE 1: SMART ROUTER REFACTOR

## Prompt 1.1: Implement N-Tier Router

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Refactor smart router from 2-tier (primary + fallback) to N-tier (Groq → Gemini → Ollama → Local).

CURRENT STATE:
- route(primary_fn, fallback_fn, *args) only supports 2 tiers
- Needs to support unlimited tiers: route(tier1, tier2, tier3, tier4, *args)

WHAT YOU NEED TO DO:
1. Open core/ai/smart_router.py
2. Rewrite async def route() to accept *tier_functions instead of (primary_fn, fallback_fn)
3. Implement N-tier logic:
   - Loop through each tier_function in order
   - For each tier:
     * Check required_envs using _check_required_envs
     * If envs missing, skip to next tier
     * Try to execute tier
     * If it returns None, try next tier
     * If it raises exception, log and try next tier
     * If it succeeds, return result immediately
   - If all tiers fail, return safe_placeholder from last tier
4. Keep helper functions: _is_api_key_set and _check_required_envs
5. Add comprehensive logging at each step
6. Update docstring with clear examples

IMPLEMENTATION DETAILS:
- Handle both sync and async functions
- Check asyncio.iscoroutine() and await if needed
- Log different error types (safety, quota, auth, etc.)
- Each tier can have required_envs attribute
- Each tier can have safe_placeholder attribute
- Default safe_placeholder is {"error": "All tiers failed"}

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "1.1: Refactor Smart Router to N-Tier"

OUTPUT:
Show me:
1. Complete updated core/ai/smart_router.py with route() function
2. Confirm it handles: single tier, 3-tier chain, skipping tiers with missing env vars, None returns, exceptions, safe placeholders
```

---

## Prompt 1.2: Create N-Tier Router Tests

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Create comprehensive test suite for N-tier router.

WHAT YOU NEED TO DO:
1. Create tests/unit/test_n_tier_routing.py
2. Write these test cases (use pytest.mark.asyncio):
   - test_single_tier_execution: Verify single tier works
   - test_three_tier_fallback_chain: Tier1 fails → Tier2 fails → Tier3 succeeds
   - test_skip_tier_on_missing_env_vars: Skip tier if required envs missing
   - test_none_result_triggers_fallback: None from tier1 → try tier2
   - test_safe_placeholder_on_all_failure: All tiers fail → return safe_placeholder
   - test_mixed_sync_and_async_tiers: Handle both sync and async functions
   - test_environment_variable_or_logic: Test ["KEY_A", "KEY_B"] = at least one
   - test_environment_variable_and_logic: Test "KEY_A" = must have it
3. Run pytest tests/unit/test_n_tier_routing.py -v
4. Verify all tests pass
5. Output coverage report

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "4.1: Create N-Tier Routing Tests"

OUTPUT:
Show me:
1. Complete tests/unit/test_n_tier_routing.py
2. Test run output showing all tests passing
3. Coverage percentage
```

---

## Prompt 1.3: Document Router Breaking Changes

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Create migration guide documenting breaking changes from 2-tier to N-tier router.

WHAT YOU NEED TO DO:
1. Create BREAKING_CHANGES.md
2. Document:
   - OLD function signature: route(primary_fn, fallback_fn, *args, **kwargs)
   - NEW function signature: route(*tier_functions, *args, **kwargs)
   - What changed: positional args are now tiers, not just 2
   - How to migrate: show before/after examples
   - List all files needing updates (provide file names)
   - Show code migration example for each pattern:
     * Pattern 1: Simple cloud → local fallback
     * Pattern 2: Cloud → Cloud → Local (3-tier)
     * Pattern 3: With required_envs
3. Create checklists for:
   - Files to update
   - Things to test
4. Save as BREAKING_CHANGES.md

REFERENCE CODE:
Use examples from IMPLEMENTATION_CHECKLIST.md

OUTPUT:
Show me:
1. Complete BREAKING_CHANGES.md file
2. Confirm it covers: signature change, all affected files, migration patterns, testing checklist
```

---

## ✅ Phase 1 Verification

After completing all 3 prompts, run:

```bash
pytest tests/unit/test_n_tier_routing.py -v --tb=short
```

Expected: **8+ tests all passing ✓**

---

# PHASE 2: APIFY REGISTRY & CALL SITE UPDATES

## Prompt 2.1: Create YAML Registry Config

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Create YAML-based Apify actor registry configuration.

WHAT YOU NEED TO DO:
1. Create config/apify_actors.yaml
2. Structure with:
   - version: "1.0.0"
   - last_updated: ISO timestamp
   - scrapers: list of actor configs
   - local_scrapers: list of local fallback configs
3. For each scraper, include:
   - id: unique identifier
   - name: human readable name
   - actor_id: Apify actor ID
   - priority: 1 (highest) to 999 (lowest)
   - enabled: true/false
   - timeout_seconds: execution timeout
   - max_results: max results to return
   - cost_per_run_usd: estimated cost
   - description: what it does
   - capabilities: list of what it can scrape
   - requirements: list of required env vars
   - tags: searchable tags
   - retry_policy: max_retries, backoff_multiplier, initial_delay_ms
   - health_check: interval_minutes, timeout_seconds
4. Create at least 3 Apify actors:
   - LinkedIn (priority 1)
   - Indeed (priority 2)
   - Google Jobs (priority 3)
5. Create 1 local scraper:
   - JobSpy (priority 999)
6. Validate YAML syntax

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "2.1: Create YAML Registry Configuration"

OUTPUT:
Show me:
1. Complete config/apify_actors.yaml file
2. Confirm it's valid YAML
3. Show all 4 scrapers with proper structure
```

---

## Prompt 2.2: Implement Registry Loader

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Create ApifyActorRegistry class to load and manage actor configs from YAML.

WHAT YOU NEED TO DO:
1. Create core/providers/apify/__init__.py (empty or minimal)
2. Create core/providers/apify/registry.py with ApifyActorRegistry class:
   - __init__(config_path: str) - Load YAML config
   - _load_config() - Parse YAML file
   - _parse_actors() - Extract actors into dict
   - get_actor(actor_id: str) - Get one actor
   - get_enabled_actors() - Get all enabled actors sorted by priority
   - get_actors_by_capability(capability: str) - Filter by capability
   - mark_actor_healthy(actor_id: str) - Track health
   - mark_actor_unhealthy(actor_id: str, reason: str) - Track failures
   - is_actor_healthy(actor_id: str) -> bool - Check health status
3. Implement health_cache as dict
4. Add logging throughout
5. Create singleton: registry = ApifyActorRegistry()
6. Handle missing config gracefully (return empty dict)

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "2.2: Create Registry Loader"

OUTPUT:
Show me:
1. Complete core/providers/apify/registry.py
2. Confirm it can load config/apify_actors.yaml
3. Show example usage of each method
```

---

## Prompt 2.3: Implement Actor Selector

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Create ApifyActorSelector class to choose best actor for a query.

WHAT YOU NEED TO DO:
1. Create core/providers/apify/selector.py with ApifyActorSelector class:
   - __init__(registry_instance) - Accept registry dependency
   - select_actor(query: str, location: str) -> Optional[dict] - Choose single best actor
   - select_actors_parallel(query: str, count: int) -> List[dict] - Choose N actors
   - _infer_capabilities_from_query(query_lower: str) -> List[str] - Infer from keywords
2. Selection strategy:
   - Get enabled actors from registry
   - Infer capabilities from query ("linkedin" → ["linkedin"])
   - Filter to matching capabilities
   - Prefer healthy actors (subtract 10 from priority score)
   - Sort by priority and return best
   - If no matches, use all enabled actors
3. For parallel selection, return top N sorted by score
4. Add logging at each step
5. Create singleton: selector = ApifyActorSelector(registry)

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "2.3: Create Actor Selector"

OUTPUT:
Show me:
1. Complete core/providers/apify/selector.py
2. Example: select_actor("python developer linkedin", "Remote")
3. Example: select_actors_parallel("software engineer", 3)
4. Show capability inference for various queries
```

---

## Prompt 2.4: Implement Health Checker

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Create ApifyHealthChecker to monitor actor health.

WHAT YOU NEED TO DO:
1. Create core/providers/apify/health.py with ApifyHealthChecker class:
   - __init__(registry_instance) - Accept registry dependency
   - HEALTH_CHECK_CACHE_TTL_MINUTES = 5 (don't check too often)
   - async def check_actor_health(actor_id: str) -> bool
   - last_check_time: dict - Track last health check
2. Health check logic:
   - Use ApifyClient from apify_client package
   - Get actor_id from registry config
   - Call client.actor(apify_actor_id).call() with timeout
   - Check last run status
   - If "SUCCEEDED" → mark_actor_healthy
   - Otherwise → mark_actor_unhealthy
   - Cache result for 5 minutes
3. If client not initialized, assume healthy (don't over-react)
4. On any exception, log and assume healthy
5. Integrate with registry.mark_actor_healthy/unhealthy
6. Create singleton: health_checker = ApifyHealthChecker(registry)

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "2.4: Create Health Check Service"

OUTPUT:
Show me:
1. Complete core/providers/apify/health.py
2. Confirm it imports ApifyClient correctly
3. Show health check flow
```

---

## Prompt 2.5: Create Registry Tests

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Create comprehensive tests for Apify registry, selector, and health checker.

WHAT YOU NEED TO DO:
1. Create tests/unit/test_apify_registry.py
2. Write test cases:
   - test_registry_loads_yaml: Verify YAML loads correctly
   - test_get_enabled_actors_sorted_by_priority: Check sorting works
   - test_get_actors_by_capability: Filter by capability
   - test_actor_health_tracking: Mark healthy/unhealthy
   - test_selector_chooses_highest_priority: Best actor selected
   - test_selector_infers_capabilities_from_query: "linkedin" → linkedin actor
   - test_selector_parallel_actors: Get multiple actors ordered by priority
3. Use config/apify_actors.yaml as fixture
4. Run pytest tests/unit/test_apify_registry.py -v
5. Verify all tests pass

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "4.2: Create Apify Registry Tests"

OUTPUT:
Show me:
1. Complete tests/unit/test_apify_registry.py
2. All tests passing
3. Coverage report
```

---

## ✅ Phase 2 Verification

After all 5 prompts, run:

```bash
pytest tests/unit/test_apify_registry.py -v --tb=short
```

Expected: **7+ tests all passing ✓**

---

# PHASE 3: CALL SITE UPDATES & POLISH

## Prompt 3.1: Update Router Call Sites - Part 1

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Update router call sites from 2-tier route(primary, fallback) to N-tier route(tier1, tier2, tier3).

PART 1: Update LLM Client (core/ai/llm_client.py)

CURRENT CODE:
The SmartLLMClient.chat_completion() calls:
```python
return await route(try_primary, try_fallback)
```

NEW CODE SHOULD:
```python
async def groq_tier():
    client = GroqLLMClient()
    if not client.client:
        raise ValueError("Groq client not initialized")
    target_model = model or settings.GROQ_MODEL
    return await client.chat_completion(target_model, messages)

groq_tier.required_envs = ["GROQ_API_KEY"]
groq_tier.safe_placeholder = {"error": "Groq tier failed"}

async def gemini_tier():
    client = GeminiLLMClient()
    if not client.client:
        raise ValueError("Gemini client not initialized")
    target_model = model or settings.GEMINI_MODEL
    return await client.chat_completion(target_model, messages)

gemini_tier.required_envs = ["GEMINI_API_KEY"]
gemini_tier.safe_placeholder = {"error": "Gemini tier failed"}

async def ollama_tier():
    client = OllamaLLMClient()
    if not client.client:
        raise ValueError("Ollama client not initialized")
    target_model = model or settings.OLLAMA_MODEL
    return await client.chat_completion(target_model, messages)

ollama_tier.required_envs = []
ollama_tier.safe_placeholder = {"error": "All LLM tiers exhausted"}

return await route(groq_tier, gemini_tier, ollama_tier)
```

WHAT YOU NEED TO DO:
1. Open core/ai/llm_client.py
2. Find SmartLLMClient.chat_completion() method
3. Replace the entire method with code above
4. Test: pytest tests/unit/test_llm_client.py -v
5. Commit: "refactor: update LLM client to 3-tier routing"

OUTPUT:
Show me:
1. Updated SmartLLMClient.chat_completion() method
2. Test results
```

---

## Prompt 3.2: Update Router Call Sites - Part 2

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Update remaining router call sites (Part 2 of router migration).

FILES TO UPDATE (all follow same pattern - 2-tier to 3-tier):

1. core/ai/matcher.py - JobMatcher.analyze_fit()
2. core/ai/generator.py - generate_cover_letter()
3. core/ai/resume_parser.py - parse_resume()
4. core/scraper.py - scrape_jobs()
5. core/resume_engine.py - tailor_bullets()
6. core/enricher.py - find_decision_makers()

MIGRATION PATTERN:

OLD:
```python
return await route(cloud_tier, local_tier)
```

NEW (3-tier):
```python
async def groq_tier():
    # ... groq implementation
groq_tier.required_envs = ["GROQ_API_KEY"]

async def gemini_tier():
    # ... gemini implementation
gemini_tier.required_envs = ["GEMINI_API_KEY"]

async/def local_tier():
    # ... local implementation
local_tier.required_envs = []

return await route(groq_tier, gemini_tier, local_tier)
```

WHAT YOU NEED TO DO:
1. For each file above, apply the pattern
2. Add 3-tier routing
3. Update required_envs accordingly
4. Update any nested route() calls (flatten them)
5. Run tests for each file
6. Commit for each file: "refactor: update [FILE] to 3-tier routing"

USE THESE AS REFERENCE:
- core/ai/matcher.py: See IMPLEMENTATION_CHECKLIST.md section on matcher
- Others: Similar pattern

OUTPUT:
Show me:
1. All 6 files updated
2. Test results for each
3. Confirm all tests passing
```

---

## Prompt 3.3: Refactor Scraper to Use Registry

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Refactor core/scraper.py to use Apify Actor Registry.

CURRENT CODE:
- apify_scrape() uses hardcoded APIFY_ACTOR_ID
- local_scrape() uses JobSpy
- scrape_jobs() calls route(apify_scrape, local_scrape)

NEW CODE SHOULD:
- apify_scrape_v2() uses selector to choose actor dynamically
- local_scrape_v2() keeps JobSpy logic
- scrape_jobs_v2() calls route(apify_tier, jobspy_tier)
- Keep old function names for backward compatibility
- scrape_jobs() should call scrape_jobs_v2() internally

WHAT YOU NEED TO DO:
1. Open core/scraper.py
2. Import:
   - from core.providers.apify.registry import registry
   - from core.providers.apify.selector import selector
   - from core.providers.apify.health import health_checker
3. Create async def apify_scrape_v2(payload):
   - Use selector.select_actor(query, location)
   - Get apify_actor_id from selected_actor
   - Call ApifyClient with selected actor
   - Mark healthy on success
   - Mark unhealthy on failure
   - Return {"source": "apify", "data": results, "actor": actor_id}
4. Create async def local_scrape_v2(payload):
   - Keep existing JobSpy logic
5. Create async def scrape_jobs_v2(payload):
   - Create tier functions
   - Call route(apify_tier, jobspy_tier)
   - Normalize results
6. Update scrape_jobs() to call scrape_jobs_v2()
7. Test manually: call scrape_jobs with different queries
8. Commit: "refactor: scraper uses Apify registry and dynamic actor selection"

REFERENCE CODE:
See IMPLEMENTATION_CHECKLIST.md section "2.5: Refactor Scraper to Use Registry"

OUTPUT:
Show me:
1. Updated core/scraper.py with v2 functions
2. Example scrape_jobs() call with output
3. Confirm it selected the right actor
```

---

## Prompt 3.4: Final Polish & Deployment

**Send this to Claude/Copilot:**

```
You are working on the JobHunterAI repository at https://github.com/IamAzmathullaShaikh/JobHunterAI on branch feature/architecture-stabilization.

TASK: Final polish - code quality, documentation, and deployment preparation.

WHAT YOU NEED TO DO:

1. CODE FORMATTING:
   - Run: black backend/ core/ tests/
   - Run: isort backend/ core/ tests/
   - Run: flake8 backend/ core/ tests/ --max-line-length=120
   - Fix any issues

2. CONFIGURATION (core/config/settings.py):
   - Add Apify settings:
     * APIFY_ENABLED: bool = True
     * APIFY_API_TOKEN: Optional[str] = None
     * APIFY_MAX_CONCURRENT_RUNS: int = 3
     * APIFY_RUN_TIMEOUT_SECONDS: int = 120
     * APIFY_HEALTH_CHECK_INTERVAL_MINUTES: int = 60
     * APIFY_ACTORS_CONFIG_PATH: str = "config/apify_actors.yaml"
     * APIFY_FALLBACK_TO_SAMPLE: bool = True

3. UPDATE README.md:
   - Add "3-Tier AI Routing" section explaining Groq → Gemini → Local
   - Add "Multi-Platform Job Scraping" section with registry explanation
   - Add "Zero-Trust PII Redaction" section
   - Add configuration examples for each provider

4. CREATE CI/CD WORKFLOW:
   - Create .github/workflows/lint.yml
   - Run Black, isort, Flake8 on push
   - Run pytest tests/
   - Run frontend linting (optional)

5. FINAL VERIFICATION:
   - Run full test suite: pytest tests/ -v --cov
   - Check coverage > 80%
   - No errors or warnings

6. COMMIT:
   - "feat: code quality, config, and CI/CD setup"

WHAT TO SHOW ME:
1. Code formatting summary (before/after files changed)
2. Updated core/config/settings.py with Apify fields
3. Updated README.md with new sections
4. .github/workflows/lint.yml workflow file
5. Full pytest output with coverage report
5. Confirm all tests passing
```

---

## ✅ FULL IMPLEMENTATION VERIFICATION

After all prompts completed, run this final verification:

```bash
# 1. All tests passing
pytest tests/ -v --cov --tb=short

# 2. Code quality checks
black --check backend/ core/ tests/
isort --check-only backend/ core/ tests/
flake8 backend/ core/ tests/ --max-line-length=120

# 3. Fresh database initialization
python -c "import asyncio; from core.lifecycle import AppLifecycleManager; asyncio.run(AppLifecycleManager.startup()); print('✓ Database initialized')"

# 4. Router test
curl -X POST http://localhost:8000/api/system/test-router \
  -H "Content-Type: application/json" \
  -d '{"force_fail": false}'

# 5. Push to GitHub
git push origin feature/architecture-stabilization
```

Expected output:
```
✅ All tests passing (25+ tests)
✅ Code quality checks pass
✅ Database initializes
✅ Router works
✅ Ready for production
```

---

## 🎯 QUICK REFERENCE: WHICH PROMPT FOR WHICH PHASE

| Phase | Prompts | Time | Key Deliverable |
|-------|---------|------|-----------------|
| 0 | 0.1, 0.2, 0.3 | 2-3h | Database init, env validation, PII redaction |
| 1 | 1.1, 1.2, 1.3 | 2-3h | N-tier router, tests, breaking changes doc |
| 2 | 2.1, 2.2, 2.3, 2.4, 2.5 | 3-4h | YAML registry, selector, health checks, scraper |
| 3 | 3.1, 3.2, 3.3, 3.4 | 2-3h | Call site updates, scraper refactor, polish |
| **Total** | **15 prompts** | **10-13h** | **Production-ready codebase** |

---

## 🚀 HOW TO USE THESE PROMPTS

1. **Start with Phase 0.1** - Send the prompt to Claude
2. **Review output** - Read the response carefully
3. **Copy code** - Use the code snippets provided
4. **Run tests** - Execute pytest commands
5. **Move to next prompt** - Once previous is verified
6. **Commit frequently** - After each major task
7. **Report blockers** - If anything fails, ask Claude for help

---

## 📝 EXAMPLE: How to Send First Prompt

Send this to Claude in a new conversation:

```
I need to implement architecture stabilization for JobHunterAI repository.

Here's the FIRST PROMPT to execute:

[PASTE PROMPT 0.1 TEXT HERE]

Start with this exact task and show me all the code changes needed.
```

Then Claude will respond with the complete implementation. Copy the code, test it locally, and commit.

---

**Ready to get started? Send Prompt 0.1 to Claude! 🚀**
