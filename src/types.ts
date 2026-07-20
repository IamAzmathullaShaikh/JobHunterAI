export enum ApplicationStatus {
  IDENTIFIED = "Identified",
  AI_READY = "AI Ready",
  APPLIED = "Applied",
  INTERVIEWING = "Interviewing",
  OFFER = "Offer",
  REJECTED = "Rejected",
  ARCHIVED = "Archived"
}

export interface JobListing {
  id: number;
  job_id_raw: string;
  title: string;
  company_name: string;
  location: string;
  work_place_type: "Remote" | "Hybrid" | "Onsite" | string;
  job_type: "Full-Time" | "Internship" | "Apprenticeship" | string;
  source: string;
  url: string;
  raw_url?: string;
  canonical_url?: string;
  portal_id?: string;
  needs_validation?: boolean;
  description_raw: string;
  description_clean?: string;
  salary_raw?: string;
  is_starred?: boolean;
  date_scraped?: string;
  ai_analysis?: AIAnalysis | null;
  application?: JobApplication | null;
}

export interface AIAnalysis {
  id: number;
  job_id: number;
  match_score: number; // 0 - 100
  fit_summary: string;
  keywords_matched: string[];
  keywords_missing: string[];
  analyzed_at?: string;
}

export interface JobApplication {
  id: number;
  job_id: number;
  status: ApplicationStatus;
  notes?: string;
  date_created?: string;
  date_updated?: string;
}

export interface CandidateProfile {
  full_name: string;
  total_experience_years: number;
  education: string[];
  key_skills: string[];
  recommended_search_queries: string[];
  experience_highlights: string[];
}

export interface ContactFinderDTO {
  suggested_search_queries: Record<string, string>; // label -> URL
  cold_outreach_dm_template: string;
}
