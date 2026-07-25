import logging

from application.ports.providers.interfaces import IFileParserProvider
from application.results.result import Result
from application.use_cases.base import ApplicationUseCase

logger = logging.getLogger(__name__)


class ExtractResumeTextUseCase(ApplicationUseCase[tuple, str]):
    """
    Extracts raw text from a resume file (PDF/DOCX) using a specialized provider.
    """

    def __init__(self, file_parser: IFileParserProvider):
        self._file_parser = file_parser

    async def _run(self, input_data: tuple) -> Result[str]:
        file_content, content_type = input_data

        try:
            text = await self._file_parser.extract_text(file_content, content_type)

            if not text or not text.strip():
                return Result.validation_fail(
                    "Could not extract any text from the provided file."
                )

            return Result.ok(text)

        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return Result.infra_fail(f"Failed to process file: {str(e)}")

    async def execute(self, file_content: bytes, content_type: str) -> Result[str]:
        return await super().execute((file_content, content_type))
