from application.dto.output.job_output import JobOutputDTO
from application.dto.output.matching_output import (JobMatchDTO,
                                                    MatchBreakdownDTO)
from application.mappers.location_mapper import LocationMapper
from domain.discovery.entities import Job, MatchResult


class JobMapper:
    """Maps between Job domain entities and DTOs."""

    @staticmethod
    def to_output_dto(job: Job) -> JobOutputDTO:
        return JobOutputDTO(
            id=str(job.id),
            title=job.title,
            company_name="Known",  # Need company lookup or join in a real service
            location=LocationMapper.to_dto(job.location),
            url=job.url,
            salary_range=str(job.salary_range) if job.salary_range else None,
            is_open=job.is_open(),
        )

    @staticmethod
    def to_match_result_dto(match: MatchResult) -> JobMatchDTO:
        return JobMatchDTO(
            job_id=str(match.job_id),
            overall_score=match.overall_score,
            breakdown=MatchBreakdownDTO(
                skills=match.breakdown.skills_score,
                experience=match.breakdown.experience_score,
                education=match.breakdown.education_score,
                keywords=match.breakdown.keywords_score,
                location=match.breakdown.location_score,
                salary=match.breakdown.salary_score,
            ),
            matched_skills=match.matched_skills,
            missing_skills=match.missing_skills,
            fit_summary=match.fit_summary,
        )
