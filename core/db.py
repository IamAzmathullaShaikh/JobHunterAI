from core.database.connection import get_db_session, async_engine
from core.database.models import Base

async def init_db():
    """Initializes the database and creates all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Reuse the session generator
get_session = get_db_session
