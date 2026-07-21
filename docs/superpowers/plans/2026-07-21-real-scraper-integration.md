# Real Scraper Integration + Job-Link Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `POST /api/scrape` return real job listings with real posting URLs by invoking the existing Python/Playwright scraper fleet via a subprocess, and remove the frontend/backend link-mangling so those URLs open directly. Never display fabricated data.

**Architecture:** Node's `/api/scrape` spawns `python3 scripts/scrape_cli.py`, passing search params as JSON on stdin. The Python CLI runs `ScraperManager.run_all()` and prints a JSON array of real listings on stdout (logs on stderr). Node maps those into the existing `database/db.json` shape, dedups, and saves. The React `JobCard` renders a plain anchor to the real URL.

**Tech Stack:** Node 20 + Express + TypeScript (tsx), React 18 + Vite, Vitest (jsdom); Python 3 + Playwright scrapers; stdlib `unittest` for Python tests.

## Global Constraints

- No fabricated/AI-mock job data anywhere in the scrape path. Empty results must render honestly.
- Python subprocess stdout must be **pure JSON**; all Python logging goes to **stderr**.
- Node must never crash on scraper failure — return `502` (subprocess/JSON error), `500` (python missing), `400` (bad request), or `200` with `new_count: 0`.
- Follow existing repo commit convention: `type(scope): description`.
- TS files use ESM (`"type": "module"`); relative imports need explicit paths.
- Preserve the existing `db.json` job shape and the `job_id_raw` + `title::company::location` dedup fingerprint already used in `server.ts`.

---

### Task 1: Scraper bridge — pure mapping + dedup

**Files:**
- Create: `src/server/scraperBridge.ts`
- Test: `tests/server/scraperBridge.test.ts`

**Interfaces:**
- Produces:
  - `interface ScrapedJob { job_id_raw: string; title: string; company_name: string; location: string; work_place_type?: string; job_type: string; source: string; url: string; description_raw: string; description_clean?: string | null; salary_min?: number | null; salary_max?: number | null; salary_currency?: string | null; date_posted?: string | null; }`
  - `interface ScrapeParams { search_query: string; location: string; job_type: string; limit: number; }`
  - `function mapScrapedJob(item: ScrapedJob, id: number): any`
  - `function buildNewJobs(scraped: ScrapedJob[], existingJobs: any[]): any[]`

- [ ] **Step 1: Write the failing test**

Create `tests/server/scraperBridge.test.ts`:

```ts
import { describe, test, expect } from 'vitest';
import { mapScrapedJob, buildNewJobs, ScrapedJob } from '../../src/server/scraperBridge';

const base: ScrapedJob = {
  job_id_raw: 'li-1',
  title: 'Backend Engineer',
  company_name: 'Acme',
  location: 'Remote',
  work_place_type: 'Remote',
  job_type: 'Full-Time',
  source: 'LinkedIn',
  url: 'https://www.linkedin.com/jobs/view/li-1',
  description_raw: 'Build things',
};

test('mapScrapedJob binds the real url to url/raw_url/canonical_url', () => {
  const j = mapScrapedJob(base, 7);
  expect(j.id).toBe(7);
  expect(j.url).toBe(base.url);
  expect(j.raw_url).toBe(base.url);
  expect(j.canonical_url).toBe(base.url);
  expect(j.portal_id).toBe('li-1');
  expect(j.needs_validation).toBe(false);
  expect(j.is_starred).toBe(false);
  expect(j.ai_analysis).toBeNull();
});

test('buildNewJobs assigns incrementing ids from existing max', () => {
  const existing = [{ id: 4, job_id_raw: 'old', title: 'x', company_name: 'y', location: 'z' }];
  const out = buildNewJobs([base], existing);
  expect(out).toHaveLength(1);
  expect(out[0].id).toBe(5);
});

test('buildNewJobs skips items already in db (by job_id_raw) and by fingerprint', () => {
  const existingById = [{ id: 1, job_id_raw: 'li-1', title: 'other', company_name: 'other', location: 'other' }];
  expect(buildNewJobs([base], existingById)).toHaveLength(0);
  const existingByFp = [{ id: 1, job_id_raw: 'diff', title: 'Backend Engineer', company_name: 'Acme', location: 'Remote' }];
  expect(buildNewJobs([base], existingByFp)).toHaveLength(0);
});

test('buildNewJobs drops in-batch duplicates and items missing url or id', () => {
  const dupe = { ...base };
  const noUrl = { ...base, job_id_raw: 'li-2', url: '' };
  const noId = { ...base, job_id_raw: '', url: 'https://x/y' };
  const out = buildNewJobs([base, dupe, noUrl, noId], []);
  expect(out).toHaveLength(1);
  expect(out[0].job_id_raw).toBe('li-1');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run tests/server/scraperBridge.test.ts`
