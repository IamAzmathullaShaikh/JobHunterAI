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
