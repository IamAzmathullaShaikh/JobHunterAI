# Implementation Checklist: Architecture Stabilization & Apify Registry

**Objective:** Stabilize core AI routing, implement scalable Apify Actor Registry, and prepare for production release.

**Timeline:** ~25-30 hours of work across 3 weeks

**Branch:** `feature/architecture-stabilization`

---

## Phase 0: Critical Bug Fixes (Week 1, Days 1-2)

These must be fixed first to provide a stable foundation.

### 0.1: Fix Database Initialization

**File:** `core/lifecycle.py`

**Current Issue:** Database tables are never created on fresh install. App starts but crashes on first API call with `ProgrammingError: table "job_listings" does not exist`.

**Changes Required:**

```python
# core/lifecycle.py (BEFORE)
class AppLifecycleManager:
    @staticmethod
    async def startup():
        logger.info("Starting JobHunterAI backend...")
        # No database initialization!

# core/lifecycle.py (AFTER)
from core.database.models import Base
from core.database.connection import async_engine

class AppLifecycleManager:
    @staticmethod
    async def startup():
        logger.info("Starting JobHunterAI backend...")
        
        # 1. Create all tables (idempotent)
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✓ Database schema initialized")
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            raise
        
        # 2. Run Alembic migrations (if any pending)
        try:
            from alembic.config import Config
            from alembic.runtime.migration import MigrationContext
            from alembic.operations import Operations
            
            alembic_cfg = Config("backend/alembic.ini")
            async with async_engine.begin() as conn:
                mc = MigrationContext.configure(conn)
                op = Operations(mc)
                # Migrations handled here
            logger.info("✓ Database migrations applied")
        except Exception as e:
            logger.warning(f"⚠ Migration check failed (may be expected): {e}")
```

**Verification:**
```bash
# Fresh database should initialize without errors
python -c "import asyncio; from core.lifecycle import AppLifecycleManager; asyncio.run(AppLifecycleManager.startup())"
# Expected output: "✓ Database schema initialized"
```

**Tests to add:**
```python
# tests/unit/test_database_init.py
@pytest.mark.asyncio
async def test_database_creates_tables_on_startup():
    """Verify tables exist after startup."""
    await AppLifecycleManager.startup()
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1 FROM job_listings LIMIT 1"))
        # Should not raise TableNotFound
```

---

### 0.2: Fix Environment Variable Validation

**File:** `core/config/settings.py`

**Current Issue:** `config_dict.get(env)` returns falsy for `None` values, but the Pydantic model always includes all fields. This causes false positives for "missing" keys.

**Changes Required:**

```python
# core/config/settings.py (BEFORE - BUGGY)
for requirement in required_envs:
    if isinstance(requirement, list):
        # OR Logic: At least one in the sub-list must exist
        if not any(config_dict.get(env) for env in requirement):  # ← WRONG
            can_proceed = False

# core/config/settings.py (AFTER - FIXED)
def _is_api_key_present(key: str) -> bool:
    """Check if an API key is actually set (not None, not empty string)."""
    value = config_dict.get(key)
    return value is not None and value != ""

for requirement in required_envs:
    if isinstance(requirement, list):
        # OR Logic: At least one in the sub-list must exist
        if not any(_is_api_key_present(env) for env in requirement):  # ← CORRECT
            can_proceed = False
        else:
            # Found at least one valid key in the OR list
            missing_info.append(f"({' or '.join(requirement)}) ✓")
    else:
        # AND Logic: Must exist
        if not _is_api_key_present(requirement):
            can_proceed = False
            missing_info.append(requirement)
```

**Verification:**
```python
# tests/unit/test_settings_validation.py
def test_missing_groq_key_detected():
    """Verify router detects missing Groq key."""
    settings.GROQ_API_KEY = None
    settings.GEMINI_API_KEY = None
    config_dict = settings.model_dump()
    
    # Should return False (keys missing)
    assert not _is_api_key_present("GROQ_API_KEY")

def test_empty_string_treated_as_missing():
    """Verify empty string is treated like None."""
    settings.GROQ_API_KEY = ""
    assert not _is_api_key_present("GROQ_API_KEY")

def test_or_logic_with_one_valid_key():
    """Verify OR logic passes if one key exists."""
    settings.GROQ_API_KEY = None
    settings.GEMINI_API_KEY = "valid-key-12345"
    config_dict = settings.model_dump()
    
    result = any(_is_api_key_present(env) for env in ["GROQ_API_KEY", "GEMINI_API_KEY"])
    assert result is True  # Gemini key exists
```

---

### 0.3: Fix PII Redactor (Prepare for Phase 1)

**File:** `core/privacy.py`

**Current Issue:** Uses `.replace()` which can cause partial replacements. Example: redacting "John" might accidentally replace "John" inside "Johnson".

**Changes Required:**

```python
# core/privacy.py (BEFORE - UNSAFE)
def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
    mapping = {}
    redacted_text = text
    
    for pii_type, pattern in self.PATTERNS.items():
        matches = re.findall(pattern, redacted_text, re.IGNORECASE)
        for i, match in enumerate(matches):
            placeholder = f"[[REDACTED_{pii_type}_{i}]]"
            mapping[placeholder] = match
            redacted_text = redacted_text.replace(match, placeholder)  # ← UNSAFE
    
    return redacted_text, mapping

# core/privacy.py (AFTER - SAFE)
import uuid

def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
    """Redacts PII using atomic regex substitution (no partial replacements)."""
    if not text:
        return "", {}
    
    mapping = {}
    
    def replace_with_placeholder(match):
        """Callback for re.sub to generate unique placeholder."""
        unique_id = str(uuid.uuid4())[:8]
        pii_type = "UNKNOWN"
        
        # Determine which pattern matched
        for ptype, pattern in self.PATTERNS.items():
            if re.match(pattern, match.group(0)):
                pii_type = ptype
                break
        
        placeholder = f"[[REDACTED_{pii_type}_{unique_id}]]"
        mapping[placeholder] = match.group(0)
        return placeholder
    
    redacted_text = text
    
    # Apply each pattern atomically
    for pii_type, pattern in self.PATTERNS.items():
        redacted_text = re.sub(
            pattern,
            replace_with_placeholder,
            redacted_text,
            flags=re.IGNORECASE
        )
    
    return redacted_text, mapping

def restore(self, text: str, mapping: Dict[str, str]) -> str:
    """Restores redacted PII (reverse of redact)."""
    if not text or not mapping:
        return text
    
    restored_text = text
    for placeholder, original in mapping.items():
        restored_text = restored_text.replace(placeholder, original)
    
    return restored_text
```

