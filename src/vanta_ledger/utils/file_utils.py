#!/usr/bin/env python3
"""
Secure File Upload Utilities
Handles secure file uploads, validation, and storage
"""

import os
import uuid
import hashlib
import mimetypes
import magic
from pathlib import Path
from typing import Optional, Tuple, List
from fastapi import UploadFile, HTTPException, status
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class SecureFileHandler:
    """Secure file upload and handling utilities"""
    
    def __init__(self):
        self.allowed_extensions = set(settings.ALLOWED_FILE_EXTENSIONS)
        self.max_file_size = settings.MAX_FILE_SIZE
        
        # MIME type validation
        self.allowed_mime_types = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/msword': '.doc',
            'text/plain': '.txt',
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/tiff': '.tiff',
            'image/bmp': '.bmp'
        }
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded file for security"""
        try:
            # Check file size
            if file.size and file.size > self.max_file_size:
                return False, f"File size exceeds maximum allowed size of {self.max_file_size} bytes"
            
            # Check file extension
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in self.allowed_extensions:
                return False, f"File extension '{file_extension}' is not allowed"
            
            # Read file content for MIME type validation
            content = file.file.read(2048)  # Read first 2KB for magic number detection
            file.file.seek(0)  # Reset file pointer
            
            # Validate MIME type using python-magic
            try:
                detected_mime = magic.from_buffer(content, mime=True)
                if detected_mime not in self.allowed_mime_types:
                    return False, f"MIME type '{detected_mime}' is not allowed"
                
                # Double-check extension matches MIME type
                expected_extension = self.allowed_mime_types[detected_mime]
                if file_extension != expected_extension:
                    return False, f"File extension '{file_extension}' does not match detected MIME type '{detected_mime}'"
                    
            except Exception as e:
                logger.warning(f"Could not detect MIME type for file {file.filename}: {str(e)}")
                # Fallback to extension-only validation
                pass
            
            return True, "File validation successful"
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False, f"File validation failed: {str(e)}"
    
    def generate_secure_filename(self, original_filename: str, user_id: str) -> str:
        """Generate a secure, unique filename"""
        # Get file extension
        file_extension = Path(original_filename).suffix.lower()
        
        # Generate unique identifier
        unique_id = str(uuid.uuid4())
        
        # Create hash of original filename for reference
        filename_hash = hashlib.sha256(original_filename.encode()).hexdigest()[:8]
        
        # Combine user ID, hash, and unique ID for secure filename
        secure_filename = f"{user_id}_{filename_hash}_{unique_id}{file_extension}"
        
        return secure_filename
    
    def get_safe_upload_path(self, filename: str, upload_dir: str) -> Path:
        """Get safe upload path, preventing path traversal"""
        # Normalize path to prevent directory traversal
        safe_filename = Path(filename).name  # Only get filename, not path
        
        # Create upload directory if it doesn't exist
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure the final path is within the upload directory
        final_path = upload_path / safe_filename
        
        # Security check: ensure the resolved path is within the upload directory
        try:
            final_path.resolve().relative_to(upload_path.resolve())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )
        
        return final_path
    
    def save_file_securely(self, file: UploadFile, user_id: str, upload_dir: str) -> Tuple[Path, str]:
        """Save uploaded file securely"""
        try:
            # Validate file
            is_valid, message = self.validate_file(file)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=message
                )
            
            # Generate secure filename
            secure_filename = self.generate_secure_filename(file.filename, user_id)
            
            # Get safe upload path
            file_path = self.get_safe_upload_path(secure_filename, upload_dir)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            logger.info(f"File saved securely: {file_path}")
            return file_path, secure_filename
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )
    
    def cleanup_temp_file(self, file_path: Path) -> bool:
        """Safely cleanup temporary file"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Temporary file cleaned up: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cleaning up temporary file {file_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get file information for logging and analysis"""
        try:
            stat = file_path.stat()
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "path": str(file_path),
                "exists": file_path.exists()
            }
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {"error": str(e)}

# Global instance
secure_file_handler = SecureFileHandler() 