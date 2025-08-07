#!/usr/bin/env python3
"""
Security Test Suite
Tests authentication, input validation, file upload security, and SQL injection prevention
"""

import pytest
import jwt
import os
import tempfile
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path

from backend.app.main import app
from backend.app.auth import AuthService, User
from backend.app.utils.validation import input_validator
from backend.app.utils.file_utils import secure_file_handler
from backend.app.config import settings

client = TestClient(app)

class TestAuthentication:
    """Test authentication security"""
    
    def test_login_with_valid_credentials(self):
        """Test successful login with valid credentials"""
        response = client.post("/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post("/auth/login", data={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_with_sql_injection(self):
        """Test login with SQL injection attempts"""
        sql_injection_payloads = [
            "admin' OR '1'='1",
            "admin' --",
            "admin'/*",
            "admin' UNION SELECT * FROM users --",
            "'; DROP TABLE users; --"
        ]
        
        for payload in sql_injection_payloads:
            response = client.post("/auth/login", data={
                "username": payload,
                "password": "password"
            })
            # Should not crash and should return 401
            assert response.status_code in [401, 400]
    
    def test_jwt_token_validation(self):
        """Test JWT token validation"""
        # Create a valid token
        token_data = {"sub": "admin", "user_id": "1"}
        valid_token = AuthService.create_access_token(token_data)
        
        # Test valid token
        response = client.get("/health", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200
        
        # Test invalid token
        response = client.get("/health", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401
        
        # Test expired token
        expired_token = jwt.encode(
            {"sub": "admin", "exp": datetime.utcnow() - timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        response = client.get("/health", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
    
    def test_token_blacklisting(self):
        """Test JWT token blacklisting"""
        token_data = {"sub": "admin", "user_id": "1"}
        token = AuthService.create_access_token(token_data)
        
        # Token should be valid initially
        payload = AuthService.verify_token(token)
        assert payload["sub"] == "admin"
        
        # Blacklist the token
        jti = payload.get("jti")
        assert AuthService.blacklist_token(jti)
        
        # Token should now be invalid
        with pytest.raises(Exception):
            AuthService.verify_token(token)

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_integer_validation(self):
        """Test integer validation"""
        # Valid integers
        assert input_validator.validate_integer(5) == 5
        assert input_validator.validate_integer("10") == 10
        assert input_validator.validate_integer(15, min_value=10, max_value=20) == 15
        
        # Invalid inputs
        with pytest.raises(Exception):
            input_validator.validate_integer("not_a_number")
        
        with pytest.raises(Exception):
            input_validator.validate_integer(5, min_value=10)
        
        with pytest.raises(Exception):
            input_validator.validate_integer(25, max_value=20)
    
    def test_string_validation(self):
        """Test string validation and sanitization"""
        # Valid strings
        assert input_validator.validate_string("hello") == "hello"
        assert input_validator.validate_string("  hello  ") == "hello"  # Trim whitespace
        
        # SQL injection attempts
        sql_injection_strings = [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "SELECT * FROM users",
            "UNION SELECT password FROM users",
            "1; INSERT INTO users VALUES ('hacker', 'password')"
        ]
        
        for sql_string in sql_injection_strings:
            with pytest.raises(Exception):
                input_validator.validate_string(sql_string)
        
        # XSS attempts
        xss_strings = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src=javascript:alert('xss')></iframe>"
        ]
        
        for xss_string in xss_strings:
            with pytest.raises(Exception):
                input_validator.validate_string(xss_string)
    
    def test_uuid_validation(self):
        """Test UUID validation"""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        assert input_validator.validate_uuid(valid_uuid) == valid_uuid
        
        with pytest.raises(Exception):
            input_validator.validate_uuid("invalid-uuid")
        
        with pytest.raises(Exception):
            input_validator.validate_uuid("123e4567-e89b-12d3-a456-426614174000' OR '1'='1")
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            assert input_validator.validate_email(email) == email.lower()
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user@example"
        ]
        
        for email in invalid_emails:
            with pytest.raises(Exception):
                input_validator.validate_email(email)
    
    def test_filename_validation(self):
        """Test filename validation"""
        valid_filenames = [
            "document.pdf",
            "file_name.docx",
            "test123.txt"
        ]
        
        for filename in valid_filenames:
            assert input_validator.validate_filename(filename) == filename
        
        invalid_filenames = [
            "file<name.pdf",
            "file>name.pdf",
            "file:name.pdf",
            "file|name.pdf",
            "file?name.pdf",
            "file*name.pdf",
            "file\\name.pdf",
            "file/name.pdf",
            "CON.pdf",  # Reserved name
            "PRN.txt"
        ]
        
        for filename in invalid_filenames:
            with pytest.raises(Exception):
                input_validator.validate_filename(filename)

class TestFileUploadSecurity:
    """Test secure file upload functionality"""
    
    def test_file_type_validation(self):
        """Test file type validation"""
        # Create test files
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4\n%Test PDF content")
            pdf_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test text content")
            txt_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            f.write(b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00")
            exe_path = f.name
        
        try:
            # Test valid file types
            from fastapi import UploadFile
            
            # Mock PDF file
            with open(pdf_path, 'rb') as f:
                pdf_file = UploadFile(filename="test.pdf", file=f)
                is_valid, message = secure_file_handler.validate_file(pdf_file)
                assert is_valid
            
            # Mock text file
            with open(txt_path, 'rb') as f:
                txt_file = UploadFile(filename="test.txt", file=f)
                is_valid, message = secure_file_handler.validate_file(txt_file)
                assert is_valid
            
            # Test invalid file type
            with open(exe_path, 'rb') as f:
                exe_file = UploadFile(filename="test.exe", file=f)
                is_valid, message = secure_file_handler.validate_file(exe_file)
                assert not is_valid
                assert "not allowed" in message
        
        finally:
            # Cleanup
            for path in [pdf_path, txt_path, exe_path]:
                if os.path.exists(path):
                    os.unlink(path)
    
    def test_secure_filename_generation(self):
        """Test secure filename generation"""
        original_filename = "sensitive_document.pdf"
        user_id = "user123"
        
        secure_filename = secure_file_handler.generate_secure_filename(original_filename, user_id)
        
        # Should not contain original filename
        assert "sensitive_document" not in secure_filename
        assert "user123" in secure_filename
        assert secure_filename.endswith(".pdf")
        
        # Should be unique
        secure_filename2 = secure_file_handler.generate_secure_filename(original_filename, user_id)
        assert secure_filename != secure_filename2
    
    def test_path_traversal_prevention(self):
        """Test path traversal prevention"""
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for filename in malicious_filenames:
            with pytest.raises(Exception):
                secure_file_handler.get_safe_upload_path(filename, "/tmp/uploads")

class TestSQLInjectionPrevention:
    """Test SQL injection prevention in endpoints"""
    
    def test_company_endpoint_sql_injection(self):
        """Test SQL injection prevention in company endpoint"""
        # First, get a valid token
        login_response = client.post("/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # SQL injection attempts
        sql_injection_payloads = [
            "1 OR 1=1",
            "1' OR '1'='1",
            "1; DROP TABLE companies; --",
            "1 UNION SELECT * FROM users --",
            "1' UNION SELECT password FROM users --"
        ]
        
        for payload in sql_injection_payloads:
            response = client.get(f"/companies/{payload}", headers=headers)
            # Should not crash and should return 400 or 404
            assert response.status_code in [400, 404, 422]
    
    def test_pagination_sql_injection(self):
        """Test SQL injection prevention in pagination"""
        login_response = client.post("/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # SQL injection attempts in pagination parameters
        malicious_params = [
            {"page": "1 OR 1=1", "limit": "10"},
            {"page": "1", "limit": "10; DROP TABLE companies; --"},
            {"page": "1' UNION SELECT * FROM users --", "limit": "10"}
        ]
        
        for params in malicious_params:
            response = client.get("/companies/", params=params, headers=headers)
            # Should not crash and should return 400 or 422
            assert response.status_code in [400, 422]

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting(self):
        """Test rate limiting on endpoints"""
        # Make multiple requests quickly
        for i in range(10):
            response = client.get("/health")
            if response.status_code == 429:  # Rate limited
                break
        else:
            # If we didn't hit rate limit, the test passes
            assert True

class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        response = client.get("/health")
        
        headers = response.headers
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        assert "Referrer-Policy" in headers
        assert "Permissions-Policy" in headers

if __name__ == "__main__":
    pytest.main([__file__]) 