import json
from ai.llm_client import get_llm_client
from config.settings import settings
from schemas.user_profile import ParsedProfileDTO
from utils.logger import logger

class ResumeParser:
    def __init__(self):
        # Initialize client, will be None if keys are missing
        self.client = get_llm_client()
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
            response = await self.client.chat_completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI career analyst extracting structured candidate profiles into JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw_content = response.choices[0].message.content
            parsed_json = json.loads(raw_content)
            
            dto = ParsedProfileDTO(**parsed_json)
            logger.success(f"Parsed profile for '{dto.full_name or 'Candidate'}': {len(dto.key_skills)} skills identified.")
            return dto

        except Exception as e:
            logger.error(f"Resume extraction failed: {str(e)}")
            raise e
