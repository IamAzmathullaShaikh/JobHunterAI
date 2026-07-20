from openai import AsyncOpenAI
from loguru import logger
from config.settings import settings

class ResumeTailor:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def generate_optimized_bullets(self, missing_keywords: list, user_profile: str, job_context: str) -> str:
        """Generates contextual resume bullet updates to seamlessly integrate missing target keywords."""
        log = logger.bind(ai=True)
        log.debug(f"Formulating resume optimizations targeting keywords: {missing_keywords}")

        if not missing_keywords:
            return "### ATS Optimization Summary\nYour profile perfectly matches the keyword requirements for this job target."

        keywords_str = ", ".join(missing_keywords)
        
        system_prompt = (
            "You are an elite professional resume writer and career strategist specializing in clearing ATS screening filters. "
            "Your objective is to review the candidate's experience context and provide alternative, punchy resume bullet points "
            "that naturally weave in the required keywords without lying, sounding forced, or inflating experience details."
        )

        user_content = (
            f"### CRITICAL TARGET KEYWORDS TO INTEGRATE ###\n{keywords_str}\n\n"
            f"### USER PROFESSIONAL BACKGROUND PROFILE ###\n{user_profile}\n\n"
            f"### TARGET JOB CONTEXT ###\n{job_context}\n\n"
            "Provide a set of 3 to 5 highly practical, actionable resume bullet suggestions. "
            "Each suggestion must clearly use at least one missing keyword and follow the Action Verb + Context + Result pattern."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3
            )
            
            suggestions = response.choices[0].message.content
            log.success("ATS target adjustments generated successfully.")
            return suggestions
            
        except Exception as e:
            log.error(f"Failed to generate custom tailored optimizations: {str(e)}")
            return f"Optimization engine encountered an error generating bullet segments: {str(e)}"