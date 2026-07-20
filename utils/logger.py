import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

def configure_logging():
    """Initializes multi-sink rolling log directories for isolated debugging."""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # Remove default standard out handler to prevent duplicate console printing
    logger.remove()
    
    # 1. Main Console Output (Clean, human-readable formatting)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO"
    )
    
    # 2. Scraper Target Log Sink
    logger.add(
        log_dir / "scraper.log",
        filter=lambda record: "scrapers" in record["name"] or "scraper" in record["extra"],
        rotation="10 MB",
        retention="7 days",
        level="DEBUG"
    )
    
    # 3. AI Target Log Sink
    logger.add(
        log_dir / "ai.log",
        filter=lambda record: "ai" in record["name"] or "ai" in record["extra"],
        rotation="10 MB",
        retention="14 days",
        level="DEBUG"
    )
    
    # 4. Global System Catch-All File Log
    logger.add(
        log_dir / "system.log",
        rotation="20 MB",
        retention="30 days",
        level="WARNING",
        compression="zip"
    )

# Run instantly upon framework initialization
configure_logging()