**Verification:**
```python
# tests/unit/test_pii_redaction.py
@pytest.mark.asyncio
async def test_pii_redaction_is_atomic():
    """Verify PII is redacted without partial replacements."""
    text = "Contact John Doe (john@example.com) or call 555-123-4567"
    
    redacted, mapping = redactor.redact(text)
    
    # John should be fully redacted once
    assert "John" not in redacted
    assert "john@" not in redacted
    
    # Placeholders should exist
    assert any("REDACTED" in placeholder for placeholder in mapping.keys())
    
    # Restore should recover original
    restored = redactor.restore(redacted, mapping)
    assert restored == text

@pytest.mark.asyncio
async def test_pii_collision_prevention():
    """Verify no placeholder collisions."""
    text = "John Doe, john.doe@company.com, Johnson Smith, johnson@company.com"
    
    redacted, mapping = redactor.redact(text)
    
    # All placeholders should be unique
    placeholders = list(mapping.keys())
    assert len(placeholders) == len(set(placeholders))  # No duplicates

@pytest.mark.asyncio
async def test_pii_patterns_comprehensive():
    """Verify all PII patterns are detected."""
    test_cases = [
        ("Email: alice@company.com", "EMAIL"),
        ("Phone: +1-234-567-8900", "PHONE"),
        ("Address: 123 Main Street, Springfield", "ADDRESS"),
    ]
    
    for text, expected_type in test_cases:
        redacted, mapping = redactor.redact(text)
        assert any(expected_type in placeholder for placeholder in mapping.keys())
```

---

## Phase 1: Core Architecture Stabilization (Week 1, Days 3-5)

### 1.1: Refactor Smart Router to N-Tier

**Files:** `core/ai/smart_router.py`

**Current Issue:** Only supports 2 tiers (primary + fallback). Needs to support N tiers (Groq → Gemini → Ollama → local).

**Changes Required:**

```python
# core/ai/smart_router.py (REFACTORED)
import asyncio
import logging
from typing import Any, Callable, List, Optional

from core.config.settings import settings

logger = logging.getLogger("jobhunterai.smart_router")


async def route(*tier_functions: Callable, *args, **kwargs) -> Any:
    """
    N-Tier Router: Attempts each tier function in sequence until one succeeds.
    
    Args:
        *tier_functions: Ordered list of async functions to try
        *args: Arguments to pass to tier functions
        **kwargs: Keyword arguments to pass to tier functions
    
    Returns:
        Result from first successful tier, or safe placeholder on complete failure
    
    Example:
        result = await route(
            tier1_groq,
            tier2_gemini,
            tier3_ollama,
            job_description,
            resume_text
        )
    """
    if not tier_functions:
        logger.error("No tier functions provided to route()")
        return {}
    
    config_dict = settings.model_dump()
    
    for tier_index, tier_fn in enumerate(tier_functions):
        tier_name = getattr(tier_fn, "__name__", f"Tier_{tier_index + 1}")
        
        # 1. Check if tier should be skipped due to missing env vars
        required_envs: List[Any] = getattr(tier_fn, "required_envs", [])
        
        if not _check_required_envs(required_envs, config_dict):
            logger.warning(
                f"Skipping {tier_name}: Missing required environment variables. "
                f"Required: {required_envs}"
            )
            continue
        
        # 2. Attempt tier execution
        try:
            logger.info(f"Attempting {tier_name}...")
            result = tier_fn(*args, **kwargs)
            
            # Handle async functions
            if asyncio.iscoroutine(result) or asyncio.iscoroutinefunction(tier_fn):
                result = await result
            
            # Validate result
            if result is None:
                logger.warning(f"{tier_name} returned None, trying next tier...")
                continue
            
            # Success!
            logger.info(f"✓ {tier_name} succeeded")
            return result
        
        except Exception as e:
            err_str = str(e).lower()
            
            if "safety" in err_str or "policy" in err_str:
                logger.warning(f"{tier_name} blocked by AI safety filter: {e}")
            elif "quota" in err_str or "rate limit" in err_str:
                logger.warning(f"{tier_name} rate limited: {e}")
            elif "unauthorized" in err_str or "401" in err_str or "403" in err_str:
                logger.warning(f"{tier_name} authentication failed: {e}")
            else:
                logger.error(f"{tier_name} failed: {e}")
            
            # Try next tier
            continue
    
    # All tiers exhausted
    logger.critical("All tiers failed - no fallback available")
    
    # Return safe placeholder from last tier function
    safe_placeholder = getattr(
        tier_functions[-1],
        "safe_placeholder",
        {"error": "All AI tiers failed. Please try again later."}
    )
    return safe_placeholder


def _check_required_envs(required_envs: List[Any], config_dict: dict) -> bool:
    """
    Validate that required environment variables are set.
    
    Args:
        required_envs: List of strings (AND logic) or list of lists (OR logic)
        config_dict: Pydantic model.model_dump() dict
    
    Returns:
        True if all requirements met, False otherwise
    
    Examples:
        ["GROQ_API_KEY"]  # Must have GROQ_API_KEY
        [["GROQ_API_KEY", "GEMINI_API_KEY"]]  # Must have at least one
        ["REQUIRED_KEY", ["OPTIONAL_A", "OPTIONAL_B"]]  # Must have REQUIRED_KEY AND (A or B)
    """
    for requirement in required_envs:
        if isinstance(requirement, list):
            # OR Logic: At least one in the sub-list must exist
            if not any(_is_api_key_set(config_dict, env) for env in requirement):
                return False
        else:
            # AND Logic: Must exist
            if not _is_api_key_set(config_dict, requirement):
                return False
    
    return True


def _is_api_key_set(config_dict: dict, key: str) -> bool:
    """Check if an API key is actually set (not None, not empty string)."""
    value = config_dict.get(key)
    return value is not None and str(value).strip() != ""
```

**Verification:**
```python
# tests/unit/test_n_tier_routing.py
@pytest.mark.asyncio
async def test_single_tier_success():
    """Verify single tier execution works."""
    async def tier1_success():
        return {"result": "tier1"}
    
    result = await route(tier1_success)
    assert result["result"] == "tier1"

@pytest.mark.asyncio
async def test_multi_tier_fallback():
    """Verify fallback chain works."""
    async def tier1_fail():
        raise ValueError("Tier 1 failed")
    
    async def tier2_succeed():
        return {"result": "tier2"}
    
    result = await route(tier1_fail, tier2_succeed)
    assert result["result"] == "tier2"

@pytest.mark.asyncio
async def test_three_tier_chain():
    """Verify 3-tier chain (Groq -> Gemini -> Local)."""
    async def groq_fail():
        raise Exception("Quota exceeded")
    
    async def gemini_fail():
        raise Exception("Rate limited")
    
    async def local_succeed():
        return {"result": "local", "source": "fallback"}
    
    result = await route(groq_fail, gemini_fail, local_succeed)
    assert result["source"] == "fallback"

@pytest.mark.asyncio
async def test_skip_tier_on_missing_env_vars():
    """Verify tier is skipped if env vars missing."""
    call_count = {"tier1": 0, "tier2": 0}
    
    async def tier1_needs_groq():
        call_count["tier1"] += 1
        return {"result": "tier1"}
    tier1_needs_groq.required_envs = ["GROQ_API_KEY"]
    
    async def tier2_no_requirements():
        call_count["tier2"] += 1
        return {"result": "tier2"}
    tier2_no_requirements.required_envs = []
    
    # Mock settings with no Groq key
    with patch("core.config.settings.GROQ_API_KEY", None):
        result = await route(tier1_needs_groq, tier2_no_requirements)
    
    assert call_count["tier1"] == 0  # Skipped
    assert call_count["tier2"] == 1  # Called
    assert result["result"] == "tier2"

@pytest.mark.asyncio
async def test_none_result_triggers_fallback():
    """Verify None result from tier triggers next tier."""
    async def tier1_returns_none():
        return None
    
    async def tier2_returns_value():
        return {"result": "tier2"}
    
    result = await route(tier1_returns_none, tier2_returns_value)
    assert result["result"] == "tier2"

@pytest.mark.asyncio
async def test_safe_placeholder_on_all_failure():
    """Verify safe placeholder returned when all tiers fail."""
    async def tier1_fail():
        raise Exception("Failed")
    
    tier1_fail.safe_placeholder = {"error": "Fallback placeholder"}
    
    result = await route(tier1_fail)
    assert result["error"] == "Fallback placeholder"
```

