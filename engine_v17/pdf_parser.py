"""Document text extraction — PDF, DOCX, TXT, MD.

Standalone module with graceful fallback: if a parser fails, returns
what it can with a warning rather than crashing the pipeline.
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path


def extract_text(file_path: Path) -> str:
    """Extract plain text from a document. Returns empty string on failure."""
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _extract_pdf(file_path)
        elif suffix == ".docx":
            return _extract_docx(file_path)
        elif suffix in (".txt", ".md"):
            return file_path.read_text(encoding="utf-8", errors="replace")
        else:
            warnings.warn(f"Unsupported file type: {suffix} ({file_path.name})")
            return ""
    except Exception as e:
        warnings.warn(f"Failed to extract {file_path.name}: {e}")
        return ""


def _extract_pdf(file_path: Path) -> str:
    """Extract text from PDF using pdfplumber, falling back to pdfminer."""
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        if pages:
            return "\n\n".join(pages)
    except Exception:
        pass

    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        return pdfminer_extract(str(file_path))
    except Exception:
        pass

    return ""


def _extract_docx(file_path: Path) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(str(file_path))
        return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except ImportError:
        warnings.warn("python-docx not installed — cannot read .docx files")
        return ""
    except Exception as e:
        warnings.warn(f"DOCX extraction failed: {e}")
        return ""


def extract_all(folder: Path) -> dict[Path, str]:
    """Extract text from all supported documents in a folder.

    Returns {file_path: extracted_text} for files that produced text.
    Skips temp files (starting with ~$ or .), hidden files, and unsupported types.
    """
    results = {}
    supported = {".pdf", ".docx", ".txt", ".md"}

    for file_path in sorted(folder.iterdir()):
        if file_path.is_dir():
            continue
        if file_path.name.startswith(("~$", ".")):
            continue
        if file_path.suffix.lower() not in supported:
            continue

        text = extract_text(file_path)
        if text.strip():
            results[file_path] = text

    return results


def detect_id_from_text(text: str) -> str | None:
    """Try to extract a patent/invention ID from document text.

    Looks for patterns like US8527057B2, US 8,527,057, patent number 8530, etc.
    Returns normalized ID (letters+digits, uppercase) or None.
    """
    patterns = [
        r"(?:US|US\s*)(\d{5,8}[A-Z]?\d?)",           # US8527057B2, US 8527057
        r"(?:Patent\s+(?:No\.?|Number|#)\s*:?\s*)(\d{4,8})",  # Patent No. 8530
        r"(?:Patent\s+Application\s+(?:No\.?|Number|#)\s*:?\s*)(\d{4,8})",
        r"\b(\d{5,8}[A-Z]?\d?)\b",                     # bare number 8527057
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1) if match.lastindex else match.group(0)
            normalized = re.sub(r"[^A-Za-z0-9]+", "", raw).upper()
            if len(normalized) >= 4:
                return normalized

    return None


def detect_id_from_filenames(folder: Path) -> str | None:
    """Try to extract a patent/invention ID from filenames AND the folder name.

    Checks filenames like: 8530-disclosure.pdf, US8527057.pdf, patent-8530.pdf
    Also checks the folder name itself: /path/to/8530/ or /path/to/US8527057/
    """
    # Check the folder name first (e.g., user points at a folder named "8530")
    folder_id = _extract_id_from_name(folder.name)
    if folder_id:
        return folder_id

    # Check filenames inside the folder
    for file_path in sorted(folder.iterdir()):
        if file_path.is_dir() or file_path.name.startswith(("~$", ".")):
            continue
        file_id = _extract_id_from_name(file_path.stem)
        if file_id:
            return file_id

    return None


def _extract_id_from_name(name: str) -> str | None:
    """Extract a patent/invention ID from a name string (filename or folder name)."""
    patterns = [
        r"(?:US\s*)(\d{4,8}[A-Z]?\d?)",       # US8527057, US 8530
        r"(?:patent[-_\s]*)(\d{4,8})",          # patent-8530, patent_8530
        r"(\d{4,8}[A-Z]?\d?)",                  # 8530, 8527057B2
    ]

    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            raw = match.group(1) if match.lastindex else match.group(0)
            normalized = re.sub(r"[^A-Za-z0-9]+", "", raw).upper()
            if len(normalized) >= 4:
                return normalized

    return None
