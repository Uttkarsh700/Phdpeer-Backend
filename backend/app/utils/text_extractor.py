"""Text extraction utilities for PDF and DOCX files."""
import io
from typing import Optional
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None


class TextExtractionError(Exception):
    """Raised when text extraction fails."""
    pass


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract raw text from PDF file.
    
    Args:
        file_content: PDF file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        TextExtractionError: If extraction fails
    """
    if PyPDF2 is None:
        raise TextExtractionError("PyPDF2 not installed. Install with: pip install PyPDF2")
    
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    except Exception as e:
        raise TextExtractionError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """
    Extract raw text from DOCX file.
    
    Args:
        file_content: DOCX file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        TextExtractionError: If extraction fails
    """
    if Document is None:
        raise TextExtractionError("python-docx not installed. Install with: pip install python-docx")
    
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n\n".join(text_parts)
    
    except Exception as e:
        raise TextExtractionError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text(file_content: bytes, file_type: str) -> str:
    """
    Extract text from file based on file type.
    
    Args:
        file_content: File content as bytes
        file_type: File extension (pdf, docx)
        
    Returns:
        Extracted text as string
        
    Raises:
        TextExtractionError: If extraction fails or file type not supported
    """
    file_type = file_type.lower().replace(".", "")
    
    if file_type == "pdf":
        return extract_text_from_pdf(file_content)
    elif file_type == "docx":
        return extract_text_from_docx(file_content)
    else:
        raise TextExtractionError(f"Unsupported file type: {file_type}. Supported types: pdf, docx")