Expected: FAIL — cannot find module `../../src/server/scraperBridge`.

- [ ] **Step 3: Write minimal implementation**

Create `src/server/scraperBridge.ts`:

```ts
export interface ScrapedJob {
  job_id_raw: string;
  title: string;
  company_name: string;
  location: string;
  work_place_type?: string;
  job_type: string;
  source: string;
  url: string;
  description_raw: string;
  description_clean?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency?: string | null;
  date_posted?: string | null;
}

export interface ScrapeParams {
  search_query: string;
  location: string;
  job_type: string;
  limit: number;
}

function fingerprint(title?: string, company?: string, location?: string): string {
  const norm = (s?: string) => (s || '').toLowerCase().trim();
  return `${norm(title)}::${norm(company)}::${norm(location)}`;
}

export function mapScrapedJob(item: ScrapedJob, id: number): any {
  return {
    id,
    job_id_raw: item.job_id_raw,
    portal_id: item.job_id_raw,
    title: item.title,
    company_name: item.company_name,
    location: item.location,
    work_place_type: item.work_place_type || 'Onsite',
    job_type: item.job_type || 'Full-Time',
    source: item.source,
    url: item.url,
    raw_url: item.url,
    canonical_url: item.url,
    needs_validation: false,
    description_raw: item.description_raw,
    description_clean: item.description_clean ?? null,
    salary_min: item.salary_min ?? null,
    salary_max: item.salary_max ?? null,
    salary_currency: item.salary_currency ?? null,
    date_posted: item.date_posted ?? null,
    is_starred: false,
    date_scraped: new Date().toISOString(),
    ai_analysis: null,
    application: null,
  };
}

export function buildNewJobs(scraped: ScrapedJob[], existingJobs: any[]): any[] {
  const existingIds = new Set(existingJobs.map((j) => j.job_id_raw));
  const existingFps = new Set(existingJobs.map((j) => fingerprint(j.title, j.company_name, j.location)));
  const seenIds = new Set<string>();
  const seenFps = new Set<string>();
  let maxId = existingJobs.length > 0 ? Math.max(...existingJobs.map((j) => j.id)) : 0;

  const newJobs: any[] = [];
  for (const item of scraped) {
    if (!item.job_id_raw || !item.url) continue;
    const fp = fingerprint(item.title, item.company_name, item.location);
    if (existingIds.has(item.job_id_raw) || existingFps.has(fp)) continue;
    if (seenIds.has(item.job_id_raw) || seenFps.has(fp)) continue;
    seenIds.add(item.job_id_raw);
    seenFps.add(fp);
    maxId += 1;
    newJobs.push(mapScrapedJob(item, maxId));
  }
  return newJobs;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run tests/server/scraperBridge.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/server/scraperBridge.ts tests/server/scraperBridge.test.ts
git commit -m "feat(scraper): add pure mapping and dedup for scraped jobs"
```

---

### Task 2: Scraper bridge — subprocess runner

