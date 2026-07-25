from typing import Any, Dict

from jinja2 import Template


class FallbackContentGenerator:
    """
    Rule-based deterministic templates for when AI is unavailable.
    """

    TEMPLATES = {
        "cover_letter": """
Dear Hiring Manager,

I am writing to express my strong interest in the {{ job_title }} position at {{ company }}.
With {{ years_exp }} years of experience and a proven track record in {{ skills }},
I am confident that I am the ideal candidate for this role.

Thank you for your consideration.

Sincerely,
{{ name }}
        """,
        "outreach": "Hi [Recruiter Name], I noticed the {{ job_title }} opening at {{ company }}. I'd love to connect and share more about my background in {{ top_skill }}.",
    }

    @staticmethod
    def generate(content_type: str, context: Dict[str, Any]) -> str:
        raw_template = FallbackContentGenerator.TEMPLATES.get(
            content_type, "Content unavailable."
        )
        template = Template(raw_template)

        # Flatten context for template
        flat_context = {
            "job_title": context.get("job", {}).get("title", "this position"),
            "company": context.get("job", {}).get("company", "your company"),
            "years_exp": context.get("candidate", {}).get(
                "experience_years", "multiple"
            ),
            "name": context.get("candidate", {}).get("name", "Applicant"),
            "skills": ", ".join(context.get("candidate", {}).get("skills", [])[:3]),
            "top_skill": context.get("candidate", {}).get(
                "skills", ["Software Development"]
            )[0],
        }

        return template.render(**flat_context)
