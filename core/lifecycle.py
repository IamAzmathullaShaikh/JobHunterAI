import asyncio
import logging

from core.container import container
from core.provider_loader import ProviderLoader
from core.providers.telemetry_events import (ApplicationReady,
                                             ApplicationStarting,
                                             ApplicationStopping)

logger = logging.getLogger(__name__)


class AppLifecycleManager:
    """
    Orchestrates the global startup and shutdown sequences for the platform.
    Ensures infrastructure is initialized in the correct order.
    """

    @staticmethod
    async def startup() -> None:
        """Sequential startup of all platform infrastructure."""
        if container.registry.is_frozen:
            logger.warning("Platform already started. Skipping startup sequence.")
            return

        # 1. Start Telemetry (The observer starts first)
        container.telemetry_dispatcher.publish(ApplicationStarting())
        logger.info("Platform startup sequence initiated...")

        # 2. Discover and Register Providers
        ProviderLoader.load_all(container.registry)

        # 3. Initialize Database
        from core.database.connection import async_engine
        from core.database.models import Base

        logger.info("Initializing database schema...")
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialization successful.")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # In production, we might want to fail-fast here

        # 4. Freeze Registry (Finalize configuration)
        container.registry.freeze()

        # 5. Emit Final Ready Event
        container.telemetry_dispatcher.publish(ApplicationReady())
        logger.info("Platform is READY.")

    @staticmethod
    async def shutdown() -> None:
        """Graceful cleanup of all resources."""
        container.telemetry_dispatcher.publish(ApplicationStopping())
        logger.info("Platform shutdown sequence initiated...")

        # 1. Shutdown Provider Manager (closes all SDK connections)
        await container.provider_manager.shutdown()

        # 2. Flush and Shutdown Telemetry
        # (Future: ensure exporters have sent all data)

        logger.info("Platform shutdown complete.")