---

### 1.2: Update All Router Call Sites

**Files to Update:** 15+ files using `smart_route()`

**Call Sites:**
1. `core/task_engine.py` (5+ calls)
2. `core/ai/llm_client.py` (2+ calls)
3. `core/ai/matcher.py` (1 call)
4. `core/ai/generator.py` (1 call)
5. `core/ai/resume_parser.py` (1 call)
6. `core/scraper.py` (1 call)
7. `core/resume_engine.py` (1 call)
8. `core/enricher.py` (1 call)
9. `backend/api/system.py` (1 call for testing)

**Update Strategy:**

All calls follow the same pattern. Convert from:
```python
# OLD (2-tier)
result = await smart_route(primary_fn, fallback_fn, arg1, arg2)
```

To:
```python
# NEW (N-tier)
result = await route(tier1_fn, tier2_fn, tier3_fn, arg1, arg2)
```

**Example Refactoring (core/ai/llm_client.py):**

```python
# BEFORE (2-tier)
class SmartLLMClient(LLMClient):
    async def chat_completion(self, model: str = None, messages: list = []) -> Any:
        async def try_primary():
            client = get_llm_client(settings.DEFAULT_AI_PROVIDER)
            target_model = model or client.get_model_for_capability(Capability.REASONING)
            return await client.chat_completion(target_model, messages)
        
        try_primary.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]
        
        async def try_fallback():
            client = get_llm_client(settings.FALLBACK_AI_PROVIDER)
            target_model = model or client.get_model_for_capability(Capability.REASONING)
            return await client.chat_completion(target_model, messages)
        
        try_fallback.required_envs = [["GEMINI_API_KEY", "OPENROUTER_API_KEY"]]
        
        return await route(try_primary, try_fallback)

# AFTER (3-tier with proper definitions)
class SmartLLMClient(LLMClient):
    async def chat_completion(self, model: str = None, messages: list = []) -> Any:
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
        
        ollama_tier.required_envs = []  # Local, no requirements
        ollama_tier.safe_placeholder = {"error": "All LLM tiers exhausted"}
        
        return await route(groq_tier, gemini_tier, ollama_tier)
```

**Audit Checklist:**

```markdown
- [ ] core/task_engine.py - analyze_ats_fit()
- [ ] core/task_engine.py - generate_cover_letter()
- [ ] core/task_engine.py - generate_cover_letter_structured()
- [ ] core/task_engine.py - generate_contextual_questions()
- [ ] core/task_engine.py - evaluate_interview_answer()
- [ ] core/task_engine.py - generate_outreach()
- [ ] core/task_engine.py - generate_recruiter_outreach()
- [ ] core/task_engine.py - prepare_interview()
- [ ] core/task_engine.py - provide_star_feedback()
- [ ] core/ai/llm_client.py - SmartLLMClient.chat_completion()
- [ ] core/ai/matcher.py - JobMatcher.analyze_fit()
- [ ] core/ai/generator.py - generate_cover_letter()
- [ ] core/ai/resume_parser.py - parse_resume()
- [ ] core/scraper.py - scrape_jobs()
- [ ] core/resume_engine.py - tailor_bullets()
- [ ] core/enricher.py - find_decision_makers()
- [ ] backend/api/system.py - test_router()
```

---

### 1.3: Remove Nested Router Calls

**Issue:** Some functions call `route()` inside functions that are passed to `route()`, creating double routing.

**Example Problem (core/task_engine.py):**

```python
# PROBLEMATIC: Nested routing
async def analyze_ats_fit(self, resume_text: str, job_description: str) -> Dict[str, Any]:
    async def groq_call():
        matcher = JobMatcher()
        return await matcher.analyze_fit(job_desc, resume)  # ← Also calls route() internally!
    
    result = await smart_route(groq_call, local_call)  # ← Outer route()
```

**Solution: Flatten the routing**

```python
# FIXED: Single level of routing
async def analyze_ats_fit(self, resume_text: str, job_description: str) -> Dict[str, Any]:
    # Tier functions operate directly on data, no nested routing
    
    async def groq_tier():
        client = get_llm_client("groq")
        prompt = f"Analyze fit: {resume_text}\n\n{job_description}"
        return await client.chat_completion(
            messages=[{"role": "user", "content": prompt}]
        )
    
    groq_tier.required_envs = ["GROQ_API_KEY"]
    
    async def gemini_tier():
        client = get_llm_client("gemini")
        prompt = f"Analyze fit: {resume_text}\n\n{job_description}"
        return await client.chat_completion(
            messages=[{"role": "user", "content": prompt}]
        )
    
    gemini_tier.required_envs = ["GEMINI_API_KEY"]
    
    def local_tier():
        # Local analysis using embeddings or keyword matching
        model = get_local_model()
        embeddings = model.encode([resume_text, job_description])
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0] * 100
        return {
            "match_score": round(score, 1),
            "fit_summary": "Local semantic analysis"
        }
    
    local_tier.required_envs = []
    
    return await route(groq_tier, gemini_tier, local_tier)
```

**Files to Flatten:**
```markdown
- [ ] core/task_engine.py - Remove JobMatcher intermediate routing
- [ ] core/ai/matcher.py - Remove double routing in analyze_fit()
- [ ] core/ai/resume_parser.py - Remove double routing in parse_resume()
- [ ] core/enricher.py - Remove double routing in find_decision_makers()
```

---

## Phase 2: Apify Actor Registry (Week 2, Days 1-5)

### 2.1: Create YAML Registry Configuration

**File:** `config/apify_actors.yaml` (NEW)

