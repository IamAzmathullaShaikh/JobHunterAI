import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import pdfplumber
from jinja2 import Template
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.ai.smart_router import route as smart_route
from core.caching import AICache
from core.database.models import (JobListing, MatchHistory, TelemetryLog,
                                  UserProfile)
from core.privacy import redactor

logger = logging.getLogger(__name__)

# Optional local ML imports - loaded only if needed to keep startup fast
_model = None


def get_local_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            logger.error(
                "sentence-transformers not installed. Local semantic match will fail."
            )
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
        logger.warning(
            f"Text too large ({len(text)} chars). Truncating to {max_chars} chars for quota safety."
        )
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
            cached = await self.cache.get(text[:5000])  # Cache based on first 5k chars
            if cached:
                return {"success": True, "source": "local_cache", "data": cached}

            return {
                "success": True,
                "source": "local_pypdf",
                "data": {"raw_text": text, "length": len(text)},
            }
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            return {"success": False, "error": str(e)}

    # --- Workflow 2: ATS Score & Gap Analysis ---
    async def analyze_ats_fit(
        self, resume_text: str, job_description: str
    ) -> Dict[str, Any]:
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

            score = (
                float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]) * 100
            )

            return {
                "match_score": round(score, 1),
                "fit_summary": "Semantic match calculated locally using MiniLM.",
                "keywords_matched": [],
                "keywords_missing": [],
            }

        result_data = await smart_route(groq_call, local_call)

        # 4. Persistence & Caching
        # Normalize result for uniform API response
        is_success = isinstance(result_data, dict) and "match_score" in result_data
        final_result = {
            "success": is_success,
            "source": "cloud" if is_success and "(local)" not in str(result_data) else "local",
            "data": result_data
        }

        if is_success:
            await self.cache.set(cache_key, result_data)
            history = MatchHistory(
                match_score=result_data.get("match_score", 0),
                readability_score=result_data.get("readability_score", 0),
                action_verb_score=result_data.get("action_verb_score", 0),
                formatting_score=result_data.get("formatting_score", 0),
                quantification_score=result_data.get("quantification_score", 0),
                fit_summary=result_data.get("fit_summary", ""),
                keywords_matched=result_data.get("keywords_matched"),
                keywords_missing=result_data.get("keywords_missing"),
            )
            self.db.add(history)
            await self.db.commit()

        return final_result

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
                country_allowed="usa",  # Adjust as needed
            )
            # Convert pandas DF to list of dicts
            jobs_list = jobs.to_dict("records")
            return {"success": True, "source": "jobspy", "data": jobs_list}
        except Exception as e:
            logger.error(f"JobSpy scrape failed: {e}")
            return {"success": False, "error": str(e)}

    # --- Workflow 4: Tailored Cover Letter ---
    async def generate_cover_letter(
        self, resume_text: str, job_details: str
    ) -> Dict[str, Any]:
        """Workflow 4: 3-Tiered cover letter generation with Caching."""

        safe_resume = self._truncate_text(resume_text, 3000)
        safe_job = self._truncate_text(job_details, 3000)

        cache_key = f"cover_letter_{safe_resume[:500]}_{safe_job[:500]}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        redacted_resume, _ = redactor.redact(safe_resume)
        prompt = f"""
        Write a professional, high-conversion cover letter.
        Candidate Context: {redacted_resume}
        Target Job: {safe_job}

        Guidelines:
        1. Emphasize specific technical fit.
        2. Quantify achievements where possible.
        3. Use a tone that matches the company culture (based on the JD).
        4. Return ONLY the cover letter text.
        """

        async def llm_call():
            from core.ai.llm_client import get_llm_client

            client = get_llm_client()
            response = await client.chat_completion(
                None,
                [
                    {
                        "role": "system",
                        "content": "You are a professional technical writer specialized in hyper-tailored cover letters.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return (
                response.choices[0].message.content
                if hasattr(response, "choices")
                else str(response)
            )

        llm_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        def local_call():
            template = Template(
                "Dear Hiring Manager, I am writing to express interest in the position at {{ company }}. My background in {{ skills }} makes me a strong fit..."
            )
            return template.render(
                company="the company", skills="relevant technologies"
            )

        result_data = await smart_route(llm_call, local_call)

        # Handle formatting: if result_data is a dict (maybe from a previous version of router), extract text
        text_content = result_data.get("data") if isinstance(result_data, dict) else result_data

        final_result = {
            "success": True,
            "cover_letter": text_content,
            "data": text_content, # compatibility
            "source": "cloud" if "Dear Hiring Manager" not in str(text_content) else "local"
        }

        if final_result["success"]:
            await self.cache.set(cache_key, text_content)
        return final_result

    async def generate_cover_letter_structured(
        self,
        resume_content: Dict[str, Any],
        job_description: str,
        writing_style: str = "Professional",
        company_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Workflow 4B: Grounded, styled, and structured cover letter generation."""

        safe_jd = self._truncate_text(job_description, 3000)
        cache_key = f"cl_struct_{hash(str(resume_content))}_{safe_jd[:500]}_{writing_style}"

        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        prompt = f"""
        You are an expert career coach and technical writer.
        Generate a highly personalized, structured cover letter.

        Writing Style: {writing_style}
        Target Company: {company_name or 'the company'}

        Candidate Resume Context (DO NOT HALLUCINATE):
        {json.dumps(resume_content)}

        Target Job Description:
        {safe_jd}

        Strict Output Format (JSON only):
        {{
            "salutation": "...",
            "opening": "...",
            "why_us": "...",
            "experience_highlight": "...",
            "closing": "...",
            "sign_off": "..."
        }}

        Rules:
        1. Ground everything in the resume. If a skill isn't there, don't mention it.
        2. Adjust tone based on the style: {writing_style}.
        3. Make the "why_us" section specifically reference the JD context.
        """

        async def llm_call():
            from core.ai.llm_client import Capability, get_llm_client
            client = get_llm_client()
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content if hasattr(response, "choices") else str(response)

            import re
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("Failed to parse AI JSON response")

        def local_call():
            return {
                "salutation": "Dear Hiring Manager,",
                "opening": f"I am writing to express my interest in the role at {company_name or 'your company'}.",
                "why_us": "Your company's mission aligns perfectly with my career goals.",
                "experience_highlight": "In my previous roles, I have demonstrated a strong ability to deliver results.",
                "closing": "Thank you for your time and consideration.",
                "sign_off": "Best regards,"
            }

        result_data = await smart_route(llm_call, local_call)

        final_result = {
            "success": True,
            "data": result_data,
            "source": "cloud" if "opening" in result_data and len(result_data["opening"]) > 50 else "local"
        }

        if final_result["success"]:
            await self.cache.set(cache_key, result_data)
        return final_result

    async def regenerate_cl_section(
        self,
        section_id: str,
        resume_content: Dict[str, Any],
        job_description: str,
        writing_style: str = "Professional"
    ) -> Dict[str, Any]:
        """Regenerates a single section of a cover letter."""

        prompt = f"""
        You are an elite career coach. Regenerate ONLY the "{section_id}" section of a cover letter.

        Writing Style: {writing_style}

        Candidate Context:
        {json.dumps(resume_content)}

        Target JD:
        {job_description[:2000]}

        Rules:
        1. Return ONLY the text for the "{section_id}" paragraph.
        2. Do not include any other sections, salutations, or sign-offs.
        3. Ground the content in the resume and JD.
        """

        async def llm_call():
            from core.ai.llm_client import Capability, get_llm_client
            client = get_llm_client()
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content if hasattr(response, "choices") else str(response)

        result_text = await smart_route(llm_call, lambda: f"Refined {section_id} paragraph.")

        return {"success": True, "data": result_text}

    # --- Workflow 6B: Interactive Contextual Question Generation ---
    async def generate_contextual_questions(
        self,
        resume_content: Dict[str, Any],
        job_description: str,
        difficulty: str = "Senior",
    ) -> List[Dict[str, Any]]:
        """Generates 5 role-specific and resume-grounded interview questions."""

        prompt = f"""
        You are an elite technical interviewer. Generate 5 unique interview questions for a candidate.

        Difficulty Level: {difficulty}

        Candidate Resume:
        {json.dumps(resume_content)}

        Target Job Description:
        {job_description[:2000]}

        Requirements:
        1. 2 Technical questions specifically probing technologies mentioned in the resume relative to the JD.
        2. 1 Behavioral question targeting a project or achievement listed in the resume.
        3. 1 System Design or Architecture question relative to the seniority: {difficulty}.
        4. 1 "Company Culture" or HR question based on the JD context.

        Output Format (JSON array only):
        [
            {{"question_text": "...", "category": "Technical"}},
            ...
        ]
        """

        async def llm_call():
            from core.ai.llm_client import Capability, get_llm_client
            client = get_llm_client()
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content if hasattr(response, "choices") else str(response)

            import re
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("Failed to parse AI JSON response")

        def local_call():
            return [
                {"question_text": "Tell me about your most challenging project.", "category": "Behavioural"},
                {"question_text": "How do you handle technical debt?", "category": "Technical"},
                {"question_text": f"Why are you a good fit for this {difficulty} role?", "category": "HR"},
            ]

        return await smart_route(llm_call, local_call)

    # --- Workflow 7B: Deep Answer Evaluation ---
    async def evaluate_interview_answer(
        self, question: str, answer: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provides detailed feedback and scoring for an interview answer."""

        prompt = f"""
        Evaluate this interview answer.
        Question: {question}
        User Answer: {answer}

        {f"Context (Resume/JD): {context}" if context else ""}

        Critique the answer based on:
        1. STAR Method usage (for behavioral).
        2. Technical accuracy (for technical).
        3. Clarity and Confidence.

        Output Format (JSON only):
        {{
            "score": 8.5,
            "strengths": ["...", "..."],
            "weaknesses": ["...", "..."],
            "suggestions": "...",
            "improved_answer": "..."
        }}
        """

        async def llm_call():
            from core.ai.llm_client import Capability, get_llm_client
            client = get_llm_client()
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content if hasattr(response, "choices") else str(response)

            import re
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("Failed to parse AI evaluation JSON")

        def local_call():
            return {
                "score": 5.0,
                "strengths": ["Answer provided"],
                "weaknesses": ["Local analysis limited"],
                "suggestions": "Try to use the STAR method.",
                "improved_answer": "I don't have a local improved answer yet."
            }

        return await smart_route(llm_call, local_call)

    # --- Workflow 5: Recruiter Outreach DM ---
    async def generate_outreach(self, target_role: str, company: str) -> Dict[str, Any]:
        """Workflow 5: 3-Tiered outreach message generation."""
        cache_key = f"outreach_{target_role}_{company}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        prompt = f"Draft a short, professional LinkedIn outreach message for a {target_role} position at {company}."

        async def llm_call():
            from core.ai.llm_client import Capability, get_llm_client

            client = get_llm_client()
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model, messages=[{"role": "user", "content": prompt}]
            )
            return (
                response.choices[0].message.content
                if hasattr(response, "choices")
                else str(response)
            )

        llm_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        def local_call():
            return f"Hi [Name], I noticed the {target_role} opening at {company} and would love to connect..."

        result_data = await smart_route(llm_call, local_call)

        final_result = {
            "success": True,
            "data": result_data,
            "source": "cloud" if "Hi [Name]" not in str(result_data) else "local"
        }

        if final_result["success"]:
            await self.cache.set(cache_key, result_data)
        return final_result

    async def generate_recruiter_outreach(
        self,
        recruiter_name: str,
        recruiter_title: str,
        company_name: str,
        resume_content: Dict[str, Any],
        message_type: str = "Intro",
        writing_style: str = "Professional"
    ) -> Dict[str, Any]:
        """Workflow 5B: Context-aware and styled recruiter outreach generation."""

        prompt = f"""
        Draft a high-conversion {message_type} message for a recruiter on LinkedIn.

        Writing Style: {writing_style}
        Recruiter: {recruiter_name} ({recruiter_title} at {company_name})

        Candidate Context:
        {json.dumps(resume_content)}

        Guidelines:
        1. Tone: {writing_style}.
        2. Reference a specific achievement from the resume that matches the recruiter's company profile.
        3. Keep it concise (under 100 words).
        4. Return ONLY the message text.
        """

        async def llm_call():
            from core.ai.llm_client import Capability, get_llm_client
            client = get_llm_client()
            model = client.get_model_for_capability(Capability.REASONING)
            response = await client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content if hasattr(response, "choices") else str(response)

        result_text = await smart_route(llm_call, lambda: f"Hi {recruiter_name}, I'm following up on my application to {company_name}...")

        return {"success": True, "data": result_text}

    # --- Workflow 6: Interview Q&A Prep ---
    async def prepare_interview(self, job_description: str) -> Dict[str, Any]:
        """Workflow 6: 3-Tiered interview preparation."""
        safe_job = self._truncate_text(job_description, 4000)
        cache_key = f"interview_prep_{safe_job[:1000]}"
        cached = await self.cache.get(cache_key)
        if cached:
            return {"success": True, "source": "local_cache", "data": cached}

        prompt = f"""
        Generate an interview preparation guide for this job.
        Job Description: {safe_job}

        Output Requirements:
        1. 3 Technical Questions with sample answers.
        2. 2 Behavioral Questions mapped to the STAR method (Situation, Task, Action, Result).
        3. A 'Cheat Sheet' of key company values to mention.

        Return ONLY the guide text.
        """

        async def llm_call():
            from core.ai.llm_client import get_llm_client

            client = get_llm_client()
            response = await client.chat_completion(
                None,
                [
                    {
                        "role": "system",
                        "content": "You are an expert career coach specialized in STAR method interview preparation.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return (
                response.choices[0].message.content
                if hasattr(response, "choices")
                else str(response)
            )

        llm_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        def local_call():
            return "1. Tell me about yourself. 2. What are your strengths? 3. Why do you want this job?"

        result_data = await smart_route(llm_call, local_call)

        final_result = {
            "success": True,
            "data": result_data,
            "source": "cloud" if "Tell me about yourself" not in str(result_data) else "local"
        }

        if final_result["success"]:
            await self.cache.set(cache_key, result_data)
        return final_result

    # --- Workflow 7: STAR Feedback Engine ---
    async def provide_star_feedback(
        self, question: str, response: str
    ) -> Dict[str, Any]:
        """Provides AI feedback on an interview response using the STAR framework."""
        prompt = f"""
        Analyze the following interview response using the STAR method (Situation, Task, Action, Result).
        Question: {question}
        User Response: {response}

        Return a critique including:
        1. STAR Completeness (which parts are missing?).
        2. Impact Score (0-10).
        3. A suggested 'Better Version' of the answer.
        """

        async def llm_call():
            from core.ai.llm_client import get_llm_client

            client = get_llm_client()
            response = await client.chat_completion(
                None,
                [
                    {
                        "role": "system",
                        "content": "You are an elite interview coach providing specific, actionable STAR method feedback.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return (
                response.choices[0].message.content
                if hasattr(response, "choices")
                else str(response)
            )

        llm_call.required_envs = [["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]]

        def local_call():
            return "Local STAR feedback: Ensure you mention a specific result with numbers."

        result_data = await smart_route(llm_call, local_call)

        return {
            "success": True,
            "data": result_data,
            "source": "cloud" if "Local STAR" not in str(result_data) else "local"
        }

    # --- Workflow 8: Voice Mock Interview ---
    async def mock_interview_voice(self, audio_data: Any) -> Dict[str, Any]:
        """Workflow 7: Integration placeholder for voice-to-text and AI response."""
        # This would typically involve Whisper (Tier 1) or local STT
        return {
            "success": True,
            "source": "placeholder",
            "data": "Voice integration requires active audio streaming.",
        }

    # --- Workflow 8: Salary & Location Insights ---
    async def get_salary_insights(self, role: str, location: str) -> Dict[str, Any]:
        """Workflow 8: Salary data from Teleport or DDG."""
        try:
            import requests

            # Simple Teleport API check for cities
            city = location.lower().replace(" ", "-")
            res = requests.get(
                f"https://api.teleport.org/api/urban_areas/slug:{city}/salaries/"
            )
            if res.status_code == 200:
                return {"success": True, "source": "teleport_api", "data": res.json()}

            # Fallback to a static or search-based estimate
            return {
                "success": True,
                "source": "static_data",
                "data": {"estimated_range": "$80k - $120k"},
            }
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
