import asyncio
import sys
from loguru import logger
from database.connection import async_engine
from database.models import Base

async def init_system_db():
    """Initializes physical schema mapping bounds over the SQLite engine database connection."""
    logger.info("Initializing structural system data storage models...")
    async with async_engine.begin() as conn:
        # Fallback automated table schema layout generator if alembic hasn't migrated tracking nodes yet
        await conn.run_sync(Base.metadata.create_all)
    logger.success("Database engine storage bounds configured successfully.")

if __name__ == "__main__":
    print("====================================================")
    print("     JobHunterAI Platform Ingestion Blueprint       ")
    print("====================================================")
    try:
        asyncio.run(init_system_db())
        logger.info("System structures validated. Fire up your dashboard using: streamlit run dashboard/Home.py")
    except Exception as e:
        logger.critical(f"Platform setup routine execution failure occurred: {str(e)}")
        sys.exit(1)