**Files:**
- Modify: `src/server/scraperBridge.ts` (append)
- Create: `tests/fixtures/stub_ok.py`, `tests/fixtures/stub_badjson.py`, `tests/fixtures/stub_fail.py`, `tests/fixtures/stub_sleep.py`
- Test: `tests/server/runScraper.test.ts`

**Interfaces:**
- Consumes: `ScrapedJob`, `ScrapeParams`, `buildNewJobs` (Task 1)
- Produces:
  - `interface RunScraperOpts { python?: string; script?: string; timeoutMs?: number; }`
  - `function runScraper(params: ScrapeParams, opts?: RunScraperOpts): Promise<ScrapedJob[]>`
  - `async function discoverAndBuild(params: ScrapeParams, existingJobs: any[], opts?: RunScraperOpts): Promise<any[]>`

- [ ] **Step 1: Write the failing test**

Create the fixtures first.

`tests/fixtures/stub_ok.py`:
```python
import sys, json
params = json.loads(sys.stdin.read() or "{}")
sys.stderr.write("stub log line\n")
print(json.dumps([{
    "job_id_raw": "stub-1",
    "title": "Stub Engineer " + params.get("search_query", ""),
    "company_name": "StubCo",
    "location": params.get("location", "Remote"),
    "work_place_type": "Remote",
    "job_type": params.get("job_type", "Full-Time"),
    "source": "LinkedIn",
    "url": "https://example.com/jobs/stub-1",
    "description_raw": "desc",
    "date_posted": None
}]))
```

`tests/fixtures/stub_badjson.py`:
```python
print("this is not json")
```

`tests/fixtures/stub_fail.py`:
```python
import sys
sys.stderr.write("boom\n")
sys.exit(1)
```

`tests/fixtures/stub_sleep.py`:
```python
import time
time.sleep(5)
print("[]")
```

Create `tests/server/runScraper.test.ts`:
```ts
import { describe, test, expect } from 'vitest';
import path from 'path';
import { runScraper, discoverAndBuild } from '../../src/server/scraperBridge';

const fx = (name: string) => path.join(process.cwd(), 'tests', 'fixtures', name);
const params = { search_query: 'python', location: 'Remote', job_type: 'Full-Time', limit: 10 };

test('runScraper passes params on stdin and parses stdout JSON', async () => {
  const jobs = await runScraper(params, { script: fx('stub_ok.py') });
  expect(jobs).toHaveLength(1);
  expect(jobs[0].title).toContain('python');
  expect(jobs[0].url).toBe('https://example.com/jobs/stub-1');
});

test('runScraper rejects on non-zero exit', async () => {
  await expect(runScraper(params, { script: fx('stub_fail.py') })).rejects.toThrow(/exited 1/);
});

test('runScraper rejects on invalid JSON', async () => {
  await expect(runScraper(params, { script: fx('stub_badjson.py') })).rejects.toThrow(/JSON/i);
});

test('runScraper rejects with ENOENT when python is missing', async () => {
  await expect(
    runScraper(params, { python: 'no-such-python-xyz', script: fx('stub_ok.py') })
  ).rejects.toMatchObject({ code: 'ENOENT' });
});

test('runScraper rejects on timeout', async () => {
  await expect(
    runScraper(params, { script: fx('stub_sleep.py'), timeoutMs: 200 })
  ).rejects.toThrow(/timed out/i);
});

test('discoverAndBuild maps stub output into db shape', async () => {
  const out = await discoverAndBuild(params, [], { script: fx('stub_ok.py') });
  expect(out).toHaveLength(1);
  expect(out[0].canonical_url).toBe('https://example.com/jobs/stub-1');
  expect(out[0].id).toBe(1);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run tests/server/runScraper.test.ts`
Expected: FAIL — `runScraper`/`discoverAndBuild` not exported.

- [ ] **Step 3: Write minimal implementation**