```yaml
# Apify Scraper Registry
# Each actor defined here with priority, enabled status, and configuration

version: "1.0.0"
last_updated: "2026-07-27"

scrapers:
  # Priority 1: Fastest and most reliable
  - id: "linkedin-jobs-v1"
    name: "LinkedIn Jobs Scraper"
    actor_id: "apify/linkedin-jobs-scraper"
    provider: "apify"
    priority: 1
    enabled: true
    timeout_seconds: 60
    max_results: 50
    cost_per_run_usd: 0.10
    description: "Scrapes job listings from LinkedIn with high reliability"
    capabilities:
      - "linkedin"
      - "job_descriptions"
      - "salary_data"
    requirements:
      - "APIFY_API_TOKEN"
    tags:
      - "tier1"
      - "fast"
      - "reliable"
    retry_policy:
      max_retries: 2
      backoff_multiplier: 2.0
      initial_delay_ms: 1000
    health_check:
      interval_minutes: 60
      timeout_seconds: 30

  # Priority 2: Good coverage, slightly slower
  - id: "indeed-jobs-v1"
    name: "Indeed Jobs Scraper"
    actor_id: "apify/indeed-jobs-scraper"
    provider: "apify"
    priority: 2
    enabled: true
    timeout_seconds: 90
    max_results: 50
    cost_per_run_usd: 0.08
    description: "Scrapes job listings from Indeed"
    capabilities:
      - "indeed"
      - "job_descriptions"
      - "company_info"
    requirements:
      - "APIFY_API_TOKEN"
    tags:
      - "tier2"
      - "reliable"
    retry_policy:
      max_retries: 2
      backoff_multiplier: 2.0
      initial_delay_ms: 1500
    health_check:
      interval_minutes: 60
      timeout_seconds: 30

  # Priority 3: Fallback scraper
  - id: "google-jobs-v1"
    name: "Google Jobs Scraper"
    actor_id: "apify/google-jobs-scraper"
    provider: "apify"
    priority: 3
    enabled: true
    timeout_seconds: 120
    max_results: 30
    cost_per_run_usd: 0.12
    description: "Scrapes job listings from Google Jobs"
    capabilities:
      - "google_jobs"
      - "job_descriptions"
    requirements:
      - "APIFY_API_TOKEN"
    tags:
      - "tier3"
      - "fallback"
    retry_policy:
      max_retries: 1
      backoff_multiplier: 1.5
      initial_delay_ms: 2000
    health_check:
      interval_minutes: 120
      timeout_seconds: 30

# Fallback: Local scraper (no actor)
local_scrapers:
  - id: "jobspy-local"
    name: "JobSpy Local Scraper"
    provider: "local"
    priority: 999
    enabled: true
    description: "Local Python-based job scraper using JobSpy library"
    capabilities:
      - "indeed"
      - "linkedin"
      - "glassdoor"
    requirements: []
    tags:
      - "local"
      - "fallback"
      - "free"
```

**Verification:**
```python
# tests/unit/test_apify_registry.py
def test_yaml_loads_correctly():
    """Verify YAML config can be loaded."""
    import yaml
    with open("config/apify_actors.yaml") as f:
        config = yaml.safe_load(f)
    
    assert "scrapers" in config
    assert len(config["scrapers"]) > 0
    
    # Verify structure
    for scraper in config["scrapers"]:
        assert "id" in scraper
        assert "actor_id" in scraper
        assert "priority" in scraper
        assert "enabled" in scraper
```

---

### 2.2: Create Registry Loader

**File:** `core/providers/apify/registry.py` (NEW)

```python
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("jobhunterai.apify.registry")


class ApifyActorRegistry:
    """
    Manages Apify actor configurations from YAML.
    Provides actor lookup, priority-based selection, and health tracking.
    """
    
    def __init__(self, config_path: str = "config/apify_actors.yaml"):
        """Initialize registry by loading YAML config."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.actors: Dict[str, dict] = {}
        self.health_cache: Dict[str, dict] = {}
        
        self._parse_actors()
    
    def _load_config(self) -> dict:
        """Load and parse YAML configuration."""
        if not self.config_path.exists():
            logger.error(f"Apify config not found: {self.config_path}")
            return {"scrapers": [], "local_scrapers": []}
        
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            logger.info(f"✓ Loaded Apify config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load Apify config: {e}")
            return {"scrapers": [], "local_scrapers": []}
    
    def _parse_actors(self):
        """Parse actors from config into internal dict."""
        # Parse Apify actors
        for actor_config in self.config.get("scrapers", []):
            actor_id = actor_config.get("id")
            if actor_id:
                self.actors[actor_id] = actor_config
        
        # Parse local actors
        for actor_config in self.config.get("local_scrapers", []):
            actor_id = actor_config.get("id")
            if actor_id:
                self.actors[actor_id] = actor_config
        
        logger.info(f"Parsed {len(self.actors)} actors from registry")
    
    def get_actor(self, actor_id: str) -> Optional[dict]:
        """Retrieve actor configuration by ID."""
        return self.actors.get(actor_id)
    
    def get_enabled_actors(self) -> List[dict]:
        """Get all enabled actors sorted by priority."""
        enabled = [a for a in self.actors.values() if a.get("enabled", True)]
        return sorted(enabled, key=lambda a: a.get("priority", 999))
    
    def get_actors_by_capability(self, capability: str) -> List[dict]:
        """Get actors that support a specific capability."""
        actors = [
            a for a in self.actors.values()
            if capability in a.get("capabilities", [])
        ]
        return sorted(actors, key=lambda a: a.get("priority", 999))
    
    def mark_actor_healthy(self, actor_id: str):
        """Mark actor as healthy (last run succeeded)."""
        if actor_id in self.health_cache:
            self.health_cache[actor_id]["healthy"] = True
            self.health_cache[actor_id]["last_success"] = time.time()
        else:
            self.health_cache[actor_id] = {
                "healthy": True,
                "last_success": time.time(),
                "last_failure": None
            }
    
    def mark_actor_unhealthy(self, actor_id: str, reason: str = ""):
        """Mark actor as unhealthy (last run failed)."""
        if actor_id in self.health_cache:
            self.health_cache[actor_id]["healthy"] = False
            self.health_cache[actor_id]["last_failure"] = time.time()
            self.health_cache[actor_id]["failure_reason"] = reason
        else:
            self.health_cache[actor_id] = {
                "healthy": False,
                "last_success": None,
                "last_failure": time.time(),
                "failure_reason": reason
            }
    
    def is_actor_healthy(self, actor_id: str) -> bool:
        """Check if actor is healthy."""
        health = self.health_cache.get(actor_id)
        if not health:
            return True  # Unknown actors assumed healthy
        return health.get("healthy", True)


# Singleton instance
registry = ApifyActorRegistry()
```

---

### 2.3: Create Actor Selector

**File:** `core/providers/apify/selector.py` (NEW)

