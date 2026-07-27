import logging
import os
import urllib.parse
from typing import Any, Dict, List

from core.ai.generator import \
    generate_cover_letter  # We can reuse this or specialized outreach
from core.ai.smart_router import route
from core.config.settings import settings

logger = logging.getLogger("jobhunterai.enricher")


# --- Cloud Primary ---
async def cloud_find_decision_makers(company: str, role: str) -> List[Dict[str, Any]]:
    """Uses Hunter.io or Apify to find verified emails/leads."""
    import requests

    # Attempt Apify first if token exists, fallback to Hunter
    apify_token = settings.APIFY_API_TOKEN
    if apify_token:
        # Placeholder for Apify enrichment logic
        pass

    hunter_key = settings.HUNTER_API_KEY
    if hunter_key:
        domain = f"{company.lower().replace(' ', '')}.com"  # Simple heuristic
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={hunter_key}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if "data" in data and "emails" in data["data"]:
                leads = []
                for email in data["data"]["emails"][:5]:
                    leads.append(
                        {
                            "person_name": f"{email.get('first_name', '')} {email.get('last_name', '')}".strip()
                            or "Verified Contact",
                            "title": email.get("position", role),
                            "email": email.get("value"),
                            "linkedin_url": email.get("linkedin_url", ""),
                            "source": "hunter.io",
                            "confidence_score": 0.9,
                        }
                    )
                return leads
        except Exception as e:
            logger.error(f"Hunter.io call failed: {e}")

    raise ValueError("Cloud providers (Apify/Hunter) returned no results or failed")


cloud_find_decision_makers.required_envs = [["APIFY_API_TOKEN", "HUNTER_API_KEY"]]


# --- Local Fallback ---
async def local_find_decision_makers(company: str, role: str) -> List[Dict[str, Any]]:
    """Returns useful LinkedIn/Google search links for manual exploration when cloud keys are missing."""
    logger.info(f"Local fallback: Providing discovery vectors for {company}")

    q_linkedin = urllib.parse.quote(f'site:linkedin.com/in/ "{company}" "{role}"')
    q_google = urllib.parse.quote(f'"{company}" "{role}" recruiter email')

    return [
        {
            "person_name": f"{role} Search (LinkedIn)",
            "title": "Manual Discovery",
            "email": "key-required@hunter.io",
            "type": "discovery_card",
            "linkedin_url": f"https://www.google.com/search?q={q_linkedin}",
            "desc": "Use Google X-Ray to find hiring managers directly on LinkedIn.",
            "source": "local_vectors",
            "confidence_score": 0.5,
            "match_explanation": "Recommended: Provide an Apify or Hunter.io key for automated contact extraction."
        },
        {
            "person_name": f"{company} Talent Search",
            "title": "Public Directory",
            "email": "key-required@apify.com",
            "type": "discovery_card",
            "linkedin_url": f"https://www.google.com/search?q={q_google}",
            "desc": "Search for public email patterns and recruiter directories.",
            "source": "local_vectors",
            "confidence_score": 0.4,
            "match_explanation": "Automated enrichment is currently disabled due to missing API keys."
        }
    ]


local_find_decision_makers.safe_placeholder = []


# --- Public API & Compatibility Class ---
class Enricher:
    """Backward-compatible class for recruiter discovery and outreach."""

    async def find_decision_makers(
        self, company: str, role: str = "Engineering"
    ) -> List[Dict[str, Any]]:
        return await route(
            cloud_find_decision_makers, local_find_decision_makers, company, role
        )

    async def draft_outreach(
        self,
        resume_text: str,
        job_title: str,
        company: str,
        recruiter_name: str,
        user_name: str,
    ) -> Dict[str, Any]:
        """Drafts a cold outreach email by calling the generator."""
        from core.ai.generator import generate_cover_letter

        # We'll treat the outreach as a short cover letter for simplicity in this tiering
        candidate = {
            "full_name": user_name,
            "resume_text": resume_text,
            "key_skills": ["Software Engineering"],  # Heuristic if not parsed
        }
        job = {
            "title": job_title,
            "company_name": company,
            "recruiter_name": recruiter_name,
        }

        res = await generate_cover_letter(candidate, job)
        return {"success": True, "source": res["source"], "data": res["cover_letter"]}


enricher = Enricher()


async def find_decision_makers(company: str, role: str) -> List[Dict[str, Any]]:
    return await route(
        cloud_find_decision_makers, local_find_decision_makers, company, role
    )