Append to `src/server/scraperBridge.ts`:
```ts
import { spawn } from 'child_process';
import path from 'path';

export interface RunScraperOpts {
  python?: string;
  script?: string;
  timeoutMs?: number;
}

export function runScraper(params: ScrapeParams, opts: RunScraperOpts = {}): Promise<ScrapedJob[]> {
  const python = opts.python || process.env.PYTHON_BIN || 'python3';
  const script = opts.script || path.join(process.cwd(), 'scripts', 'scrape_cli.py');
  const timeoutMs = opts.timeoutMs ?? 120000;

  return new Promise((resolve, reject) => {
    const child = spawn(python, [script], { stdio: ['pipe', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    let settled = false;

    const timer = setTimeout(() => {
      settled = true;
      child.kill('SIGKILL');
      reject(new Error('Scraper timed out'));
    }, timeoutMs);

    child.stdout.on('data', (d) => { out += d.toString(); });
    child.stderr.on('data', (d) => { err += d.toString(); });

    child.on('error', (e) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(e);
    });

    child.on('close', (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (code !== 0) {
        reject(new Error(`Scraper exited ${code}: ${err.slice(-500)}`));
        return;
      }
      try {
        resolve(JSON.parse(out || '[]'));
      } catch (e) {
        reject(new Error(`Bad scraper JSON: ${(e as Error).message}`));
      }
    });

    child.stdin.write(JSON.stringify(params));
    child.stdin.end();
  });
}

export async function discoverAndBuild(
  params: ScrapeParams,
  existingJobs: any[],
  opts?: RunScraperOpts
): Promise<any[]> {
  const scraped = await runScraper(params, opts);
  return buildNewJobs(scraped, existingJobs);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run tests/server/runScraper.test.ts`
Expected: PASS (6 tests). Requires `python3` on PATH (present in dev/CI).

- [ ] **Step 5: Commit**

```bash
git add src/server/scraperBridge.ts tests/server/runScraper.test.ts tests/fixtures/
git commit -m "feat(scraper): spawn python scraper subprocess with timeout and error handling"
```

---

### Task 3: Python scrape CLI

**Files:**
- Create: `scripts/scrape_cli.py`
- Test: `tests/scripts/test_scrape_cli.py`

**Interfaces:**
- Reads a JSON object on stdin: `{search_query, location, job_type, limit}`.
- Writes a JSON array of job dicts on stdout; logs on stderr; exit 0 on success.
- Produces (module-level, for tests): `_serialize(job)`, `main()`.

- [ ] **Step 1: Write the failing test**

Create `tests/scripts/test_scrape_cli.py`:
```python
import io
import json
import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts import scrape_cli  # noqa: E402


class SerializeTest(unittest.TestCase):
    def test_serialize_converts_date_posted_to_iso(self):
        class Fake:
            def model_dump(self):
                return {"title": "X", "date_posted": datetime(2026, 7, 21, 9, 0, 0)}
        out = scrape_cli._serialize(Fake())
        self.assertEqual(out["date_posted"], "2026-07-21T09:00:00")

    def test_serialize_handles_none_date(self):
        class Fake:
            def model_dump(self):
                return {"title": "X", "date_posted": None}
        out = scrape_cli._serialize(Fake())
        self.assertIsNone(out["date_posted"])


class MainEmptyQueryTest(unittest.TestCase):
    def test_empty_query_prints_empty_array_without_scraping(self):
        old_in, old_out = sys.stdin, sys.stdout
        sys.stdin = io.StringIO(json.dumps({"search_query": ""}))
        sys.stdout = io.StringIO()
        try:
            scrape_cli.main()
            printed = sys.stdout.getvalue()
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        self.assertEqual(json.loads(printed), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.scripts.test_scrape_cli -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.scrape_cli'` (and missing `tests/scripts/__init__.py`, `scripts/__init__.py`).

- [ ] **Step 3: Write minimal implementation**

Create empty `scripts/__init__.py` and `tests/scripts/__init__.py`.