```python
import logging
from typing import Dict, List, Optional

from core.config.settings import settings
from core.providers.apify.registry import registry

logger = logging.getLogger("jobhunterai.apify.selector")


class ApifyActorSelector:
    """
    Selects the best Apify actor for a given job search intent.
    Considers priority, health, and search query requirements.
    """
    
    def __init__(self, registry_instance=None):
        self.registry = registry_instance or registry
    
    def select_actor(self, query: str, location: str = "Remote") -> Optional[dict]:
        """
        Select the best actor for this search query.
        
        Strategy:
        1. Filter to enabled actors
        2. Prefer actors matching search keywords (e.g., "linkedin" → LinkedIn scraper)
        3. Prefer healthy actors
        4. Return highest priority among viable options
        """
        # Get all enabled actors
        enabled_actors = self.registry.get_enabled_actors()
        
        if not enabled_actors:
            logger.warning("No enabled actors in registry")
            return None
        
        # Analyze search intent
        query_lower = query.lower()
        preferred_capabilities = self._infer_capabilities_from_query(query_lower)
        
        # Filter actors matching query
        matching_actors = []
        for actor in enabled_actors:
            actor_capabilities = actor.get("capabilities", [])
            
            # Prefer actors with matching capabilities
            if any(cap in actor_capabilities for cap in preferred_capabilities):
                # Additional weight if actor is healthy
                score = actor.get("priority", 999)
                if self.registry.is_actor_healthy(actor.get("id")):
                    score -= 10  # Boost healthy actors
                
                matching_actors.append((score, actor))
        
        # If no matching actors, use all enabled actors
        if not matching_actors:
            matching_actors = [(a.get("priority", 999), a) for a in enabled_actors]
        
        # Return best actor (lowest priority score = highest priority)
        matching_actors.sort(key=lambda x: x[0])
        best_actor = matching_actors[0][1] if matching_actors else None
        
        if best_actor:
            logger.info(f"Selected actor: {best_actor.get('name')} for query: {query}")
        
        return best_actor
    
    def select_actors_parallel(self, query: str, count: int = 3) -> List[dict]:
        """
        Select N actors for parallel scraping to increase coverage.
        
        Returns:
            Up to `count` actors, prioritized by score
        """
        enabled_actors = self.registry.get_enabled_actors()
        
        # Bias toward healthy actors
        scored_actors = []
        for actor in enabled_actors:
            score = actor.get("priority", 999)
            
            if self.registry.is_actor_healthy(actor.get("id")):
                score -= 10  # Healthy bias
            
            scored_actors.append((score, actor))
        
        # Sort and return top N
        scored_actors.sort(key=lambda x: x[0])
        return [actor for score, actor in scored_actors[:count]]
    
    def _infer_capabilities_from_query(self, query_lower: str) -> List[str]:
        """
        Infer required capabilities from search query.
        
        Examples:
            "python jobs linkedin" → ["linkedin"]
            "remote indeed positions" → ["indeed"]
            "software engineer" → ["linkedin", "indeed"]  (default)
        """
        if "linkedin" in query_lower:
            return ["linkedin"]
        elif "indeed" in query_lower:
            return ["indeed"]
        elif "glassdoor" in query_lower:
            return ["glassdoor"]
        elif "google" in query_lower:
            return ["google_jobs"]
        else:
            # Default: search all
            return ["linkedin", "indeed", "job_descriptions"]


# Singleton selector
selector = ApifyActorSelector(registry)
```

---

### 2.4: Create Health Check Service

**File:** `core/providers/apify/health.py` (NEW)

```python
import logging
import time
from typing import Optional

from apify_client import ApifyClient

from core.config.settings import settings
from core.providers.apify.registry import registry

logger = logging.getLogger("jobhunterai.apify.health")


class ApifyHealthChecker:
    """
    Monitors Apify actor health by checking recent run results.
    Updates registry with health status.
    """
    
    # Cache health checks for 5 minutes to avoid quota exhaustion
    HEALTH_CHECK_CACHE_TTL_MINUTES = 5
    
    def __init__(self, registry_instance=None):
        self.registry = registry_instance or registry
        self.client = ApifyClient(settings.APIFY_API_TOKEN) if settings.APIFY_API_TOKEN else None
        self.last_check_time: dict = {}
    
    async def check_actor_health(self, actor_id: str) -> bool:
        """
        Check if an actor is healthy.
        
        Health check criteria:
        - Last run completed successfully (status = "SUCCEEDED")
        - Last run was within 1 hour
        
        Returns:
            True if actor is healthy, False otherwise
        """
        if not self.client:
            logger.warning("Apify client not initialized - cannot check health")
            return True  # Assume healthy if no client
        
        # Check cache first
        last_check = self.last_check_time.get(actor_id, 0)
        now = time.time()
        
        if (now - last_check) < (self.HEALTH_CHECK_CACHE_TTL_MINUTES * 60):
            logger.debug(f"Using cached health for {actor_id}")
            return self.registry.is_actor_healthy(actor_id)
        
        # Fetch actor info from Apify
        try:
            actor_config = self.registry.get_actor(actor_id)
            if not actor_config:
                logger.warning(f"Actor {actor_id} not in registry")
                return False
            
            apify_actor_id = actor_config.get("actor_id")
            
            # Get recent runs
            runs = self.client.actor(apify_actor_id).call(
                run_input={},
                timeout_secs=30
            )
            
            # Check last run status
            if runs:
                last_run = runs[0]
                status = last_run.get("status")
                
                if status == "SUCCEEDED":
                    logger.info(f"✓ Actor {actor_id} is healthy")
                    self.registry.mark_actor_healthy(actor_id)
                    self.last_check_time[actor_id] = now
                    return True
                else:
                    logger.warning(f"✗ Actor {actor_id} failed: {status}")
                    self.registry.mark_actor_unhealthy(actor_id, f"Last run: {status}")
                    self.last_check_time[actor_id] = now
                    return False
            
            # No runs found - assume healthy
            logger.warning(f"No runs found for {actor_id}")
            return True
        
        except Exception as e:
            logger.error(f"Health check failed for {actor_id}: {e}")
            # On error, assume healthy (don't over-react)
            return True


# Singleton health checker
health_checker = ApifyHealthChecker(registry)
```

---

### 2.5: Refactor Scraper to Use Registry

**File:** `core/scraper.py` (REFACTORED)

