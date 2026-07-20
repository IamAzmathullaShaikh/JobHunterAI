from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger

from database.models import JobApplication, ApplicationStatus
from schemas.ai import JobApplicationCreate, JobApplicationDTO, ApplicationStatusDTO

class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def initialize_application(self, app_data: JobApplicationCreate) -> JobApplicationDTO:
        """Pins a tracking context initialization onto an application pipeline route."""
        db_app = JobApplication(
            job_id=app_data.job_id,
            status=ApplicationStatus[app_data.status.name],
            notes=app_data.notes
        )
        self.session.add(db_app)
        await self.session.flush()
        return JobApplicationDTO.model_validate(db_app)

    async def update_status(self, app_id: int, new_status: ApplicationStatusDTO, notes: Optional[str] = None) -> JobApplicationDTO:
        """Transitions application pipelines across state-machine boundaries dynamically."""
        stmt = select(JobApplication).where(JobApplication.id == app_id)
        result = await self.session.execute(stmt)
        db_app = result.scalar_one_or_none()
        
        if not db_app:
            raise ValueError(f"Target system pipeline tracking tracking sequence ID {app_id} does not exist.")
            
        db_app.status = ApplicationStatus[new_status.name]
        if notes:
            db_app.notes = notes
            
        await self.session.flush()
        return JobApplicationDTO.model_validate(db_app)