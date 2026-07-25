# Resume Engine

The Resume Engine is responsible for all document processing and generation.

## 1. Parsing (Ingestion)
- Supports **PDF**, **DOCX**, and **Markdown**.
- **Process**: 
    1. Extract raw text.
    2. Segment into sections (Work Exp, Education, Skills).
    3. Use AI to structure data into a `CandidateProfile` object.
    4. Validate against a strict Pydantic schema.

## 2. Tailoring (Optimization)
- Analyzes a Job Description to find "Missing Keywords" and "Desired Skills".
- Suggests modifications to existing bullet points to better highlight relevant experience.
- Generates a "Summary of Changes" explaining why the modifications improve the match score.

## 3. Generation (Output)
- Uses **React-PDF** or **Docx.js** (depending on version) for generation.
- **Templates**:
    - **Classic**: Traditional, clean, black & white.
    - **Modern**: Two-column, subtle color accents.
    - **Minimalist**: Focus on white space and typography.
    - **Executive**: Dense, professional, optimized for senior roles.
- **ATS Friendly**: Ensures all generated documents are easily parsable by standard HR software.
