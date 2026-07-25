from core.database.connection import async_engine, get_db_session
from core.database.models import Base


async def init_db():
    """Initializes the database and creates all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Reuse the session generator
get_session = get_db_session
