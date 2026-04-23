"""
CoreAgent-2 — Document Loader Pipeline
Routes uploaded files through the correct LangChain loader and optionally
applies text splitting.
"""
import os
import tempfile
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PIL import Image

# Tesseract is pre-installed on the lab machine
import pytesseract


# Reusable text splitter for chunking
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)


class DocumentProcessor:
    """Handles parsing and chunking of various file types."""

    @staticmethod
    def process_file(file_path: str, chunk: bool = True) -> list[Document]:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return DocumentProcessor._load_pdf(file_path, chunk)
        elif ext in (".txt", ".md", ".csv"):
            return DocumentProcessor._load_text(file_path, chunk)
        elif ext in (".png", ".jpg", ".jpeg"):
            return DocumentProcessor._load_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def _load_pdf(file_path: str, chunk: bool = True) -> list[Document]:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        if chunk:
            return _splitter.split_documents(pages)
        return pages

    @staticmethod
    def _load_text(file_path: str, chunk: bool = True) -> list[Document]:
        loader = TextLoader(file_path)
        docs = loader.load()
        if chunk:
            return _splitter.split_documents(docs)
        return docs

    @staticmethod
    def _load_image(file_path: str) -> list[Document]:
        """OCR extraction via Tesseract (pre-installed on the lab machine)."""
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return [
                Document(
                    page_content=text.strip() or "[Image contained no readable text]",
                    metadata={"source": file_path, "type": "image"},
                )
            ]
        except Exception as e:
            return [
                Document(
                    page_content=f"[Failed to process image: {e}]",
                    metadata={"source": file_path},
                )
            ]


def process_upload(uploaded_bytes: bytes, filename: str) -> list[Document]:
    """
    Process bytes from a Streamlit UploadedFile.
    Writes to a temp file, processes, cleans up.
    """
    ext = Path(filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_bytes)
        tmp_path = tmp.name

    try:
        documents = DocumentProcessor.process_file(tmp_path)
        for doc in documents:
            doc.metadata["source"] = filename
        return documents
    finally:
        os.unlink(tmp_path)
