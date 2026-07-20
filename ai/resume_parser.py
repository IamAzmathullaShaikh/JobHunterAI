import json
import groq
from groq import AsyncGroq
from config.settings import settings
from schemas.user_profile import ParsedProfileDTO
from utils.logger import logger

class ResumeParser:
    def __init__(self):
        # 1. Defensive key check
        api_key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
        if not api_key:
            logger.error("GROQ_API_KEY is missing or empty! Check your .env file.")
            raise ValueError("GROQ_API_KEY is not configured in .env file.")
            
        # 2. Initialize Groq client with explicit timeout controls
        self.client = AsyncGroq(
            api_key=api_key,
            timeout=30.0,
            max_retries=2
        )
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    async def parse_resume(self, raw_resume_text: str) -> ParsedProfileDTO:
        logger.info("Executing LLM profile analysis & skill extraction...")
        
        prompt = f"""
        Analyze the following candidate resume text and extract structured profile parameters.

        Resume Text:
        ---
        {raw_resume_text[:4500]}
        ---

        Return strict JSON strictly matching this structure:
        {{
            "full_name": "Full Name or null",
            "target_roles": ["Role 1", "Role 2"],
            "key_skills": ["Skill 1", "Skill 2", "Skill 3"],
            "education": ["Degree/Institution"],
            "total_experience_years": 3.5,
            "experience_highlights": ["Highlight 1", "Highlight 2"],
            "recommended_search_queries": ["Optimized Query 1", "Optimized Query 2"]
        }}
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI career analyst extracting structured candidate profiles into JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            parsed_json = json.loads(raw_content)
            
            dto = ParsedProfileDTO(**parsed_json)
            logger.success(f"Parsed profile for '{dto.full_name or 'Candidate'}': {len(dto.key_skills)} skills identified.")
            return dto

        except groq.APIConnectionError as conn_err:
            logger.error(f"Groq API connection lost or blocked by network: {conn_err}")
            raise RuntimeError("Could not connect to Groq API servers. Verify internet connection and GROQ_API_KEY validity.") from conn_err
        except groq.AuthenticationError as auth_err:
            logger.error(f"Groq API key authentication failed: {auth_err}")
            raise RuntimeError("Invalid GROQ_API_KEY supplied in .env file.") from auth_err
        except Exception as e:
            logger.error(f"Resume extraction failed: {str(e)}")
            raise e