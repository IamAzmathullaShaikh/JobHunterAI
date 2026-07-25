from typing import Dict, List, Set

from domain.discovery.entities import Job
from domain.profile.candidate import Candidate
from domain.profile.entities import Resume
from domain.shared.enums import SkillCategory
from domain.shared.value_objects import Money, SalaryRange


class ResumeScoringService:
    """
    Pure logic for calculating deterministic resume quality scores.
    NO LLMs. Rule-based assessment.
    """

    @staticmethod
    def calculate_score(resume: Resume, candidate: Candidate) -> Dict[str, float]:
        # 1. Completeness Score (0.0 to 1.0)
        completeness = resume.calculate_completeness()

        # 2. Contact Formatting (0.0 or 1.0)
        has_phone = candidate.contact_info.phone is not None
        has_linkedin = candidate.contact_info.linkedin_url is not None
        formatting = 0.5 + (0.25 if has_phone else 0) + (0.25 if has_linkedin else 0)

        # 3. Skills Coverage
        has_tech_skills = any(
            s.category == SkillCategory.TECHNICAL for s in candidate.skills
        )
        keyword_score = 1.0 if has_tech_skills else 0.5

        # 4. Overall Weighted Score
        overall = (completeness * 0.4) + (formatting * 0.3) + (keyword_score * 0.3)

        return {
            "overall_score": round(overall, 2),
            "completeness_score": round(completeness, 2),
            "formatting_score": round(formatting, 2),
            "keyword_score": round(keyword_score, 2),
        }


class ResumeSuggestionService:
    """
    Generates rule-based improvement suggestions.
    """

    @staticmethod
    def generate_suggestions(
        resume: Resume, candidate: Candidate
    ) -> List[Dict[str, str]]:
        suggestions = []

        # Contact Rules
        if not candidate.contact_info.phone:
            suggestions.append(
                {
                    "category": "contact",
                    "message": "Add a phone number to improve recruiter reachability.",
                    "impact": "high",
                }
            )

        if not candidate.contact_info.linkedin_url:
            suggestions.append(
                {
                    "category": "contact",
                    "message": "Adding a LinkedIn profile increases profile trust score by 30%.",
                    "impact": "medium",
                }
            )

        # Skills Rules
        if not candidate.skills:
            suggestions.append(
                {
                    "category": "skills",
                    "message": "No skills detected. Explicitly list core competencies to pass ATS filters.",
                    "impact": "high",
                }
            )

        # Experience Rules
        if not candidate.experiences:
            suggestions.append(
                {
                    "category": "experience",
                    "message": "Add work experience or projects to demonstrate practical application.",
                    "impact": "high",
                }
            )

        return suggestions


class SkillGapService:
    """Business logic for identifying missing competencies."""

    @staticmethod
    def identify_gaps(candidate: Candidate, job: Job) -> Set[str]:
        candidate_skills = {s.name.lower() for s in candidate.skills}
        required_skills = {s.lower() for s in job.required_skills}
        return required_skills - candidate_skills


class SalaryAnalysisService:
    """Business logic for evaluating financial alignment."""

    @staticmethod
    def is_compatible(expected: Money, job_range: SalaryRange) -> bool:
        return job_range.contains(expected)
