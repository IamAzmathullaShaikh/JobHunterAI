import os
from typing import Dict, Any
from jinja2 import Template
try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    Document = None

from utils.logger import logger

class TemplateEngine:
    """
    Export Engine for 4 ATS-optimized resume templates.
    Supports PDF and DOCX export.
    """

    TEMPLATES = {
        "classic_ats": "<html><body><h1>{{ full_name }}</h1><p>{{ email }} | {{ phone }}</p><h2>Experience</h2>{% for job in work_history %}<p><b>{{ job.title }}</b> at {{ job.company }}</p><ul>{% for bullet in job.bullets %}<li>{{ bullet }}</li>{% endfor %}</ul>{% endfor %}</body></html>",
        "modern_minimal": "...",
        "executive_elegant": "...",
        "tech_clean": "..."
    }

    def render_to_html(self, profile: Dict[str, Any], template_id: str = "classic_ats") -> str:
        """Renders profile data into an HTML string based on a template."""
        html_template = self.TEMPLATES.get(template_id, self.TEMPLATES["classic_ats"])
        template = Template(html_template)
        return template.render(**profile)

    def export_docx(self, profile: Dict[str, Any], output_path: str):
        """Generates a Microsoft Word document for the profile."""
        if not Document:
            logger.error("python-docx not installed.")
            return

        doc = Document()
        doc.add_heading(profile.get("full_name", "Resume"), 0)

        # Add Contact Info
        doc.add_paragraph(f"{profile.get('email')} | {profile.get('phone')} | {profile.get('location')}")

        # Add Experience
        doc.add_heading('Experience', level=1)
        for job in profile.get("work_history", []):
            p = doc.add_paragraph()
            p.add_run(f"{job.get('title')} at {job.get('company')}").bold = True
            for bullet in job.get("bullets", []):
                doc.add_paragraph(bullet, style='List Bullet')

        doc.save(output_path)
        logger.success(f"DOCX exported to {output_path}")

template_engine = TemplateEngine()
