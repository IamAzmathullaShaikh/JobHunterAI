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
