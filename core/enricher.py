import os
import json
from typing import List, Dict, Any, Optional
from jinja2 import Template
from smart_router import router
from privacy import redactor
from utils.logger import logger

class Enricher:
    """
    Module for finding recruiters/decision-makers and drafting cold outreach emails.
    """

    def __init__(self):
        self.email_templates = {
            "standard": "Dear {{ person_name }},\n\nI recently came across the {{ job_title }} opening at {{ company_name }} and was immediately drawn to the innovative work your team is doing. My background in {{ skills }} aligns well with the requirements, particularly {{ highlight }}.\n\nI've attached my resume for your review and would love to connect to discuss how I can contribute to {{ company_name }}.\n\nBest regards,\n{{ user_name }}",
            "executive": "Hi {{ person_name }},\n\nI am reaching out regarding the {{ job_title }} role at {{ company_name }}. With my experience leading teams in {{ department }}, I am confident I can drive significant value for your organization.\n\nI would appreciate a brief conversation at your convenience.\n\nRegards,\n{{ user_name }}"
        }

    async def find_decision_makers(self, company: str, department: str = "Engineering") -> List[Dict[str, Any]]:
        """
        Tiered Recruiter Finder.
        Tier 1: Apify/Hunter.io (Placeholder)
        Tier 2: Search (Placeholder)
        Tier 3: Pattern Generator
        """
        # For now, implementing Tier 3: Local Pattern Generator
        # In a full build, this would use Apify actors
        logger.info(f"Finding decision-makers for {company} in {department}...")

        # Mocking discovery (to be replaced with actual scraping logic)
        leads = [
            {
                "person_name": f"Jane Doe",
                "title": f"Head of {department}",
                "email": f"jane.doe@{company.lower().replace(' ', '')}.com",
                "linkedin_url": f"https://linkedin.com/in/janedoe-{company.lower()}",
                "confidence_score": 0.85
            },
            {
                "person_name": f"John Recruiter",
                "title": f"Technical Recruiter",
                "email": f"john.r@{company.lower().replace(' ', '')}.com",
                "linkedin_url": f"https://linkedin.com/in/johnrecruiter-{company.lower()}",
                "confidence_score": 0.9
            }
        ]
        return leads

    async def draft_outreach(
        self,
        resume_text: str,
        job_title: str,
        company: str,
        recruiter_name: str,
        user_name: str
    ) -> Dict[str, Any]:
        """Drafts a cold outreach email using the 3-Tier AI router."""

        redacted_resume, _ = redactor.redact(resume_text)

        async def groq_call():
            from ai.llm_client import get_llm_client
            client = get_llm_client()
            prompt = f"Write a cold outreach email to {recruiter_name} at {company} for the {job_title} role. Use this resume context: {redacted_resume}"
            return await client.chat_completion("llama-3.3-70b-versatile", [{"role": "user", "content": prompt}])

        def local_call():
            template = Template(self.email_templates["standard"])
            return template.render(
                person_name=recruiter_name,
                job_title=job_title,
                company_name=company,
                skills="relevant technologies",
                highlight="my recent projects",
                user_name=user_name
            )

        return await router.route("outreach_drafting", groq_call, groq_call, local_call)

enricher = Enricher()
