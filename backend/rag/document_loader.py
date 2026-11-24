import os
import unicodedata
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except Exception:
    HAS_PYMUPDF = False

try:
    import pypdf
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False


class Document:
    """Represents an extracted document or page with text and metadata."""
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"<Document source='{self.metadata.get('source')}' page={self.metadata.get('page', 1)} len={len(self.content)}>"


class AgriculturalDocumentLoader:
    """Loads and extracts text from agricultural PDF and text documents."""

    def __init__(self, documents_dir: Optional[Path] = None):
        self.documents_dir = documents_dir

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans and normalizes extracted text.
        Applies Unicode NFKC normalization, crucial for Indic scripts (Devanagari, Gujarati).
        """
        if not text:
            return ""
        # Unicode normalization for regional languages and accents
        normalized = unicodedata.normalize("NFKC", text)
        # Collapse multiple empty lines and excessive spaces
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n\s*\n+", "\n\n", normalized)
        return normalized.strip()

    def load_pdf(self, file_path: Path) -> List[Document]:
        """Loads a PDF file using PyMuPDF (fitz) or pypdf fallback."""
        docs: List[Document] = []
        file_name = file_path.name

        # Method 1: Try PyMuPDF if available
        if HAS_PYMUPDF:
            try:
                doc = fitz.open(file_path)
                for page_idx in range(len(doc)):
                    page = doc[page_idx]
                    raw_text = page.get_text("text")
                    cleaned = self.clean_text(raw_text)
                    if cleaned:
                        metadata = {
                            "source": file_name,
                            "file_path": str(file_path),
                            "page": page_idx + 1,
                            "total_pages": len(doc),
                            "file_type": "pdf",
                            "extractor": "pymupdf"
                        }
                        docs.append(Document(content=cleaned, metadata=metadata))
                doc.close()
                if docs:
                    return docs
            except Exception as e:
                print(f"[DocumentLoader] PyMuPDF failed for {file_name}: {e}. Falling back to pypdf.")

        # Method 2: pypdf (pure Python, immune to WDAC blocks)
        if HAS_PYPDF:
            try:
                reader = pypdf.PdfReader(str(file_path))
                total_pages = len(reader.pages)
                for page_idx, page in enumerate(reader.pages):
                    raw_text = page.extract_text() or ""
                    cleaned = self.clean_text(raw_text)
                    if cleaned:
                        metadata = {
                            "source": file_name,
                            "file_path": str(file_path),
                            "page": page_idx + 1,
                            "total_pages": total_pages,
                            "file_type": "pdf",
                            "extractor": "pypdf"
                        }
                        docs.append(Document(content=cleaned, metadata=metadata))
                return docs
            except Exception as e:
                print(f"[DocumentLoader] pypdf failed for {file_name}: {e}")

        raise RuntimeError(f"Could not extract text from PDF: {file_path}. Ensure pypdf or PyMuPDF is operational.")

    def load_text_file(self, file_path: Path) -> List[Document]:
        """Loads a plain text or Markdown file with UTF-8 encoding."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = self.clean_text(content)
            if cleaned:
                metadata = {
                    "source": file_path.name,
                    "file_path": str(file_path),
                    "page": 1,
                    "total_pages": 1,
                    "file_type": file_path.suffix.lstrip("."),
                    "extractor": "text"
                }
                return [Document(content=cleaned, metadata=metadata)]
        except Exception as e:
            print(f"[DocumentLoader] Failed to read text file {file_path.name}: {e}")
        return []

    def load_file(self, file_path: Path) -> List[Document]:
        """Routes loading based on file extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self.load_pdf(file_path)
        elif suffix in [".txt", ".md", ".json"]:
            return self.load_text_file(file_path)
        else:
            print(f"[DocumentLoader] Skipping unsupported file type: {file_path.name}")
            return []

    def load_all(self, directory: Optional[Path] = None) -> List[Document]:
        """Loads all supported documents from the target directory."""
        target_dir = directory or self.documents_dir
        if not target_dir or not target_dir.exists():
            return []

        all_docs: List[Document] = []
        for file_path in target_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith("."):
                docs = self.load_file(file_path)
                all_docs.extend(docs)
                print(f"[DocumentLoader] Loaded {len(docs)} page(s) from {file_path.name}")
        return all_docs
