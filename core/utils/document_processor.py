import io
import logging
from typing import Optional

try:
    import docx
except ImportError:
    docx = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

logger = logging.getLogger("jobhunterai.document_processor")

def extract_text_from_bytes(file_bytes: bytes, filename: str) -> Optional[str]:
    """Universal text extractor for PDF and DOCX."""
    ext = filename.lower().split(".")[-1]

    try:
        if ext == "pdf":
            if not pdfplumber:
                logger.error("pdfplumber not installed.")
                return None
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                return "\n".join([page.extract_text() or "" for page in pdf.pages]).strip()

        elif ext == "docx":
            if not docx:
                logger.error("python-docx not installed.")
                return None
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()]).strip()

        elif ext == "txt":
            return file_bytes.decode("utf-8", errors="ignore").strip()

    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}")
        return None

    return None