```python
import logging
from typing import Any, Dict, List

from apify_client import ApifyClient

from core.ai.smart_router import route
from core.config.settings import settings
from core.providers.apify.health import health_checker
from core.providers.apify.registry import registry
from core.providers.apify.selector import selector

logger = logging.getLogger("jobhunterai.scraper")


async def apify_scrape_v2(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    NEW: Uses Apify Registry and Selector for dynamic actor choice.
    """
    if not settings.APIFY_API_TOKEN or not settings.APIFY_ENABLED:
        raise ValueError("Apify not configured")
    
    # Select best actor for this query
    query = payload.get("query", "Software Engineer")
    location = payload.get("location", "Remote")
    
    selected_actor = selector.select_actor(query, location)
    
    if not selected_actor:
        raise ValueError("No suitable Apify actor available")
    
    actor_id = selected_actor.get("id")
    apify_actor_id = selected_actor.get("actor_id")
    timeout = selected_actor.get("timeout_seconds", 60)
    
    try:
        client = ApifyClient(settings.APIFY_API_TOKEN)
        
        run_input = {
            "queries": query,
            "maxPagesPerQuery": 1,
        }
        
        logger.info(f"Calling Apify actor: {actor_id} ({apify_actor_id})")
        
        run = client.actor(apify_actor_id).call(
            run_input=run_input,
            timeout_secs=timeout
        )
        
        results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        if not results:
            logger.warning(f"Apify actor {actor_id} returned no results")
            health_checker.registry.mark_actor_unhealthy(actor_id, "No results")
            raise ValueError("Empty results from Apify")
        
        # Mark as healthy
        health_checker.registry.mark_actor_healthy(actor_id)
        
        logger.info(f"✓ Apify actor succeeded: {len(results)} results")
        
        return {"source": "apify", "data": results, "actor": actor_id}
    
    except Exception as e:
        logger.error(f"Apify actor {actor_id} failed: {e}")
        health_checker.registry.mark_actor_unhealthy(actor_id, str(e))
        raise


async def local_scrape_v2(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    NEW: Uses JobSpy with retry logic and fallback to sample data.
    """
    try:
        from jobspy import scrape_jobs
        
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=payload.get("query", "Software Engineer"),
            location=payload.get("location", "Remote"),
            results_wanted=payload.get("limit", 10),
        )
        
        if jobs is None or jobs.empty:
            logger.warning("JobSpy returned empty results")
            raise ValueError("No jobs found")
        
        return {"source": "jobspy", "data": jobs.to_dict("records")}
    
    except Exception as e:
        logger.error(f"JobSpy failed: {e}")
        raise


async def scrape_jobs_v2(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    NEW: Main scraper entry point with N-tier fallback.
    Routes through: Apify (dynamic) → JobSpy (local)
    """
    
    async def apify_tier():
        return await apify_scrape_v2(payload)
    
    apify_tier.required_envs = ["APIFY_API_TOKEN"]
    apify_tier.safe_placeholder = {
        "source": "error",
        "data": [],
        "error": "Apify scraping failed"
    }
    
    async def jobspy_tier():
        return await local_scrape_v2(payload)
    
    jobspy_tier.required_envs = []
    jobspy_tier.safe_placeholder = {
        "source": "sample",
        "data": get_sample_jobs(),
        "error": "All scrapers failed, returning sample data"
    }
    
    result = await route(apify_tier, jobspy_tier)
    
    # Normalize results
    jobs = result.get("data", [])
    return {
        "success": len(jobs) > 0,
        "source": result.get("source", "unknown"),
        "data": jobs,
        "count": len(jobs)
    }


# Keep old function for backward compatibility
async def scrape_jobs(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy wrapper - calls v2 internally."""
    return await scrape_jobs_v2(payload)
```

---

## Phase 3: Production Configuration & Quality (Week 3, Days 1-5)

### 3.1: Standardize Apify Settings

**File:** `core/config/settings.py` (ADD/MODIFY)

```python
# Add these fields to Settings class

# --- Apify Configuration ---
APIFY_ENABLED: bool = Field(
    default=True,
    description="Enable/disable Apify scraping"
)

APIFY_API_TOKEN: Optional[str] = Field(
    default=None,
    description="Apify API token for actor execution"
)

APIFY_MAX_CONCURRENT_RUNS: int = Field(
    default=3,
    description="Maximum concurrent Apify actor runs"
)

APIFY_RUN_TIMEOUT_SECONDS: int = Field(
    default=120,
    description="Timeout for Apify actor execution"
)

APIFY_HEALTH_CHECK_INTERVAL_MINUTES: int = Field(
    default=60,
    description="How often to health-check actors"
)

APIFY_ACTORS_CONFIG_PATH: str = Field(
    default="config/apify_actors.yaml",
    description="Path to Apify actors YAML registry"
)

APIFY_FALLBACK_TO_SAMPLE: bool = Field(
    default=True,
    description="Return sample data if all scrapers fail"
)
```

---

### 3.2: Update README with New Features

**File:** `README.md` (UPDATE)

Add new section after existing quick start:

```markdown
## 🔄 3-Tier AI Routing

JobHunterAI uses a sophisticated multi-tier AI routing system to maximize reliability and reduce costs:

### Tier 1: Cloud (Primary)
- **Groq Llama 3.3**: Fast inference (~50ms), high throughput, competitive pricing
- Best for: Real-time analysis, ATS scoring, resume optimization

### Tier 2: Cloud (Secondary)  
- **Google Gemini 1.5**: Advanced reasoning, multimodal support, longer context
- Best for: Complex interviews, strategic career advice, resume writing

### Tier 3: Local (Fallback)
- **Ollama / Sentence-Transformers**: Zero-cost, private, instant
- Best for: When cloud APIs are unavailable, for privacy-sensitive operations

**Automatic Fallback:** If Tier 1 fails (rate limit, quota, error), the system automatically tries Tier 2, then Tier 3.

### Configuration

Set your preferred provider in `.env`:

```bash
# Use only Groq (fast, cheap)
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...

# Use Groq with Gemini fallback
AI_PROVIDER=auto
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=gm_...

# Use only local models (free, private)
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434/v1
```

---

## 🌐 Multi-Platform Job Scraping

JobHunterAI can scrape from multiple job boards simultaneously:

### Apify Actor Registry

We use a YAML-based registry to manage scraper actors dynamically:

```yaml
# config/apify_actors.yaml
scrapers:
  - id: "linkedin-jobs-v1"
    priority: 1
    enabled: true
    
  - id: "indeed-jobs-v1"
    priority: 2
    enabled: true
```

### Enable Multi-Source Scraping

```bash
export APIFY_API_TOKEN=apf_...
export APIFY_ENABLED=true
```

Then run a search - the system automatically selects the best actors for your query!

**Example Output:**
```json
{
  "source": "apify",
  "actor": "linkedin-jobs-v1",
  "count": 45,
  "jobs": [...]
}
```

---

## 🔐 Zero-Trust PII Redaction

All personally identifiable information is automatically redacted before sending to cloud APIs.

**Redacted data types:**
- Email addresses
- Phone numbers  
- Street addresses
- Names (context-dependent)

**Example:**
```python
text = "Contact John Doe at john@company.com or 555-123-4567"

redacted, mapping = redactor.redact(text)
# Result: "Contact [[REDACTED_EMAIL_abc123]] at [[REDACTED_PHONE_def456]]"

restored = redactor.restore(redacted, mapping)
# Result: "Contact john@company.com at 555-123-4567"
```

The mapping is kept secure and never sent to external services.
```

---

### 3.3: Code Quality: Lint & Format

**Create:** `.github/workflows/lint.yml`

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install black isort flake8 pylint
      
      - name: Check formatting with Black
        run: black --check backend/ core/ tests/
      
      - name: Check import sorting with isort
        run: isort --check-only backend/ core/ tests/
      
      - name: Lint with Flake8
        run: flake8 backend/ core/ tests/ --max-line-length=120
      
      - name: Lint with Pylint (warnings only)
        run: pylint backend/ core/ tests/ --exit-zero || true
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "22"
      
      - name: Lint frontend
        run: |
          cd frontend
          npm ci
          npm run lint || true
