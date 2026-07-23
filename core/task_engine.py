import os
import json
import pdfplumber
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.ai.smart_router import route as smart_route
from core.privacy import redactor
from core.caching import AICache
from core.utils.logger import logger
from core.database.models import JobListing, UserProfile, MatchHistory, TelemetryLog

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
    Implements the 10 core career automation workflows using the 3-Tier fallback logic
    with Token Policing and persistent caching.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.cache = AICache(db_session)

    def _truncate_text(self, text: str, max_chars: int = 4000) -> str:
        """Enforces token safeguards by truncating large inputs."""
        if not text:
            return ""
        if len(text) <= max_chars:
            return text
        logger.warning(f"Text too large ({len(text)} chars). Truncating to {max_chars} chars for quota safety.")
        return text[:max_chars] + "... [Truncated for Token Safety]"

    # --- Workflow 1: PDF Resume Parsing ---
    async def parse_resume_pdf(self, file_path: str) -> Dict[str, Any]:
        """Workflow 1: Local PDF text extraction and basic structure parsing."""
        logger.info(f"Parsing resume PDF: {file_path}")
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

            # Check cache first for identical resume text
            cached = await self.cache.get(text[:5000]) # Cache based on first 5k chars
            if cached:
                return {"success": True, "source": "local_cache", "data": cached}

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
        """Workflow 2: 3-Tiered ATS analysis with Cache & Token policing."""

        # 1. Policing: Truncate inputs
        safe_resume = self._truncate_text(resume_text)
        safe_job = self._truncate_text(job_description)

        # 2. Caching: Check if this pair has been matched before
        cache_key = f"ats_match_{safe_resume[:1000]}_{safe_job[:1000]}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        # 3. Privacy: Redact PII
        redacted_resume, mapping = redactor.redact(safe_resume)

        async def groq_call():
            from core.ai.matcher import JobMatcher
            matcher = JobMatcher()
            return await matcher.analyze_fit(safe_job, redacted_resume)
        groq_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        async def gemini_call():
            # In a full implementation, we'd have a specific Gemini matcher
            return await groq_call()

        def local_call():
            model = get_local_model()
            if not model:
                return {"match_score": 0, "fit_summary": "Local model unavailable."}

            embeddings = model.encode([redacted_resume, safe_job])
            from sklearn.metrics.pairwise import cosine_similarity
            score = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]) * 100

            return {
                "match_score": round(score, 1),
                "fit_summary": "Semantic match calculated locally using MiniLM.",
                "keywords_matched": [],
                "keywords_missing": []
            }

        result = await smart_route(groq_call, local_call)

        # 4. Persistence & Caching
        if result["success"]:
            await self.cache.set(cache_key, result["data"])
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
        """Workflow 4: 3-Tiered cover letter generation with Caching."""

        safe_resume = self._truncate_text(resume_text, 3000)
        safe_job = self._truncate_text(job_details, 3000)

        cache_key = f"cover_letter_{safe_resume[:500]}_{safe_job[:500]}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        redacted_resume, _ = redactor.redact(safe_resume)
        prompt = f"Write a professional cover letter based on this resume: {redacted_resume} and this job: {safe_job}"

        async def llm_call():
            from core.ai.llm_client import get_llm_client
            client = get_llm_client()
            return await client.chat_completion(None, [{"role": "user", "content": prompt}])
        llm_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        def local_call():
            template = Template("Dear Hiring Manager, I am writing to express interest in the position at {{ company }}. My background in {{ skills }} makes me a strong fit...")
            return template.render(company="the company", skills="relevant technologies")

        result = await smart_route(llm_call, local_call)
        if result["success"]:
            await self.cache.set(cache_key, result["data"])
        return result

    # --- Workflow 5: Recruiter Outreach DM ---
    async def generate_outreach(self, target_role: str, company: str) -> Dict[str, Any]:
        """Workflow 5: 3-Tiered outreach message generation."""
        cache_key = f"outreach_{target_role}_{company}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        prompt = f"Draft a short, professional LinkedIn outreach message for a {target_role} position at {company}."

        async def llm_call():
            from core.ai.llm_client import get_llm_client
            client = get_llm_client()
            return await client.chat_completion(None, [{"role": "user", "content": prompt}])
        llm_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        def local_call():
            return f"Hi [Name], I noticed the {target_role} opening at {company} and would love to connect..."

        result = await smart_route(llm_call, local_call)
        if result["success"]:
            await self.cache.set(cache_key, result["data"])
        return result

    # --- Workflow 6: Interview Q&A Prep ---
    async def prepare_interview(self, job_description: str) -> Dict[str, Any]:
        """Workflow 6: 3-Tiered interview preparation."""
        safe_job = self._truncate_text(job_description, 4000)
        cache_key = f"interview_prep_{safe_job[:1000]}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        prompt = f"Generate 5 technical and 3 behavioral interview questions with suggested answers for this job: {safe_job}"

        async def llm_call():
            from core.ai.llm_client import get_llm_client
            client = get_llm_client()
            return await client.chat_completion(None, [{"role": "user", "content": prompt}])
        llm_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        def local_call():
            return "1. Tell me about yourself. 2. What are your strengths? 3. Why do you want this job?"

        result = await smart_route(llm_call, local_call)
        if result["success"]:
            await self.cache.set(cache_key, result["data"])
        return result

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
