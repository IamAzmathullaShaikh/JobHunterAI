# 3-Week Execution Plan: Full Architecture Stabilization

**Start Date:** 2026-07-27  
**Target Completion:** 2026-08-17  
**Total Effort:** 25-30 hours  
**Team:** 1 Developer  

---

## Week 1: Foundation & Bug Fixes (Hours 1-10)

### Days 1-2: Phase 0 Critical Fixes (6-8 hours)

**Goal:** Stabilize foundation so existing code works properly.

#### Task 0.1: Database Initialization Fix
- **Time:** 2 hours
- **Files:** `core/lifecycle.py`, `core/database/connection.py`
- **Steps:**
  1. Add `Base.metadata.create_all()` call in `AppLifecycleManager.startup()`
  2. Add Alembic migration runner
  3. Test fresh database creation
- **Verification:** `pytest tests/unit/test_database_init.py`

#### Task 0.2: Environment Variable Validation Fix
- **Time:** 2 hours
- **Files:** `core/ai/smart_router.py` (update `_check_required_envs`)
- **Steps:**
  1. Add `_is_api_key_set()` helper function
  2. Fix falsy value detection (None vs empty string)
  3. Update logger messages
- **Verification:** `pytest tests/unit/test_settings_validation.py`

#### Task 0.3: PII Redactor Hardening
- **Time:** 2-3 hours
- **Files:** `core/privacy.py`
- **Steps:**
  1. Replace `.replace()` with `re.sub()` + callback
  2. Add UUID for collision prevention
  3. Add comprehensive pattern testing
- **Verification:** `pytest tests/unit/test_pii_redaction.py`

**End of Day 2:** All Phase 0 tests passing ✓

---

### Days 3-5: Phase 1 Smart Router Refactor (4-5 hours)

**Goal:** Implement N-tier routing foundation.

#### Task 1.1: Refactor core/ai/smart_router.py
- **Time:** 2.5 hours
- **Steps:**
  1. Rewrite `route()` to accept `*tier_functions`
  2. Implement `_check_required_envs()` logic
  3. Add `_is_api_key_set()` helper
  4. Add comprehensive logging
- **Verification:** `pytest tests/unit/test_n_tier_routing.py -v`

#### Task 1.2: Create Router Tests
- **Time:** 1.5 hours
- **Steps:**
  1. Write `tests/unit/test_n_tier_routing.py` (8 test cases)
  2. Run full test suite
  3. Verify all tests pass
- **Verification:** `pytest tests/unit/test_n_tier_routing.py -v`

#### Task 1.3: Document Breaking Changes
- **Time:** 1 hour
- **Steps:**
  1. Create `BREAKING_CHANGES.md` with migration guide
  2. List all files needing updates
  3. Show before/after examples

**End of Week 1:** 
- ✅ Database initializes on startup
- ✅ Environment validation fixed
- ✅ PII redactor atomic
- ✅ N-tier router implemented & tested
- ⏳ Call sites still need updating (start Week 2)

---

## Week 2: Router Migration & Apify Registry (Hours 11-20)

### Days 1-3: Update All Router Call Sites (6-7 hours)

**Goal:** Convert all existing `route(primary, fallback)` calls to N-tier.

#### Task 2.1: Update LLM Client (1 hour)
- **File:** `core/ai/llm_client.py`
- **Current:**
  ```python
  return await route(try_primary, try_fallback)
  ```
- **New:**
  ```python
  return await route(groq_tier, gemini_tier, ollama_tier)
  ```
- **Verification:** `pytest tests/unit/test_llm_client.py`

#### Task 2.2: Update Matcher (1 hour)
- **File:** `core/ai/matcher.py`
- **Changes:** Remove nested `route()` calls, flatten to single routing level
- **Verification:** `pytest tests/unit/test_matcher.py`

#### Task 2.3: Update Generator (0.5 hours)
- **File:** `core/ai/generator.py`
- **Changes:** Add Gemini/Ollama tier to cover letter generation

#### Task 2.4: Update Resume Parser (0.5 hours)
- **File:** `core/ai/resume_parser.py`
- **Changes:** Add local fallback tier

#### Task 2.5: Update Resume Engine (0.5 hours)
- **File:** `core/resume_engine.py`
- **Changes:** Multi-tier bullet optimization

#### Task 2.6: Update Task Engine (2 hours)
- **File:** `core/task_engine.py` (8+ methods to update)
- **Critical:** Remove nested `JobMatcher.analyze_fit()` calls
- **Changes:** Direct tier functions instead of intermediate classes

