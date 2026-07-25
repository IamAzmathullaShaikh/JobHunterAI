import re
from typing import Dict, List

from domain.discovery.entities import ATSScore, Recommendation
from domain.profile.candidate import Candidate
from domain.profile.entities import Resume


class ATSScoringService:
    """
    Evaluates resume structural quality and completeness for ATS systems.
    Uses deterministic heuristic rules.
    """

    ACTION_VERBS = {
        "managed",
        "developed",
        "implemented",
        "increased",
        "decreased",
        "orchestrated",
        "led",
        "designed",
    }

    @staticmethod
    def analyze(resume: Resume, candidate: Candidate) -> ATSScore:
        section_scores = {}
        recommendations = []

        # 1. Contact Information (Weight: 20%)
        contact = candidate.contact_info
        contact_score = 1.0
        if not contact.phone:
            contact_score -= 0.4
            recommendations.append(
                Recommendation(
                    "contact", "Missing phone number for recruiter outreach.", "high"
                )
            )
        if not contact.linkedin_url:
            contact_score -= 0.2
            recommendations.append(
                Recommendation(
                    "contact",
                    "Add a LinkedIn profile to build professional trust.",
                    "medium",
                )
            )
        section_scores["contact"] = max(contact_score, 0.0)

        # 2. Summary & Completeness (Weight: 30%)
        text = resume.current_version.raw_text
        completeness = resume.calculate_completeness()
        section_scores["completeness"] = completeness
        if completeness < 0.6:
            recommendations.append(
                Recommendation(
                    "content",
                    "Resume content is too brief; elaborate on key projects.",
                    "high",
                )
            )

        # 3. Impact & Quantification (Weight: 30%)
        quant_count = len(re.findall(r"\d+%", text)) + len(re.findall(r"\$\d+", text))
        quant_score = min(quant_count / 5, 1.0)  # Target at least 5 metrics
        section_scores["quantification"] = round(quant_score, 2)
        if quant_score < 0.5:
            recommendations.append(
                Recommendation(
                    "impact",
                    "Use more data (%, $) to quantify your achievements.",
                    "medium",
                )
            )

        # 4. Action Verbs (Weight: 20%)
        words = set(text.lower().split())
        verb_match = words.intersection(ATSScoringService.ACTION_VERBS)
        verb_score = min(len(verb_match) / len(ATSScoringService.ACTION_VERBS), 1.0)
        section_scores["verbs"] = round(verb_score, 2)
        if verb_score < 0.4:
            recommendations.append(
                Recommendation(
                    "language",
                    "Use strong action verbs (e.g., 'orchestrated', 'implemented').",
                    "low",
                )
            )

        # 5. Overall Weighted Score
        overall = (
            (section_scores["contact"] * 0.2)
            + (section_scores["completeness"] * 0.3)
            + (section_scores["quantification"] * 0.3)
            + (section_scores["verbs"] * 0.2)
        )

        return ATSScore(
            resume_id=resume.id,
            overall_score=round(overall, 2),
            section_scores=section_scores,
            recommendations=recommendations,
        )
