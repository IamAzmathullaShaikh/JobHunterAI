import hashlib
import json
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import LLMCache
from utils.logger import logger

class AICache:
    """
    Persistent cache for AI responses to minimize costs and latency.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    def _generate_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    async def get(self, text: str) -> Optional[Dict[str, Any]]:
        """Retrieves a cached response if it exists."""
        text_hash = self._generate_hash(text)
        stmt = select(LLMCache).where(LLMCache.hash == text_hash)
        result = await self.db.execute(stmt)
        cache_entry = result.scalar_one_or_none()

        if cache_entry:
            logger.info(f"Cache hit for text hash: {text_hash[:8]}...")
            return cache_entry.payload
        return None

    async def set(self, text: str, payload: Dict[str, Any]):
        """Caches a new response."""
        text_hash = self._generate_hash(text)
        # Check if exists first to avoid duplicates
        existing = await self.get(text)
        if existing:
            return

        new_cache = LLMCache(
            hash=text_hash,
            payload=payload
        )
        self.db.add(new_cache)
        await self.db.commit()
        logger.info(f"Cached new response for text hash: {text_hash[:8]}...")
