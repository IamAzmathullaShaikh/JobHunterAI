import React from 'react';
import { render, screen, cleanup, within } from '@testing-library/react';
import { expect, test, afterEach, vi } from 'vitest';
import JobsTable from '../../src/components/JobsTable';
import { JobListing } from '../../src/types';

const makeJob = (over: Partial<JobListing> = {}): JobListing => ({
  id: 1,
  job_id_raw: 'li-1',
  title: 'Senior Python Engineer',
  company_name: 'Greenhouse Demo Co',
  location: 'Remote',
  work_place_type: 'Remote',
  job_type: 'Full-Time',
  source: 'LinkedIn',
  url: 'https://boards.greenhouse.io/example/jobs/42',
  canonical_url: 'https://boards.greenhouse.io/example/jobs/42',
  raw_url: 'https://boards.greenhouse.io/example/jobs/42',
  description_raw: 'Own backend services.',
  ...over,
});

afterEach(() => cleanup());

test('View Job links directly to the real canonical url (no google fallback)', () => {
  render(<JobsTable jobs={[makeJob()]} onTrackJob={vi.fn()} />);
  const link = screen.getByRole('link', { name: /view job/i }) as HTMLAnchorElement;
  expect(link.getAttribute('href')).toBe('https://boards.greenhouse.io/example/jobs/42');
  expect(link.getAttribute('href')).not.toContain('google.com');
});

test('a real url containing the substring "mock" is still a clickable link', () => {
  const job = makeJob({
    canonical_url: 'https://careers.mockingbird.io/jobs/7',
    raw_url: 'https://careers.mockingbird.io/jobs/7',
    url: 'https://careers.mockingbird.io/jobs/7',
  });
  render(<JobsTable jobs={[job]} onTrackJob={vi.fn()} />);
  const link = screen.getByRole('link', { name: /view job/i }) as HTMLAnchorElement;
  expect(link.getAttribute('href')).toBe('https://careers.mockingbird.io/jobs/7');
});

test('shows the expired-job fallback only when there is no usable url', () => {
  const job = makeJob({ canonical_url: undefined, raw_url: undefined, url: '' });
  render(<JobsTable jobs={[job]} onTrackJob={vi.fn()} />);
  expect(screen.queryByRole('link', { name: /view job/i })).toBeNull();
  expect(screen.getByText(/may have expired/i)).toBeDefined();
});
