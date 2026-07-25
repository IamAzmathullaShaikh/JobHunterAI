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