Create `scripts/scrape_cli.py`:
```python
#!/usr/bin/env python3
"""CLI bridge for the Node server.

Reads a JSON object on stdin: {search_query, location, job_type, limit}.
Runs the real scraper fleet and prints a JSON array of listings on stdout.
All logging goes to stderr so stdout stays pure JSON.
"""
import os
import sys
import json
import asyncio

# Ensure the repo root is importable so `import scrapers...` resolves.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _configure_logging():
    try:
        from loguru import logger
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    except ImportError:
        pass


def _serialize(job):
    data = job.model_dump() if hasattr(job, "model_dump") else dict(job)
    posted = data.get("date_posted")
    if posted is not None and hasattr(posted, "isoformat"):
        data["date_posted"] = posted.isoformat()
    return data


async def _run(params):
    from scrapers.manager import ScraperManager  # lazy: pulls in playwright
    manager = ScraperManager()
    listings = await manager.run_all(
        search_query=params["search_query"],
        location=params.get("location") or "Remote",
        limit_per_site=int(params.get("limit") or 10),
        job_type=params.get("job_type") or "Full-Time",
    )
    return [_serialize(job) for job in listings]


def main():
    _configure_logging()
    raw = sys.stdin.read() or "{}"
    params = json.loads(raw)
    if not params.get("search_query"):
        sys.stdout.write(json.dumps([]))
        return
    results = asyncio.run(_run(params))
    sys.stdout.write(json.dumps(results))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.scripts.test_scrape_cli -v`
Expected: PASS (3 tests). No playwright/loguru needed — the scraper import is lazy and only hit for non-empty queries.

- [ ] **Step 5: Commit**

```bash
git add scripts/__init__.py scripts/scrape_cli.py tests/scripts/
git commit -m "feat(scraper): add python CLI bridge that emits JSON on stdout"
```

---

### Task 4: Wire the endpoint in server.ts

**Files:**
- Modify: `server.ts` — imports near top; replace the `POST /api/scrape` handler body (lines ~178-363, from `// 3. simulated multi-engine scraping` through its closing `});`).

**Interfaces:**
- Consumes: `discoverAndBuild`, `ScrapeParams` (Tasks 1-2).

- [ ] **Step 1: Add the import**

After the existing imports at the top of `server.ts` (below the `import * as XLSX ...` line), add:
```ts
import { discoverAndBuild, ScrapeParams } from "./src/server/scraperBridge";
```

- [ ] **Step 2: Replace the `/api/scrape` handler**

Delete the entire current handler (the block starting at `// 3. simulated multi-engine scraping` and its `app.post("/api/scrape", ... });`, including the Gemini prompt, the `resolved.com` rewrite, the `canonical_url` blanking, and the `catch` fallback that pushes `fallbackJobs`). Replace with:
```ts
// 3. Real multi-engine scraping via the Python fleet (scripts/scrape_cli.py)
app.post("/api/scrape", async (req, res) => {
  const { search_query, location, job_type } = req.body;
  if (!search_query || !location) {
    return res.status(400).json({ error: "Search query and location are required." });
  }

  const params: ScrapeParams = {
    search_query,
    location,
    job_type: job_type || "Full-Time",
    limit: 10,
  };

  let newJobs: any[];
  try {
    const db = loadDB();
    newJobs = await discoverAndBuild(params, db.jobs);
    if (newJobs.length > 0) {
      db.jobs.push(...newJobs);
      saveDB(db);
    }
    return res.json({
      scraped_count: newJobs.length,
      new_count: newJobs.length,
      jobs: db.jobs,
      message:
        newJobs.length === 0
          ? "No new roles found for this search. Try a different query or location."
          : undefined,
    });
  } catch (error: any) {
    if (error && error.code === "ENOENT") {
      console.error("[Scraper] python3 not found:", error.message);
      return res.status(500).json({
        error:
          "Python runtime not found. Install Python 3, then run 'pip install -r requirements.txt' and 'playwright install chromium'. See README > Real Scraping Setup.",
      });
    }
    console.error("[Scraper] subprocess failed:", error.message);
    return res.status(502).json({ error: `Scraper failed: ${error.message}` });
  }
});
```

