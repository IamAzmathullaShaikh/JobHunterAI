import io
from pypdf import PdfReader
import docx

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extracts raw plain text from PDF, DOCX, or TXT file streams."""
    ext = filename.lower().split(".")[-1]
    
    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        text_pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text_pages).strip()
        
    elif ext == "docx":
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
        
    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore").strip()
        
    else:
        raise ValueError("Unsupported format. Please upload a PDF, DOCX, or TXT document.")