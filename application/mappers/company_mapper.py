from domain.discovery.company import Company


class CompanyMapper:
    """Maps between Company domain entities and DTOs."""

    @staticmethod
    def to_output_dto(company: Company) -> dict:
        return {
            "id": str(company.id),
            "name": company.name,
            "industry": company.industry,
            "active_jobs_count": len(company.active_jobs()),
        }