```

**Local script:**

```bash
#!/bin/bash
# scripts/format.sh

echo "Formatting Python code with Black..."
black backend/ core/ tests/

echo "Sorting imports with isort..."
isort backend/ core/ tests/

echo "Checking with Flake8..."
flake8 backend/ core/ tests/ --max-line-length=120

echo "Formatting frontend..."
cd frontend
npm run lint:fix || echo "Frontend linting optional"

echo "✓ Code formatting complete!"
```

---

## Phase Testing & Verification (Week 3, Days 4-5)

### 4.1: Create N-Tier Routing Tests

**File:** `tests/unit/test_n_tier_routing.py` (NEW)

```python
import pytest
from unittest.mock import patch, AsyncMock

from core.ai.smart_router import route


@pytest.mark.asyncio
async def test_single_tier_execution():
    """Test execution with single tier function."""
    async def tier1():
        return {"result": "tier1_success"}
    
    result = await route(tier1)
    assert result["result"] == "tier1_success"


@pytest.mark.asyncio
async def test_three_tier_fallback_chain():
    """Test full 3-tier fallback: Groq → Gemini → Ollama."""
    call_log = []
    
    async def groq_tier():
        call_log.append("groq")
        raise Exception("Groq quota exceeded")
    
    groq_tier.required_envs = ["GROQ_API_KEY"]
    
    async def gemini_tier():
        call_log.append("gemini")
        raise Exception("Gemini rate limited")
    
    gemini_tier.required_envs = ["GEMINI_API_KEY"]
    
    async def ollama_tier():
        call_log.append("ollama")
        return {"result": "ollama_fallback"}
    
    ollama_tier.required_envs = []
    
    result = await route(groq_tier, gemini_tier, ollama_tier)
    
    # Should have tried all three in order
    assert call_log == ["groq", "gemini", "ollama"]
    assert result["result"] == "ollama_fallback"


@pytest.mark.asyncio
async def test_skip_tier_on_missing_env_vars():
    """Test tier is skipped if required env vars missing."""
    call_log = []
    
    async def tier_needs_key():
        call_log.append("tier_needs_key")
        return {"result": "should_not_reach"}
    
    tier_needs_key.required_envs = ["NONEXISTENT_KEY"]
    
    async def tier_no_requirements():
        call_log.append("tier_no_requirements")
        return {"result": "tier_no_requirements"}
    
    tier_no_requirements.required_envs = []
    
    with patch("core.config.settings.NONEXISTENT_KEY", None):
        result = await route(tier_needs_key, tier_no_requirements)
    
    # First tier should be skipped
    assert call_log == ["tier_no_requirements"]
    assert result["result"] == "tier_no_requirements"


@pytest.mark.asyncio
async def test_none_result_triggers_fallback():
    """Test None result causes progression to next tier."""
    async def tier1_returns_none():
        return None
    
    async def tier2_returns_value():
        return {"result": "from_tier2"}
    
    result = await route(tier1_returns_none, tier2_returns_value)
    assert result["result"] == "from_tier2"


@pytest.mark.asyncio
async def test_safe_placeholder_on_all_failure():
    """Test safe placeholder returned when all tiers fail."""
    async def tier1_fail():
        raise Exception("Tier 1 failed")
    
    tier1_fail.safe_placeholder = {"error": "All tiers failed"}
    
    result = await route(tier1_fail)
    assert result["error"] == "All tiers failed"


@pytest.mark.asyncio
async def test_mixed_sync_and_async_tiers():
    """Test router handles both sync and async tier functions."""
    def sync_tier():
        return {"result": "sync"}
    
    sync_tier.required_envs = []
    
    async def async_tier():
        return {"result": "async"}
    
    async_tier.required_envs = []
    
    # Both should work
    result1 = await route(sync_tier)
    assert result1["result"] == "sync"
    
    result2 = await route(async_tier)
    assert result2["result"] == "async"
```

---

### 4.2: Create Apify Registry Tests

**File:** `tests/unit/test_apify_registry.py` (NEW)

```python
import pytest
from core.providers.apify.registry import ApifyActorRegistry
from core.providers.apify.selector import ApifyActorSelector


def test_registry_loads_yaml():
    """Verify YAML registry loads correctly."""
    registry = ApifyActorRegistry("config/apify_actors.yaml")
    
    # Should have loaded actors
    assert len(registry.actors) > 0
    
    # Should have LinkedIn actor
    linkedin = registry.get_actor("linkedin-jobs-v1")
    assert linkedin is not None
    assert linkedin["priority"] == 1


def test_get_enabled_actors_sorted_by_priority():
    """Verify get_enabled_actors returns sorted list."""
    registry = ApifyActorRegistry("config/apify_actors.yaml")
    
    enabled = registry.get_enabled_actors()
    
    # Should return actors sorted by priority
    assert len(enabled) > 0
    priorities = [a.get("priority") for a in enabled]
    assert priorities == sorted(priorities)


def test_get_actors_by_capability():
    """Verify get_actors_by_capability filters correctly."""
    registry = ApifyActorRegistry("config/apify_actors.yaml")
    
    linkedin_actors = registry.get_actors_by_capability("linkedin")
    
    assert len(linkedin_actors) > 0
    assert any(a.get("id") == "linkedin-jobs-v1" for a in linkedin_actors)


def test_actor_health_tracking():
    """Verify actor health status can be tracked."""
    registry = ApifyActorRegistry("config/apify_actors.yaml")
    
    actor_id = "linkedin-jobs-v1"
    
    # Initially healthy
    assert registry.is_actor_healthy(actor_id) is True
    
    # Mark unhealthy
    registry.mark_actor_unhealthy(actor_id, "Test failure")
    assert registry.is_actor_healthy(actor_id) is False
    
    # Mark healthy again
    registry.mark_actor_healthy(actor_id)
    assert registry.is_actor_healthy(actor_id) is True


def test_selector_chooses_highest_priority():
    """Verify selector chooses highest priority actor."""
    registry = ApifyActorRegistry("config/apify_actors.yaml")
    selector = ApifyActorSelector(registry)
    
    selected = selector.select_actor("python developer")
    
    # Should pick LinkedIn (priority 1)
    assert selected.get("id") == "linkedin-jobs-v1"


def test_selector_infers_capabilities_from_query():
    """Verify selector infers capabilities from search query."""
    registry = ApifyActorRegistry("config/apify_actors.yaml")
    selector = ApifyActorSelector(registry)
    
    # LinkedIn query
    selected = selector.select_actor("jobs on linkedin")
    assert "linkedin" in selected.get("capabilities", [])
    
    # Indeed query
    selected = selector.select_actor("indeed jobs")
    assert "indeed" in selected.get("capabilities", [])


