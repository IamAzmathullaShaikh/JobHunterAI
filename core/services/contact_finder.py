import json
import logging
from typing import Dict, Optional

import groq
from groq import AsyncGroq
from pydantic import BaseModel, Field

from core.config.settings import settings

logger = logging.getLogger(__name__)


class ContactFinderDTO(BaseModel):
    company_name: str
    target_role: str
    suggested_search_queries: Dict[str, str] = Field(
        ...,
        description="Pre-formatted search links for Google, LinkedIn, and X/Twitter to find decision makers.",
    )
    cold_outreach_dm_template: str = Field(
        ...,
        description="A concise, 3-sentence cold DM template for reaching out to founders/recruiters.",
    )


class ContactFinderService:
    def __init__(self):
        from core.ai.llm_client import get_llm_client
        self.client = get_llm_client()

    async def find_hiring_contacts(
        self, company_name: str, role_title: str
    ) -> ContactFinderDTO:
        logger.info(
            f"Generating decision-maker search vectors and cold DM for '{company_name}'..."
        )

        # Construct direct Google X-Ray search query URLs
        linkedin_query = f'site:linkedin.com/in/ "{company_name}" AND ("Founder" OR "Hiring Manager" OR "Recruiter" OR "HR")'
        twitter_query = f'site:twitter.com OR site:x.com "{company_name}" AND ("hiring" OR "founder" OR "recruiter")'

        search_urls = {
            "LinkedIn Decision Makers": f"https://www.google.com/search?q={linkedin_query.replace(' ', '+')}",
            "Twitter/X Outreach Search": f"https://www.google.com/search?q={twitter_query.replace(' ', '+')}",
            "Company Careers Hub": f"https://www.google.com/search?q={company_name.replace(' ', '+')}+careers",
        }

        template = (
            f"Hi [Name], saw that {company_name} is growing its team for the {role_title} role. "
            f"I recently led key initiatives in territory growth and sales analytics with strong execution metrics. "
            f"I'd love to share a quick 2-minute summary of how I can contribute to {company_name}'s goals!"
        )

        try:
            prompt = f"""
            Create a high-converting, personalized 3-sentence Cold DM for reaching out to a Founder or Hiring Manager at {company_name} regarding the {role_title} role.
            Output JSON: {{"cold_dm": "..."}}
            """
            response = await self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}]
            )

            content = (
                response.choices[0].message.content
                if hasattr(response, "choices")
                else str(response)
            )

            import re
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                data = json.loads(match.group())
                template = data.get("cold_dm", template)
        except Exception as err:
            logger.warning(f"Falling back to static DM template: {err}")

        return ContactFinderDTO(
            company_name=company_name,
            target_role=role_title,
            suggested_search_queries=search_urls,
            cold_outreach_dm_template=template,
        )
