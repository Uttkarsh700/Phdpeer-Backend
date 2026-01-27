"""File handling utilities."""
import os
import uuid
from pathlib import Path
from typing import Tuple


def get_upload_directory() -> Path:
    """
    Get the directory for storing uploaded files.
    
    Returns:
        Path to upload directory
    """
    # Default to uploads directory in project root
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    return upload_dir


def generate_unique_filename(original_filename: str) -> Tuple[str, str]:
    """
    Generate a unique filename while preserving the extension.
    
    Args:
        original_filename: Original filename from upload
        
    Returns:
        Tuple of (unique_filename, file_extension)
    """
    file_extension = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{file_extension}"
    return unique_name, file_extension


def save_upload_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded file to storage.
    
    Args:
        file_content: File content as bytes
        filename: Filename to save as
        
    Returns:
        Relative path to saved file
    """
    upload_dir = get_upload_directory()
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)


def validate_file_type(filename: str, allowed_types: list) -> bool:
    """
    Validate file type based on extension.
    
    Args:
        filename: Filename to validate
        allowed_types: List of allowed extensions (e.g., ['.pdf', '.docx'])
        
    Returns:
        True if valid, False otherwise
    """
    file_extension = Path(filename).suffix.lower()
    return file_extension in [ext.lower() for ext in allowed_types]


def get_file_size(file_content: bytes) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_content: File content as bytes
        
    Returns:
        File size in bytes
    """
    return len(file_content)
