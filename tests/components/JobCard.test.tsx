import React from 'react';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { JobCard } from '../../src/components/JobCard';
import { expect, test, vi, beforeEach, afterEach } from 'vitest';
import { JobListing } from '../../src/types';

const mockJob: JobListing = {
  id: 1,
  job_id_raw: 'test-1',
  title: 'Senior Test Engineer',
  company_name: 'TestCorp',
  location: 'Remote',
  work_place_type: 'Remote',
  job_type: 'Full-Time',
  source: 'LinkedIn',
  url: 'https://test.com/job',
  canonical_url: 'https://test.com/job',
  raw_url: 'https://test.com/job',
  description_raw: 'Test description',
  ai_analysis: {
    id: 1,
    job_id: 1,
    match_score: 95,
    fit_summary: '',
    keywords_matched: [],
    keywords_missing: []
  }
};

beforeEach(() => {
  vi.clearAllMocks();
  window.open = vi.fn();
});

afterEach(() => {
  cleanup();
});

test('JobCard renders correctly', () => {
  render(<JobCard job={mockJob} />);
  expect(screen.getByText('Senior Test Engineer')).toBeDefined();
  expect(screen.getByText('TestCorp')).toBeDefined();
  expect(screen.getByText('95%')).toBeDefined();
});

test('JobCard head check fallback', async () => {
  global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));
  render(<JobCard job={mockJob} />);
  
  const openButton = screen.getByText('Open Job');
  fireEvent.click(openButton);
  
  await waitFor(() => {
    expect(window.open).toHaveBeenCalledWith(
      expect.stringContaining('google.com/search'),
      '_blank'
    );
  });
});
