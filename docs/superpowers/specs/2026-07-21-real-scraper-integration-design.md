# Real Scraper Integration + Job-Link Fix — Design

Date: 2026-07-21
Status: Approved

## Problem

Reported by the maintainer: "the scraped results links are not redirecting to
actual job posting which it did previously."

Root cause, in two layers:

1. **The TS app never scrapes.** `POST /api/scrape` in `server.ts` is labelled
   `// 3. simulated multi-engine scraping` and prompts Gemini to *fabricate* 10
   listings, explicitly instructing it to "mock this as canonical_url". The URLs
   are AI-hallucinated (e.g. `techcorp.com/jobs/1`) and never pointed to real
   postings.
2. **Recent "fix" commits actively corrupt the links.** Commit `562dd35`
   introduced a rewrite of any `google.com/search?q=` URL into a dead
   `resolved.com/...` domain (`server.ts:255-257`), stores `canonical_url` as
   `''` when the URL looks mock (`server.ts:272-283`), and the new `JobCard.tsx`
   runs a `fetch(HEAD, {mode:'no-cors'})` before opening — when that throws (as
   it does for fabricated/cross-origin domains) it opens a **Google search page
   instead of the job** (`src/components/JobCard.tsx:19-37`).

Meanwhile the repo already contains a **real** Python + Playwright scraper fleet
(`scrapers/manager.py` → `ScraperManager.run_all()`, 9 engines) that returns
genuine posting URLs, but it is not wired into the live Node app and its FastAPI
entry point imports a non-existent `jobhunterai_core.*` package.

## Goal

Make `POST /api/scrape` return **real** job listings with **real** posting URLs
by invoking the existing Python scraper fleet, and remove the frontend/backend
link-mangling so those URLs open directly. Never display fabricated data.

## Decisions (agreed)

- **Integration:** Node spawns a Python subprocess. Keeps one app and one data
  store (`database/db.json`). No SQLAlchemy/Postgres involved.
- **No fake data:** the Gemini simulation and the mock fallback listings are
  removed. When scrapers find nothing, return an honest empty result.
- **Link fix is in scope:** remove the `resolved.com` rewrite, the
  `canonical_url` blanking, and the `JobCard` HEAD-check + Google fallback.

## Architecture

```
Browser ──POST /api/scrape──▶ server.ts
                                  │  spawn('python3', ['scripts/scrape_cli.py', --json])
                                  ▼
                        scripts/scrape_cli.py
                                  │  ScraperManager().run_all(query, location, limit, job_type)
                                  ▼
                        9 Playwright scrapers (scrapers/*.py)
                                  │  JSON array on stdout (logs → stderr)
                                  ▼
                        server.ts maps → db.json, dedups, saves
```

### Python CLI: `scripts/scrape_cli.py`
- Reads params from a single JSON object on **stdin**:
  `{search_query, location, job_type, limit}`.
- Instantiates `ScraperManager()` with **no** DB session (scraping needs none)
  and calls `run_all(...)`.
- Serialises each `JobListingCreate` to a plain dict and writes a **JSON array
  to stdout**. `date_posted` is emitted as ISO string or `null`.
- Configures `loguru` to write to **stderr** only, so stdout is pure JSON.
- Exit code `0` on success (including zero results), non-zero on hard failure.

### TS endpoint: `POST /api/scrape` (`server.ts`)
- Replace the Gemini block entirely with a `spawnScraper(params)` helper that:
  - Spawns `python3 scripts/scrape_cli.py`, writes params JSON to stdin.
  - Collects stdout, enforces a **120s timeout** (kill + reject on overrun).
  - On non-zero exit or unparseable stdout → throw (endpoint returns `502`).
- Map each scraped job into the existing `db.json` job shape, dedup, save.

## Data mapping (Python job → db.json job)

| db.json field     | source                                  |
|-------------------|-----------------------------------------|
| `job_id_raw`      | `job_id_raw`                            |
| `portal_id`       | `job_id_raw`                            |
| `title`, `company_name`, `location`, `work_place_type`, `job_type`, `source` | pass-through |
| `url`             | scraped `url` (real posting)            |
| `raw_url`         | scraped `url`                           |
| `canonical_url`   | scraped `url`                           |
| `needs_validation`| `false`                                 |
| `description_raw`, `description_clean`, `salary_*`, `date_posted` | pass-through |
| `id`              | max(existing ids)+1 (existing logic)    |
| `is_starred`      | `false`                                 |
| `date_scraped`    | `new Date().toISOString()`              |
| `ai_analysis`, `application` | `null`                       |

Dedup key: keep the existing `job_id_raw`-based skip plus the
`title::company::location` fingerprint already present in `server.ts`.

## Frontend link fix (`src/components/JobCard.tsx`)

- `const linkToOpen = job.canonical_url || job.url || job.raw_url;`
- Render an anchor: `<a href={linkToOpen} target="_blank" rel="noopener noreferrer">Open Job</a>`.
- **Remove** the `useState(checking)`, the `fetch(HEAD)` call, the
  `.includes('mock')` branch, the Google-search fallback, and the
  `console.log('RENDER_JOB', job)`.
- If `linkToOpen` is falsy, render the button disabled with an "Link
  unavailable" title instead of a working anchor.

## Runtime / dependencies

- Requires `python3`, `pip install -r requirements.txt`, and
  `playwright install chromium`.
- `Dockerfile`: add a Python install layer + `playwright install --with-deps
  chromium` so the container can run the fleet.
- **Preflight:** if `python3` is not found, `/api/scrape` returns a `500` with a
  clear message explaining the setup step, rather than an opaque spawn error.

## Error handling

| Condition                         | Response                                   |
|-----------------------------------|--------------------------------------------|
| Subprocess non-zero / bad JSON    | `502` + message, no fake data              |
| Zero listings                     | `200`, `new_count: 0`, "no new roles found"|
| Individual scraper throws         | swallowed inside `run_all` (returns `[]`)  |
| Subprocess exceeds 120s           | kill process, `502` timeout message        |
| `python3` missing                 | `500` setup-required message               |

## Testing & verification

- **Node mapping/dedup unit test**: stub the subprocess to emit a fixed JSON
  array; assert `db.json` receives correctly-mapped jobs and dedups repeats.
  Deterministic, no network.
- **JobCard test**: assert the anchor `href` equals the real URL and that no
  Google-search fallback path exists; disabled state when no URL.
- **Python CLI test**: run `scrape_cli.py` with a stubbed `ScraperManager`
  (monkeypatched `run_all`) and assert clean JSON on stdout, logs on stderr.
- **Honest caveat:** live scraping of LinkedIn/Indeed/etc. depends on network
  reachability and anti-bot defences; from a sandboxed CI/dev environment those
  sites may be blocked, so real listings are not guaranteed *there*. The
  plumbing and the link fix are fully testable offline; real-world yield is
  verified on the maintainer's machine. Verification steps documented in README.

## Out of scope

- Fixing the broken FastAPI `jobhunterai_core.*` imports (separate service path
  we are not using).
- The SQLAlchemy/Postgres persistence layer.
- Proxy/anti-bot hardening of individual scrapers.