#### Task 2.7: Update Other Modules (1 hour)
- **Files:** `core/scraper.py`, `core/enricher.py`, `backend/api/system.py`
- **Changes:** Standardize all `route()` calls

**Checkpoint: Run full test suite**
```bash
pytest tests/unit/ -v
```

**End of Day 3:** All router call sites updated and tested ✓

---

### Days 4-5: Apify Registry Setup (3-4 hours)

**Goal:** Implement YAML-based actor registry.

#### Task 3.1: Create YAML Registry (0.5 hours)
- **File:** `config/apify_actors.yaml`
- **Steps:**
  1. Create from template in checklist
  2. Verify YAML syntax
  3. Add 3-4 actor definitions
- **Verification:** `python -c "import yaml; yaml.safe_load(open('config/apify_actors.yaml'))"`

#### Task 3.2: Implement Registry Loader (1 hour)
- **File:** `core/providers/apify/registry.py` (NEW)
- **Steps:**
  1. Create `ApifyActorRegistry` class
  2. Implement YAML loading
  3. Add actor lookup methods
  4. Add health tracking
- **Verification:** `pytest tests/unit/test_apify_registry.py::test_registry_loads_yaml`

#### Task 3.3: Implement Actor Selector (1 hour)
- **File:** `core/providers/apify/selector.py` (NEW)
- **Steps:**
  1. Create `ApifyActorSelector` class
  2. Implement priority-based selection
  3. Add capability inference from query
  4. Add parallel actor selection
- **Verification:** `pytest tests/unit/test_apify_registry.py::test_selector_*`

#### Task 3.4: Implement Health Checker (1 hour)
- **File:** `core/providers/apify/health.py` (NEW)
- **Steps:**
  1. Create `ApifyHealthChecker` class
  2. Implement actor health checks
  3. Add caching (5 min TTL)
  4. Integrate with registry
- **Verification:** `pytest tests/unit/test_apify_registry.py::test_actor_health_tracking`

**End of Week 2:**
- ✅ All 15+ router call sites updated
- ✅ Router tests all passing
- ✅ YAML registry created & loaded
- ✅ Actor selector working
- ✅ Health checker implemented
- ⏳ Scraper refactor pending (start Week 3)

---

## Week 3: Apify Integration & Polish (Hours 21-30)

### Days 1-2: Refactor Scraper & Tests (5-6 hours)

**Goal:** Integrate registry into job scraping.

#### Task 4.1: Refactor Scraper (2 hours)
- **File:** `core/scraper.py`
- **Steps:**
  1. Create `apify_scrape_v2()` using registry + selector
  2. Create `scrape_jobs_v2()` with N-tier routing
  3. Keep old function for backward compatibility
  4. Update tests
- **Verification:** Manual test scraping

#### Task 4.2: Create Complete Test Suite (2 hours)
- **Files:** 
  - `tests/unit/test_n_tier_routing.py` (if not done)
  - `tests/unit/test_apify_registry.py` (if not done)
  - `tests/unit/test_pii_redaction.py` (if not done)
- **Steps:**
  1. Implement all test cases from checklist
  2. Run full coverage report
  3. Aim for 80%+ coverage
- **Verification:** `pytest tests/ -v --cov`

#### Task 4.3: Manual Testing (1-2 hours)
- **Steps:**
  1. Fresh clone test
  2. Clean startup test
  3. AI fallback test (Groq → Gemini → Local)
  4. Multi-platform scraping test
  5. PII redaction test
- **Verification:** All manual tests pass ✓

**End of Day 2:** All integration complete and tested ✓

---

### Days 3-5: Documentation & Deployment (4-5 hours)

**Goal:** Prepare for production release.

#### Task 5.1: Update Configuration (1 hour)
- **File:** `core/config/settings.py`
- **Steps:**
  1. Add Apify settings fields
  2. Add validation for Apify config
  3. Document all new settings
- **Verification:** `pytest tests/unit/test_config_validation.py`

#### Task 5.2: Update Documentation (1.5 hours)
- **Files:** `README.md`, `docs/`
- **Steps:**
  1. Add 3-Tier AI Routing section
  2. Add Multi-Platform Scraping section
  3. Add PII Redaction section
  4. Add configuration examples
  5. Update quick start guide
- **Verification:** Manual review

#### Task 5.3: Code Quality (1 hour)
- **Steps:**
  1. Run `black` formatter
  2. Run `isort` import sorter
  3. Run `flake8` linter
  4. Fix any issues
