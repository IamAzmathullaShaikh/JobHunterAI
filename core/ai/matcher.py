import json
import re
import os
from ai.llm_client import get_llm_client
from config.settings import settings
from schemas.ai_analysis import AIAnalysisCreate
from utils.logger import logger

class JobMatcher:
    def __init__(self):
        try:
            self.client = get_llm_client()
            # Determine model based on provider
            provider = os.getenv("AI_PROVIDER", "groq").lower()
            if provider == "groq":
                self.model = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
            elif provider == "gemini":
                self.model = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")
            else:
                self.model = None # Default from client
        except Exception as e:
            logger.warning(f"LLM Client initialization failed: {e}. Using heuristic fallback.")
            self.client = None

    def _heuristic_match(self, job_desc: str, user_profile: str) -> AIAnalysisCreate:
        """Determines match score using keyword intersection when LLM is unavailable."""
        job_lower = job_desc.lower()
        profile_lower = user_profile.lower()

        # Extract potential keywords from profile (simple word split for now, could be improved)
        # In a real scenario, we'd use a predefined list of tech skills
        tech_keywords = ["python", "java", "react", "node", "typescript", "aws", "docker", "kubernetes", "sql", "nosql", "fastapi", "express", "kotlin", "swift", "flutter", "react native"]

        matched = [k for k in tech_keywords if k in job_lower and k in profile_lower]
        missing = [k for k in tech_keywords if k in job_lower and k not in profile_lower]

        score = 50.0 # Base score
        if tech_keywords:
            job_tech_count = len([k for k in tech_keywords if k in job_lower])
            if job_tech_count > 0:
                score = (len(matched) / job_tech_count) * 100
        
        return AIAnalysisCreate(
            match_score=round(score, 1),
            fit_summary="Heuristic Match: Evaluated based on technical keyword intersection (Offline Fallback).",
            keywords_matched=matched,
            keywords_missing=missing,
            quota_safe=True
        )

    async def analyze_fit(self, job_description: str, user_profile: str) -> AIAnalysisCreate:
        if not self.client:
            return self._heuristic_match(job_description, user_profile)

        prompt = f"""
        Evaluate the fit compatibility between the candidate profile and the job description.

        Candidate Profile:
        ---
        {user_profile[:4000]}
        ---

        Job Description:
        ---
        {job_description[:4000]}
        ---

        Return strict JSON strictly matching this structure:
        {{
            "match_score": 85.5,
            "fit_summary": "Concise summary breakdown of candidate alignment...",
            "keywords_matched": ["Skill 1", "Skill 2"],
            "keywords_missing": ["Skill 3"]
        }}
        """

        try:
            response = await self.client.chat_completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical recruiter analyzing resume-to-job alignment."},
                    {"role": "user", "content": prompt}
                ]
            )
            data = json.loads(response.choices[0].message.content)
            
            return AIAnalysisCreate(
                match_score=float(data.get("match_score", 50.0)),
                fit_summary=data.get("fit_summary", "Alignment evaluation complete."),
                keywords_matched=data.get("keywords_matched", []),
                keywords_missing=data.get("keywords_missing", [])
            )

        except Exception as e:
            logger.error(f"AI Match Analysis execution failed: {str(e)}")
            return self._heuristic_match(job_description, user_profile)
