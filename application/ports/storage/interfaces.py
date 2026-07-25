from abc import ABC, abstractmethod
from typing import Optional


class IFileStorage(ABC):
    """
    Interface for permanent file storage (S3, R2, Local FS).
    """

    @abstractmethod
    async def save(
        self, file_content: bytes, filename: str, content_type: Optional[str] = None
    ) -> str:
        """Saves the file and returns the URI/path."""
        pass

    @abstractmethod
    async def get(self, file_id: str) -> bytes:
        """Retrieves file content."""
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """Removes a file from storage."""
        pass