- **Commands:**
  ```bash
  black backend/ core/ tests/
  isort backend/ core/ tests/
  flake8 backend/ core/ tests/ --max-line-length=120
  ```

#### Task 5.4: Create CI/CD Workflow (1 hour)
- **File:** `.github/workflows/lint.yml`
- **Steps:**
  1. Create GitHub Actions workflow
  2. Add Black, isort, Flake8 checks
  3. Add pytest tests
  4. Add frontend linting
- **Verification:** Push to GitHub and verify workflow runs

#### Task 5.5: Final Verification & Merge (0.5-1 hour)
- **Steps:**
  1. Verify all tests pass
  2. Verify CI/CD passes
  3. Create pull request
  4. Self-review PR
  5. Merge to main
- **Verification:** All GitHub checks pass ✓

**End of Week 3:**
- ✅ All code updated and working
- ✅ All tests passing (80%+ coverage)
- ✅ Documentation complete
- ✅ Code quality verified
- ✅ CI/CD configured
- ✅ Ready for production release 🚀

---

## Daily Standup Template

Use this to track progress:

```markdown
## Day X.Y: [Task Name]

### ✅ Completed
- [ ] Task 1: Description
- [ ] Task 2: Description

### 🔄 In Progress
- [ ] Task 3: Description (50%)

### ⏳ Blocked
- [ ] Task 4: Description (depends on Task X)

### 🔗 Dependencies
- Waiting for: [Thing]
- Blocking: [Thing]

### 📊 Status
- Lines of code changed: XXX
- Tests written: X
- Tests passing: X/Y

### 🐛 Issues Found
- Issue: [Description]
- Solution: [Action taken]
```

---

## Success Metrics

### Code Quality
- [ ] 80%+ test coverage
- [ ] All tests passing
- [ ] Black format passes
- [ ] No Flake8 errors (except long URLs)
- [ ] Pylint score > 8.0

### Functionality
- [ ] Database auto-initializes on fresh startup
- [ ] 3-Tier routing works (Groq → Gemini → Ollama)
- [ ] Apify registry loads from YAML
- [ ] Actor selector chooses dynamically
- [ ] Health checks update status
- [ ] PII redaction is atomic
- [ ] All manual tests pass

### Documentation
- [ ] README updated with new features
- [ ] All new modules have docstrings
- [ ] Configuration examples provided
- [ ] Breaking changes documented

### Production Ready
- [ ] No console errors on clean startup
- [ ] All API endpoints functional
- [ ] Database schema created properly
- [ ] Logging is comprehensive
- [ ] Error handling is graceful

---

## Contingency Planning

### If stuck on a task:

1. **Quick wins first** — Skip blocking task, move to next
2. **Reduce scope** — Do MVP version, leave polish for later
3. **Ask for help** — Post in GitHub Discussions
4. **Rollback** — Revert to main, start fresh if needed

### Risk mitigation:

- **Backup database** before any migration
- **Test locally** before pushing to GitHub
- **Run tests** after every file change
- **Commit frequently** (every 1-2 hours)

---

## Time Tracking

| Phase | Task | Estimated | Actual | Status |
|-------|------|-----------|--------|--------|
| 0 | Database init | 2h | - | ⏳ |
| 0 | Env validation | 2h | - | ⏳ |
| 0 | PII hardening | 2-3h | - | ⏳ |
| 1 | Router refactor | 2.5h | - | ⏳ |
| 1 | Router tests | 1.5h | - | ⏳ |
| 1 | Migration guide | 1h | - | ⏳ |
| 2 | Update call sites | 6-7h | - | ⏳ |
| 3 | Registry setup | 3-4h | - | ⏳ |
| 4 | Scraper + tests | 5-6h | - | ⏳ |
| 5 | Docs + deployment | 4-5h | - | ⏳ |
| **Total** | | **25-30h** | - | ⏳ |

---

## Getting Started

### Right Now:

```bash
# 1. Switch to feature branch
git checkout feature/architecture-stabilization
git pull

# 2. Read the checklist
cat IMPLEMENTATION_CHECKLIST.md

# 3. Start Phase 0 Task 0.1
# Follow the code examples in the checklist

# 4. Commit early and often
git add core/lifecycle.py
git commit -m "fix: database initialization on startup"
git push
```

### Track progress:

- Update this file daily with actual times
- Keep a session log: what you did, what worked, what didn't
- Share blockers early

---

**Let's build something great! 🚀**