- [ ] **Step 3: Verify types compile**

Run: `npm run lint`
Expected: PASS (no `tsc` errors). Confirms the import path, `ScrapeParams` usage, and that no dangling references to the removed Gemini code remain.

- [ ] **Step 4: Manual smoke test with a stub (no real scraping)**

Run:
```bash
PYTHON_BIN=python3 npx tsx -e "
import { discoverAndBuild } from './src/server/scraperBridge';
discoverAndBuild({search_query:'python',location:'Remote',job_type:'Full-Time',limit:10}, [], {script:'tests/fixtures/stub_ok.py'})
  .then(j => { console.log('OK', j.length, j[0].canonical_url); })
  .catch(e => { console.error('ERR', e.message); process.exit(1); });
"
```
Expected: `OK 1 https://example.com/jobs/stub-1`. Confirms the wiring composes end-to-end without touching real sites.

- [ ] **Step 5: Commit**

```bash
git add server.ts
git commit -m "feat(scraper): wire /api/scrape to real python scraper fleet, drop AI mock"
```

---

### Task 5: JobCard link fix

**Files:**
- Modify: `src/components/JobCard.tsx`
- Modify (rewrite): `tests/components/JobCard.test.tsx`

**Interfaces:**
- Consumes: `JobListing` from `src/types.ts` (unchanged).

- [ ] **Step 1: Rewrite the failing test**

Replace the body of `tests/components/JobCard.test.tsx` with:
```tsx
import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { JobCard } from '../../src/components/JobCard';
import { expect, test, afterEach } from 'vitest';
import { JobListing } from '../../src/types';

const baseJob: JobListing = {
  id: 1,
  job_id_raw: 'test-1',
  title: 'Senior Test Engineer',
  company_name: 'TestCorp',
  location: 'Remote',
  work_place_type: 'Remote',
  job_type: 'Full-Time',
  source: 'LinkedIn',
  url: 'https://boards.example.com/job/1',
  canonical_url: 'https://boards.example.com/job/1',
  raw_url: 'https://boards.example.com/job/1',
  description_raw: 'Test description',
  ai_analysis: { id: 1, job_id: 1, match_score: 95, fit_summary: '', keywords_matched: [], keywords_missing: [] },
};

afterEach(() => cleanup());

test('renders core fields', () => {
  render(<JobCard job={baseJob} />);
  expect(screen.getByText('Senior Test Engineer')).toBeDefined();
  expect(screen.getByText('TestCorp')).toBeDefined();
  expect(screen.getByText('95%')).toBeDefined();
});

test('Open Job is an anchor pointing at the real canonical url', () => {
  render(<JobCard job={baseJob} />);
  const link = screen.getByRole('link', { name: /open job/i }) as HTMLAnchorElement;
  expect(link.getAttribute('href')).toBe('https://boards.example.com/job/1');
  expect(link.getAttribute('target')).toBe('_blank');
  expect(link.getAttribute('rel')).toContain('noopener');
});

test('falls back to url then raw_url when canonical_url missing', () => {
  const job = { ...baseJob, canonical_url: undefined };
  render(<JobCard job={job} />);
  const link = screen.getByRole('link', { name: /open job/i }) as HTMLAnchorElement;
  expect(link.getAttribute('href')).toBe('https://boards.example.com/job/1');
});

test('shows a disabled control when no url is available', () => {
  const job = { ...baseJob, canonical_url: undefined, url: '', raw_url: undefined };
  render(<JobCard job={job} />);
  expect(screen.queryByRole('link')).toBeNull();
  const btn = screen.getByRole('button', { name: /unavailable/i }) as HTMLButtonElement;
  expect(btn.disabled).toBe(true);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run tests/components/JobCard.test.tsx`
