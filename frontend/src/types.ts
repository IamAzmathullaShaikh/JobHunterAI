export enum ApplicationStatus {
  WISHLIST = "Wishlist",
  APPLIED = "Applied",
  INTERVIEWING = "Interviewing",
  OFFERED = "Offered",
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
  required_skills?: string[];
  seniority?: string;
  technologies?: string[];
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
  readability_score: number;
  action_verb_score: number;
  formatting_score: number;
  quantification_score: number;
  fit_summary: string;
  keywords_matched: string[];
  keywords_missing: string[];
  detailed_recommendations?: {
    critical: string[];
    high: string[];
    medium: string[];
  };
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
  email?: string;
  phone?: string;
  location?: string;
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

// --- Resume System V2 ---

export interface ResumeHeader {
  name: string;
  title: string;
  email: string;
  phone: string;
  location: string;
  website?: string;
  linkedin?: string;
  github?: string;
}

export interface WorkHistoryItem {
  company: string;
  title: string;
  location: string;
  start_date: string;
  end_date: string;
  bullets: string[];
}

export interface EducationItem {
  school: string;
  degree: string;
  location: string;
  date: string;
}

export interface ProjectItem {
  name: string;
  role: string;
  date: string;
  bullets: string[];
}

export interface ResumeContent {
  header: ResumeHeader;
  summary: string;
  work_history: WorkHistoryItem[];
  education: EducationItem[];
  skills: string[];
  projects: ProjectItem[];
  certifications: any[];
  languages: any[];
  interests: string[];
  references: any[];
}

export interface Resume {
  id: number;
  name: string;
  template_id: string;
  is_archived: boolean;
  content: ResumeContent;
  job_id?: number;
  created_at: string;
  updated_at: string;
}

// --- Cover Letter System ---

export interface CoverLetterContent {
  header: ResumeHeader;
  salutation: string;
  opening: string;
  why_us: string;
  experience_highlight: string;
  closing: string;
  sign_off: string;
}

export interface CoverLetter {
  id: number;
  name: string;
  template_id: string;
  writing_style: string;
  is_archived: boolean;
  content: CoverLetterContent;
  resume_id?: number;
  job_id?: number;
  created_at: string;
  updated_at: string;
}

// --- Interview System ---

export interface InterviewQuestion {
  id: number;
  session_id: number;
  question_text: string;
  category: string;
  user_answer?: string;
  feedback?: any;
  score?: number;
  improved_answer?: string;
}

export interface InterviewSession {
  id: number;
  name: string;
  difficulty: string;
  status: string;
  overall_score?: number;
  resume_id?: number;
  job_id?: number;
  created_at: string;
  updated_at: string;
  questions?: InterviewQuestion[];
}

// --- Recruiter CRM ---

export interface RecruiterContact {
  id?: number;
  name: string;
  title: string;
  company: string;
  department?: string;
  location?: string;
  email?: string;
  linkedin_url?: string;
  confidence_score: number;
  match_explanation?: string;
  status: string;
  notes?: string;
  ai_ranking_score?: number;
  last_contacted_at?: string;
  created_at?: string;
  updated_at?: string;
}
