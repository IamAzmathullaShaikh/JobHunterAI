import { spawn } from 'child_process';
import path from 'path';

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