Expected: FAIL — current `JobCard` renders a `<button>Open Job</button>` (no `link` role), so the anchor assertions fail.

- [ ] **Step 3: Rewrite JobCard**

Replace the full contents of `src/components/JobCard.tsx` with:
```tsx
import React from 'react';
import { ExternalLink, MapPin, Briefcase, Building } from 'lucide-react';
import { JobListing } from '../types';

interface JobCardProps {
  job: JobListing;
}

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const linkToOpen = job.canonical_url || job.url || job.raw_url || '';

  const matchScore = job.ai_analysis?.match_score ?? 0;
  let scoreColor = 'bg-slate-800 text-slate-300';
  if (matchScore >= 80) scoreColor = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  else if (matchScore >= 60) scoreColor = 'bg-amber-500/20 text-amber-400 border-amber-500/30';
  else if (matchScore > 0) scoreColor = 'bg-rose-500/20 text-rose-400 border-rose-500/30';

  return (
    <div className="bg-panel rounded-xl p-5 border border-slate-800 hover:border-slate-600 transition-colors shadow-soft flex flex-col gap-3 group">
      <div className="flex justify-between items-start gap-4">
        <div>
          <h3 className="text-base font-semibold text-white group-hover:text-primary transition-colors line-clamp-2">
            {job.title}
          </h3>
          <div className="flex items-center gap-2 text-sm text-slate-400 mt-1">
            <Building className="w-3.5 h-3.5" />
            <span className="font-medium">{job.company_name}</span>
          </div>
        </div>
        {matchScore > 0 && (
          <div className={`px-2 py-1 rounded border text-xs font-bold flex-shrink-0 ${scoreColor}`} aria-label={`Match score: ${matchScore}%`}>
            {matchScore}%
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-muted mt-1">
        <span className="flex items-center gap-1 bg-surface px-2 py-1 rounded">
          <MapPin className="w-3 h-3" />
          {job.location} ({job.work_place_type})
        </span>
        <span className="flex items-center gap-1 bg-surface px-2 py-1 rounded">
          <Briefcase className="w-3 h-3" />
          {job.job_type}
        </span>
        <span className="flex items-center gap-1 bg-surface px-2 py-1 rounded">
          {job.source}
        </span>
      </div>

      <p className="text-sm text-slate-400 mt-2 line-clamp-3 leading-relaxed">
        {job.description_clean || job.description_raw}
      </p>

      <div className="mt-auto pt-4 flex items-center justify-between">
        <span className="text-xs text-slate-500 font-medium">
          {job.date_scraped ? new Date(job.date_scraped).toLocaleDateString() : 'Recent'}
        </span>
        {linkToOpen ? (
          <a
            href={linkToOpen}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-accent hover:text-white transition-colors"
            aria-label={`Open job: ${job.title}`}
          >
            Open Job
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        ) : (
          <button
            disabled
            title="Link unavailable"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 cursor-not-allowed"
            aria-label="Job link unavailable"
          >
            Link unavailable
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run tests/components/JobCard.test.tsx`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/components/JobCard.tsx tests/components/JobCard.test.tsx
git commit -m "fix(ui): open real job url directly, remove HEAD-check google fallback"
```

---

### Task 6: Runtime setup — package.json, Dockerfile, README

**Files:**
- Modify: `package.json` (add `test` script)
- Modify: `Dockerfile` (add Python + Playwright to the runtime stage)
- Modify: `README.md` (rewrite the "Broken Job Links" section; add "Real Scraping Setup")

- [ ] **Step 1: Add a test script to package.json**

In `package.json` `scripts`, add after `"lint": "tsc --noEmit"`:
```json
    "lint": "tsc --noEmit",
    "test": "vitest run"
