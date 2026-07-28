import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from core.database.models import JobApplication, Resume, ApplicationStatus
from core.database.connection import get_db_session
from backend.api.tracker import update_application_card
from core.schemas.api_payloads import UpdateApplicationRequest

@pytest.mark.asyncio
async def test_application_full_update():
    """Verify that all new high-intelligence fields are correctly persisted."""
    from core.database.connection import async_engine
    from core.database.models import Base

    # 0. Force schema update for test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async for db in get_db_session():
        # 1. Setup
        resume = Resume(name="Test Resume", content={"header": {}})
        db.add(resume)
        await db.commit()
        await db.refresh(resume)

        app = JobApplication(
            job_title="Intelligent Role",
            company_name="Smart Corp",
            status=ApplicationStatus.WISHLIST
        )
        db.add(app)
        await db.commit()
        await db.refresh(app)

        # 2. Update with new fields
        interview_dt = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
        req = UpdateApplicationRequest(
            application_id=app.id,
            status=ApplicationStatus.INTERVIEWING,
            notes="Ready to shine",
            salary_offered=125000.0,
            interview_date=interview_dt,
            resume_id=resume.id
        )

        class MockService:
            def __init__(self, session): self.session = session

        await update_application_card(req, job_service=MockService(db))

        # 3. Verify
        updated_app = await db.get(JobApplication, app.id)
        assert updated_app.status == ApplicationStatus.INTERVIEWING
        assert updated_app.salary_offered == 125000.0
        assert updated_app.interview_date == interview_dt
        assert updated_app.resume_id == resume.id
        assert updated_app.notes == "Ready to shine"

        break