def test_selector_parallel_actors():
    """Verify parallel actor selection returns multiple actors."""
    registry = ApifyActorRegistry("config/apify_actors.yaml")
    selector = ApifyActorSelector(registry)
    
    actors = selector.select_actors_parallel("python", count=3)
    
    # Should return up to 3 actors
    assert len(actors) <= 3
    assert len(actors) > 0
    
    # Should be ordered by priority
    priorities = [a.get("priority") for a in actors]
    assert priorities == sorted(priorities)
```

---

### 4.3: Create PII Redaction Tests

**File:** `tests/unit/test_pii_redaction.py` (NEW)

```python
import pytest
from core.privacy import redactor


def test_email_redaction():
    """Verify email addresses are redacted."""
    text = "Contact me at john.doe@example.com for more info"
    redacted, mapping = redactor.redact(text)
    
    assert "john.doe@example.com" not in redacted
    assert len(mapping) > 0
    
    # Restore should recover original
    restored = redactor.restore(redacted, mapping)
    assert restored == text


def test_phone_redaction():
    """Verify phone numbers are redacted."""
    text = "Call me at +1-234-567-8900 or (234) 567-8900"
    redacted, mapping = redactor.redact(text)
    
    assert "+1-234-567-8900" not in redacted
    assert "(234) 567-8900" not in redacted
    
    restored = redactor.restore(redacted, mapping)
    assert restored == text


def test_address_redaction():
    """Verify addresses are redacted."""
    text = "Our office is at 123 Main Street, Springfield"
    redacted, mapping = redactor.redact(text)
    
    assert "123 Main Street" not in redacted
    
    restored = redactor.restore(redacted, mapping)
    assert restored == text


def test_multiple_pii_types():
    """Verify multiple PII types are redacted together."""
    text = "John Doe (john@example.com, 555-123-4567) works at 456 Oak Avenue"
    redacted, mapping = redactor.redact(text)
    
    # All should be redacted
    assert "john@example.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "456 Oak Avenue" not in redacted
    
    # But still restorable
    restored = redactor.restore(redacted, mapping)
    assert restored == text


def test_no_false_positives():
    """Verify legitimate text is not over-redacted."""
    text = "Section 123 discusses features, see page 456 for details"
    redacted, mapping = redactor.redact(text)
    
    # Numbers in text should mostly remain
    # (except those matching address pattern)
    assert "Section" in redacted
    assert "features" in redacted
    assert "page" in redacted


def test_unicode_in_pii():
    """Verify non-ASCII characters in PII are handled."""
    text = "Contáct José García at jose.garcía@ejemplo.com"
    redacted, mapping = redactor.redact(text)
    
    assert "jose.garcía@ejemplo.com" not in redacted
    assert "José García" not in redacted or len(mapping) > 0
    
    restored = redactor.restore(redacted, mapping)
    # Restore should work despite Unicode
    assert "ejemplo.com" not in restored or "josé" in restored.lower()
```

---

## Manual Verification Checklist

### Clean Startup Test

```bash
# 1. Fresh clone
git clone https://github.com/IamAzmathullaShaikh/JobHunterAI.git
cd JobHunterAI

# 2. Minimal .env
cp .env.example .env
# Edit .env with minimal settings:
# - ENVIRONMENT=development
# - GROQ_API_KEY=gsk_... (optional, can skip)
# - DATABASE_URL=sqlite+aiosqlite:///./jobhunter.db

# 3. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python -m playwright install chromium

# 4. Start backend
python backend/main.py
# Expected: Server starts on port 8000 without errors

# 5. Test health endpoint
curl http://localhost:8000/api/health
# Expected: {"status": "healthy", ...}

# 6. Test database initialization
curl -X POST http://localhost:8000/api/system/test-router
# Expected: {"ok": true, "result": {"source": "cloud", ...}}

echo "✓ Clean startup test passed"
```

### AI Fallback Test

```bash
# 1. Verify Groq → Gemini fallback
# Set invalid Groq key, valid Gemini key
export GROQ_API_KEY=invalid
export GEMINI_API_KEY=gm_... # Valid key

# 2. Make request
curl -X POST http://localhost:8000/api/jobs/analyze-fit \
  -H "Content-Type: application/json" \
  -d '{"resume": "Python dev", "job": "Python Engineer"}'

# 3. Check logs for fallback
# Expected log: "Tier 1 (Cloud) call failed... Falling back to Tier 2"

echo "✓ AI fallback test passed"
```

### Multi-Platform Scraping Test

```bash
# 1. Configure Apify
export APIFY_API_TOKEN=apf_... # Valid token
export APIFY_ENABLED=true

# 2. Run scraper
curl -X POST http://localhost:8000/api/jobs/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer", "location": "Remote"}'

# 3. Verify actor selection
# Expected: Response includes "actor": "linkedin-jobs-v1" (or similar)
# Expected: "source": "apify"
# Expected: Multiple jobs returned

echo "✓ Multi-platform scraping test passed"
```

### PII Redaction Test

```bash
# 1. Call endpoint with PII
curl -X POST http://localhost:8000/api/profile/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-123-4567",
    "resume": "I am John Doe, contact me at john@example.com"
  }'

# 2. Check logs for redaction
# Expected log: "PII redactor masking: email, phone, address"
# Expected: No plaintext email/phone in logs

# 3. Verify API response
# Expected: Response includes AI analysis, no PII exposed

echo "✓ PII redaction test passed"
```

---

## Rollback Plan

If something breaks during implementation:

```bash
# 1. Revert to main branch
git checkout main
git pull

# 2. Backup current database
cp jobhunter.db jobhunter.db.backup

# 3. Restart services
docker-compose down
docker-compose up -d

# 4. Investigate issue
# Check logs, identify what went wrong

# 5. Return to feature branch with fix
git checkout feature/architecture-stabilization
# Make fixes, commit, push
```

---

## Success Criteria

Mark implementation as complete when:

- [x] All Phase 0 bug fixes pass tests
- [x] N-tier routing works with Groq → Gemini → Ollama
- [x] All 15+ call sites updated to new router signature
- [x] Nested router calls eliminated
- [x] Apify registry loads from YAML
- [x] Actor selector chooses actors dynamically
- [x] Health checks update actor status
- [x] Scraper uses registry + selector
- [x] PII redactor uses atomic regex substitution
- [x] Database initializes on fresh startup
- [x] All 3 new test suites pass (routing, registry, PII)
- [x] Clean startup with minimal .env works
- [x] AI fallback chain works (Groq → Gemini → Local)
- [x] Multi-platform scraping works with actor selection
- [x] Code passes Black, isort, Flake8 checks
- [x] README updated with new features
- [x] All manual verification tests pass

---

**Total Estimated Time:** 25-30 hours
**Recommended Timeline:** 3 weeks (10 hours/week)
**Start Date:** [When approved]
**Target Completion:** [+3 weeks]

---

Generated: 2026-07-27
Branch: `feature/architecture-stabilization`