```
(Keep valid JSON — add the comma after the `lint` line.)

- [ ] **Step 2: Run the full TS suite**

Run: `npm test`
Expected: PASS — all vitest tests from Tasks 1, 2, 5 green.

- [ ] **Step 3: Update the Dockerfile runtime stage**

The current runtime base is `node:20-alpine`; Playwright's Chromium does not run on Alpine/musl. Switch the runner stage to Debian-slim and install Python + Playwright. Replace the `# Stage 2: Production runtime stage` block's `FROM ...` line and add install layers:

Change:
```dockerfile
FROM node:20-alpine AS runner
```
to:
```dockerfile
FROM node:20-bookworm-slim AS runner

# Python runtime + Playwright deps for the real scraper fleet
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*
```
Then, after `RUN npm ci --omit=dev`, add (before copying dist):
```dockerfile
# Python scraper dependencies + Chromium browser
COPY requirements.txt ./
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt \
    && python3 -m playwright install --with-deps chromium
COPY scrapers ./scrapers
COPY schemas ./schemas
COPY scripts ./scripts
```

> Note: the Dockerfile cannot be built/verified in this environment. Reviewer builds it on the target machine. The primary supported path for the maintainer is local `npm run dev` with Python installed.

- [ ] **Step 4: Update README**

Replace the "### Broken Job Links" subsection in `README.md` with:
```markdown
### Job Links / Scraping
**Behaviour**: `POST /api/scrape` runs the real Python + Playwright scraper
fleet (`scripts/scrape_cli.py` → `scrapers/manager.py`). Each listing stores the
real posting URL in `canonical_url`, and the UI opens it directly in a new tab.
If the scrapers return nothing (site blocked / no network), the app shows an
honest empty result — it never fabricates listings.
**Verification**: watch `server.ts` stdout for `[Scraper]` errors, and the
Python fleet's `[scraper]` logs on stderr for per-engine counts.
```

And add a new section after "Running the System":
```markdown
## Real Scraping Setup

The scraper fleet is Python + Playwright. Install it once alongside the Node app:

\`\`\`bash
pip install -r requirements.txt
playwright install chromium
\`\`\`

The Node server invokes `python3 scripts/scrape_cli.py` on each search. Override
the interpreter with `PYTHON_BIN=/path/to/python` if `python3` is not on PATH.

Live scraping success depends on network access and each site's anti-bot
defences; results can legitimately be empty from restricted networks.
```

- [ ] **Step 5: Commit**

```bash
git add package.json Dockerfile README.md
git commit -m "chore(scraper): add python+playwright runtime, test script, and docs"
```

---

## Self-Review

**Spec coverage:**
- Node-spawns-Python subprocess → Tasks 2, 3, 4. ✓
- No fake data / honest empty → Task 4 (removed Gemini + fallback; empty message). ✓
- Data mapping table → Task 1 `mapScrapedJob`. ✓
- Frontend link fix (remove HEAD-check/Google fallback/resolved.com) → Task 5. ✓ (resolved.com + blanking removed with the old handler in Task 4.)
- Error handling table (502/500/400/200/timeout) → Tasks 2 (runner) + 4 (route). ✓
- Runtime deps + preflight → Task 4 (ENOENT 500) + Task 6 (Dockerfile/README). ✓
- Testing (stubbed subprocess, JobCard, python CLI) → Tasks 1-3, 5. ✓

**Placeholder scan:** No TBD/TODO; every code step contains full code. ✓

**Type consistency:** `ScrapedJob`, `ScrapeParams`, `RunScraperOpts`, `mapScrapedJob`, `buildNewJobs`, `runScraper`, `discoverAndBuild` used identically across tasks. Route imports `discoverAndBuild`/`ScrapeParams` from `./src/server/scraperBridge` matching Task 1-2 exports. ✓

**Known environment limits (not plan defects):** live scraper yield and Docker build are verified on the maintainer's machine, not in this sandbox (documented in spec + Task 6).
