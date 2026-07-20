import json
import groq
from groq import AsyncGroq
from config.settings import settings
from schemas.ai_analysis import AIAnalysisCreate
from utils.logger import logger

class JobMatcher:
    def __init__(self):
        api_key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
        if not api_key:
            logger.warning("GROQ_API_KEY is empty! AI matching will operate in mock mode.")
            self.client = None
        else:
            self.client = AsyncGroq(api_key=api_key, timeout=30.0, max_retries=2)
            
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    async def analyze_fit(self, job_description: str, user_profile: str) -> AIAnalysisCreate:
        logger.debug(f"Initiating free AI compatibility match analysis via model: {self.model}")
        
        if not self.client:
            return AIAnalysisCreate(
                match_score=50.0,
                fit_summary="Groq API key unconfigured. Default fit score assigned.",
                keywords_matched=[],
                keywords_missing=[]
            )

        prompt = f"""
        Evaluate the fit compatibility between the candidate profile and the job description.

        Candidate Profile:
        ---
        {user_profile[:3000]}
        ---

        Job Description:
        ---
        {job_description[:3000]}
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical recruiter analyzing resume-to-job alignment."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            
            dto = AIAnalysisCreate(
                match_score=float(data.get("match_score", 50.0)),
                fit_summary=data.get("fit_summary", "Alignment evaluation complete."),
                keywords_matched=data.get("keywords_matched", []),
                keywords_missing=data.get("keywords_missing", [])
            )
            logger.success(f"Successfully evaluated job fit via Groq. Score: {dto.match_score:.1f}%")
            return dto

        except Exception as e:
            logger.error(f"AI Match Analysis execution failed: {str(e)}")
            return AIAnalysisCreate(
                match_score=50.0,
                fit_summary="Evaluation degraded due to response formatting or connection timeout.",
                keywords_matched=[],
                keywords_missing=[]
            )