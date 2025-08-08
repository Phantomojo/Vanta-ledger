#!/usr/bin/env python3
"""
Input Validation and Sanitization Utilities
Prevents SQL injection, XSS, and other injection attacks
"""

import re
import uuid
from typing import Any, Optional, Union, List
from datetime import datetime
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|/\*|\*/)",
            r"(\b(WAITFOR|DELAY)\b)",
            r"(\b(SLEEP)\b\s*\(\s*\d+\s*\))",
            r"(\b(BENCHMARK)\b\s*\(\s*\d+\s*,)",
            r"(\b(LOAD_FILE)\b\s*\()",
            r"(\b(INTO\s+OUTFILE|INTO\s+DUMPFILE)\b)",
            r"(\b(UNION\s+ALL)\b)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<img[^>]*on\w+\s*=",
            r"<a[^>]*on\w+\s*=",
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%c0%af",
            r"\.\.%c1%9c",
        ]
        
        # Compile patterns for efficiency
        self.sql_regex = re.compile("|".join(self.sql_patterns), re.IGNORECASE)
        self.xss_regex = re.compile("|".join(self.xss_patterns), re.IGNORECASE)
        self.path_traversal_regex = re.compile("|".join(self.path_traversal_patterns), re.IGNORECASE)
    
    def validate_integer(self, value: Any, min_value: Optional[int] = None, 
                        max_value: Optional[int] = None, field_name: str = "value") -> int:
        """Validate and convert to integer"""
        try:
            if isinstance(value, str):
                # Check for SQL injection in string representation
                if self.sql_regex.search(value):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid {field_name}: contains suspicious content"
                    )
                int_value = int(value.strip())
            else:
                int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field_name} must be at least {min_value}"
                )
            
            if max_value is not None and int_value > max_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field_name} must be at most {max_value}"
                )
            
            return int_value
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be a valid integer"
            )
    
    def validate_string(self, value: Any, min_length: Optional[int] = None, 
                       max_length: Optional[int] = None, allowed_chars: Optional[str] = None,
                       field_name: str = "value") -> str:
        """Validate and sanitize string input"""
        if not isinstance(value, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be a string"
            )
        
        # Trim whitespace
        value = value.strip()
        
        # Check for SQL injection
        if self.sql_regex.search(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: contains suspicious content"
            )
        
        # Check for XSS
        if self.xss_regex.search(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: contains potentially malicious content"
            )
        
        # Check for path traversal
        if self.path_traversal_regex.search(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: contains path traversal attempts"
            )
        
        # Length validation
        if min_length is not None and len(value) < min_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be at least {min_length} characters long"
            )
        
        if max_length is not None and len(value) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be at most {max_length} characters long"
            )
        
        # Character validation
        if allowed_chars is not None:
            if not all(c in allowed_chars for c in value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field_name} contains invalid characters"
                )
        
        return value
    
    def validate_uuid(self, value: Any, field_name: str = "value") -> str:
        """Validate UUID format"""
        try:
            if isinstance(value, str):
                # Check for SQL injection
                if self.sql_regex.search(value):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid {field_name}: contains suspicious content"
                    )
                uuid.UUID(value.strip())
                return value.strip()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field_name} must be a string"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be a valid UUID"
            )
    
    def validate_email(self, value: Any, field_name: str = "email") -> str:
        """Validate email format"""
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        value = self.validate_string(value, min_length=5, max_length=254, field_name=field_name)
        
        if not email_regex.match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name} format"
            )
        
        return value.lower()
    
    def validate_filename(self, value: Any, field_name: str = "filename") -> str:
        """Validate filename for security"""
        value = self.validate_string(value, min_length=1, max_length=255, field_name=field_name)
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in value for char in dangerous_chars):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} contains invalid characters"
            )
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        
        name_without_ext = value.split('.')[0].upper()
        if name_without_ext in reserved_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} is a reserved name"
            )
        
        return value
    
    def validate_pagination_params(self, page: Any, limit: Any, 
                                 max_limit: int = 1000) -> tuple[int, int]:
        """Validate pagination parameters"""
        page = self.validate_integer(page, min_value=1, field_name="page")
        limit = self.validate_integer(limit, min_value=1, max_value=max_limit, field_name="limit")
        
        return page, limit
    
    def sanitize_sql_identifier(self, value: str) -> str:
        """Sanitize SQL identifier (table/column names)"""
        # Only allow alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SQL identifier"
            )
        return value
    
    def validate_json_payload(self, payload: dict, required_fields: List[str] = None,
                            optional_fields: List[str] = None) -> dict:
        """Validate JSON payload structure"""
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payload must be a JSON object"
            )
        
        # Check required fields
        if required_fields:
            for field in required_fields:
                if field not in payload:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing required field: {field}"
                    )
        
        # Check for unexpected fields
        if optional_fields:
            allowed_fields = set(required_fields or []) | set(optional_fields)
            unexpected_fields = set(payload.keys()) - allowed_fields
            if unexpected_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unexpected fields: {', '.join(unexpected_fields)}"
                )
        
        return payload

# Global instance
input_validator = InputValidator() 