import os
import json
import pdfplumber
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from smart_router import router
from privacy import redactor
from utils.logger import logger
from database.models import JobListing, UserProfile, MatchHistory, TelemetryLog

# Optional local ML imports - loaded only if needed to keep startup fast
_model = None

def get_local_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.error("sentence-transformers not installed. Local semantic match will fail.")
    return _model

class TaskEngine:
    """
    Implements the 10 core career automation workflows using the 3-Tier fallback logic.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    # --- Workflow 1: PDF Resume Parsing ---
    async def parse_resume_pdf(self, file_path: str) -> Dict[str, Any]:
        """Workflow 1: Local PDF text extraction and basic structure parsing."""
        logger.info(f"Parsing resume PDF: {file_path}")
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

            # Simple heuristic parsing (can be enhanced by LLM in a separate step if desired)
            # For this workflow requirement, it's Tier 3 (Local)
            return {
                "success": True,
                "source": "local_pypdf",
                "data": {
                    "raw_text": text,
                    "length": len(text)
                }
            }
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            return {"success": False, "error": str(e)}

    # --- Workflow 2: ATS Score & Gap Analysis ---
    async def analyze_ats_fit(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Workflow 2: 3-Tiered ATS analysis."""

        # Redact PII first
        redacted_resume, mapping = redactor.redact(resume_text)

        async def groq_call():
            from ai.matcher import JobMatcher
            matcher = JobMatcher() # Uses settings.GROQ_MODEL
            return await matcher.analyze_fit(job_description, redacted_resume)

        async def gemini_call():
            from ai.matcher import JobMatcher
            # We'll assume JobMatcher can be told which provider to use or we have another one
            # For now, let's use a generic LLM call if we have multiple clients
            from ai.llm_client import get_llm_client
            client = get_llm_client() # Needs to support provider selection
            # Placeholder for direct Gemini logic if JobMatcher is Groq-only
            # In real implementation, JobMatcher should be refactored to use the router
            return await groq_call() # Temporary redirect until matcher is refactored

        def local_call():
            # Vector embedding based match
            model = get_local_model()
            if not model:
                return {"match_score": 0, "fit_summary": "Local model unavailable."}

            embeddings = model.encode([redacted_resume, job_description])
            from sklearn.metrics.pairwise import cosine_similarity
            score = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]) * 100

            return {
                "match_score": round(score, 1),
                "fit_summary": "Semantic match calculated locally using MiniLM.",
                "keywords_matched": [], # Would need TF-IDF for keywords
                "keywords_missing": []
            }

        result = await router.route("ats_analysis", groq_call, gemini_call, local_call)

        # If successful, save to history
        if result["success"]:
            history = MatchHistory(
                match_score=result["data"].get("match_score", 0),
                fit_summary=result["data"].get("fit_summary", ""),
                keywords_matched=result["data"].get("keywords_matched"),
                keywords_missing=result["data"].get("keywords_missing")
            )
            self.db.add(history)
            await self.db.commit()

        return result

    # --- Workflow 3: Live Job Scraping ---
    async def search_jobs(self, query: str, location: str = "Remote") -> Dict[str, Any]:
        """Workflow 3: Live scraping using JobSpy."""
        try:
            from jobspy import scrape_jobs
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "glassdoor"],
                search_term=query,
                location=location,
                results_wanted=10,
                hours_old=72,
                country_allowed='usa', # Adjust as needed
            )
            # Convert pandas DF to list of dicts
            jobs_list = jobs.to_dict('records')
            return {"success": True, "source": "jobspy", "data": jobs_list}
        except Exception as e:
            logger.error(f"JobSpy scrape failed: {e}")
            return {"success": False, "error": str(e)}

    # --- Workflow 4: Tailored Cover Letter ---
    async def generate_cover_letter(self, resume_text: str, job_details: str) -> Dict[str, Any]:
        """Workflow 4: 3-Tiered cover letter generation."""
        redacted_resume, _ = redactor.redact(resume_text)

        prompt = f"Write a professional cover letter based on this resume: {redacted_resume} and this job: {job_details}"

        async def llm_call():
            from ai.llm_client import get_llm_client
            client = get_llm_client()
            return await client.chat_completion(None, [{"role": "user", "content": prompt}])

        def local_call():
            template = Template("Dear Hiring Manager, I am writing to express interest in the position at {{ company }}. My background in {{ skills }} makes me a strong fit...")
            # Extract basic info locally
            return template.render(company="the company", skills="relevant technologies")

        return await router.route("cover_letter", llm_call, llm_call, local_call)

    # --- Workflow 5: Recruiter Outreach DM ---
    async def generate_outreach(self, target_role: str, company: str) -> Dict[str, Any]:
        """Workflow 5: 3-Tiered outreach message generation."""
        prompt = f"Draft a short, professional LinkedIn outreach message for a {target_role} position at {company}."

        async def llm_call():
            from ai.llm_client import get_llm_client
            client = get_llm_client()
            return await client.chat_completion(None, [{"role": "user", "content": prompt}])

        def local_call():
            return f"Hi [Name], I noticed the {target_role} opening at {company} and would love to connect..."

        return await router.route("outreach", llm_call, llm_call, local_call)

    # --- Workflow 6: Interview Q&A Prep ---
    async def prepare_interview(self, job_description: str) -> Dict[str, Any]:
        """Workflow 6: 3-Tiered interview preparation."""
        prompt = f"Generate 5 technical and 3 behavioral interview questions with suggested answers for this job: {job_description}"

        async def llm_call():
            from ai.llm_client import get_llm_client
            client = get_llm_client()
            return await client.chat_completion(None, [{"role": "user", "content": prompt}])

        def local_call():
            return "1. Tell me about yourself. 2. What are your strengths? 3. Why do you want this job?"

        return await router.route("interview_prep", llm_call, llm_call, local_call)

    # --- Workflow 7: Voice Mock Interview ---
    async def mock_interview_voice(self, audio_data: Any) -> Dict[str, Any]:
        """Workflow 7: Integration placeholder for voice-to-text and AI response."""
        # This would typically involve Whisper (Tier 1) or local STT
        return {"success": True, "source": "placeholder", "data": "Voice integration requires active audio streaming."}

    # --- Workflow 8: Salary & Location Insights ---
    async def get_salary_insights(self, role: str, location: str) -> Dict[str, Any]:
        """Workflow 8: Salary data from Teleport or DDG."""
        try:
            import requests
            # Simple Teleport API check for cities
            city = location.lower().replace(" ", "-")
            res = requests.get(f"https://api.teleport.org/api/urban_areas/slug:{city}/salaries/")
            if res.status_code == 200:
                return {"success": True, "source": "teleport_api", "data": res.json()}

            # Fallback to a static or search-based estimate
            return {"success": True, "source": "static_data", "data": {"estimated_range": "$80k - $120k"}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Workflow 9: User Data & Auth ---
    async def sync_user_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Workflow 9: Local SQLite persistence for user profiles."""
        try:
            profile = UserProfile(**profile_data)
            self.db.add(profile)
            await self.db.commit()
            return {"success": True, "source": "local_sqlite", "data": profile_data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Workflow 10: Cloud Resume Storage ---
    async def store_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Workflow 10: Local file system storage with R2/S3 placeholder."""
        storage_path = os.path.join("data", "resumes")
        os.makedirs(storage_path, exist_ok=True)
        file_path = os.path.join(storage_path, filename)

        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            return {"success": True, "source": "local_fs", "data": {"path": file_path}}
        except Exception as e:
            return {"success": False, "error": str(e)}
