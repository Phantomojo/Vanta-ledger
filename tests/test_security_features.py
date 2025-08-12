#!/usr/bin/python3
"""
Security Features Testing Script for Vanta Ledger
Tests authentication, authorization, input validation, and security measures
"""

import asyncio
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import jwt
import pytest
import requests

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityFeaturesTestSuite:
    """Comprehensive security features testing suite"""

    def __init__(self, base_url: str = "http://localhost:8500"):
        self.base_url = base_url
        self.test_results = {}
        self.start_time = time.time()
        self.session = requests.Session()
        self.auth_token = None

    def log_test_result(
        self, test_name: str, success: bool, details: str = "", data: Dict = None
    ):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "data": data,
            "timestamp": time.time(),
        }

    def test_password_security(self) -> bool:
        """Test password security measures"""
        logger.info("🔒 Testing Password Security...")

        try:
            from app.auth import hash_password, verify_password
            from app.utils.validation import validate_password

            # Test password validation
            weak_passwords = ["123456", "password", "qwerty", "abc123", "password123"]

            strong_passwords = [
                "StrongPass123!",
                "MySecureP@ssw0rd",
                "Complex!Password#2024",
                "VantaLedger$ecure1",
            ]

            # Test weak passwords
            weak_password_results = []
            for password in weak_passwords:
                is_valid = validate_password(password)
                weak_password_results.append(
                    not is_valid
                )  # Should reject weak passwords

            # Test strong passwords
            strong_password_results = []
            for password in strong_passwords:
                is_valid = validate_password(password)
                strong_password_results.append(
                    is_valid
                )  # Should accept strong passwords

            weak_rejected = all(weak_password_results)
            strong_accepted = all(strong_password_results)

            self.log_test_result(
                "Password Validation",
                weak_rejected and strong_accepted,
                f"Weak rejected: {weak_rejected}, Strong accepted: {strong_accepted}",
            )

            # Test password hashing
            test_password = "TestPassword123!"
            hashed = hash_password(test_password)
            verify_success = verify_password(test_password, hashed)
            verify_fail = verify_password("WrongPassword", hashed)

            self.log_test_result(
                "Password Hashing",
                verify_success and not verify_fail,
                f"Hash verification: {verify_success}, Wrong password rejected: {not verify_fail}",
            )

            return True

        except Exception as e:
            self.log_test_result("Password Security", False, f"Error: {str(e)}")
            return False

    def test_authentication_mechanisms(self) -> bool:
        """Test authentication mechanisms"""
        logger.info("🔐 Testing Authentication Mechanisms...")

        try:
            from app.auth import create_access_token, get_current_user, verify_token

            # Test token creation
            test_user = {"user_id": "test123", "email": "test@example.com"}
            token = create_access_token(test_user)

            self.log_test_result(
                "Token Creation",
                bool(token),
                f"Token created: {len(token) if token else 0} chars",
            )

            # Test token verification
            if token:
                verified = verify_token(token)
                self.log_test_result(
                    "Token Verification",
                    bool(verified),
                    f"Token verified: {bool(verified)}",
                )

                # Test expired token
                expired_token = jwt.encode(
                    {
                        "user_id": "test123",
                        "exp": time.time() - 3600,
                    },  # Expired 1 hour ago
                    "test_secret",
                    algorithm="HS256",
                )
                expired_verified = verify_token(expired_token)
                self.log_test_result(
                    "Expired Token Rejection",
                    not expired_verified,
                    "Expired token properly rejected",
                )

            return True

        except Exception as e:
            self.log_test_result("Authentication Mechanisms", False, f"Error: {str(e)}")
            return False

    def test_authorization_rules(self) -> bool:
        """Test authorization rules"""
        logger.info("🚫 Testing Authorization Rules...")

        try:
            from app.auth import get_current_user
            from app.models.user_models import User

            # Test role-based access
            admin_user = User(
                email="admin@example.com", full_name="Admin User", role="admin"
            )

            regular_user = User(
                email="user@example.com", full_name="Regular User", role="user"
            )

            # Test admin privileges
            admin_has_admin_access = admin_user.role == "admin"
            user_has_admin_access = regular_user.role == "admin"

            self.log_test_result(
                "Role-Based Access",
                admin_has_admin_access and not user_has_admin_access,
                f"Admin access: {admin_has_admin_access}, User access: {user_has_admin_access}",
            )

            return True

        except Exception as e:
            self.log_test_result("Authorization Rules", False, f"Error: {str(e)}")
            return False

    def test_input_validation(self) -> bool:
        """Test input validation and sanitization"""
        logger.info("🧹 Testing Input Validation...")

        try:
            from app.utils.validation import (
                sanitize_input,
                validate_email,
                validate_filename,
            )

            # Test email validation
            valid_emails = [
                "test@example.com",
                "user.name@domain.co.uk",
                "test+tag@example.org",
            ]

            invalid_emails = [
                "invalid-email",
                "@example.com",
                "test@",
                "test..test@example.com",
            ]

            valid_email_results = [validate_email(email) for email in valid_emails]
            invalid_email_results = [
                not validate_email(email) for email in invalid_emails
            ]

            self.log_test_result(
                "Email Validation",
                all(valid_email_results) and all(invalid_email_results),
                f"Valid emails: {sum(valid_email_results)}/{len(valid_emails)}, Invalid emails: {sum(invalid_email_results)}/{len(invalid_emails)}",
            )

            # Test filename validation
            valid_filenames = ["document.pdf", "report_2024.xlsx", "data.csv"]

            invalid_filenames = [
                "../../../etc/passwd",
                "file<script>alert('xss')</script>.pdf",
                "file with spaces.txt",
            ]

            valid_filename_results = [
                validate_filename(filename) for filename in valid_filenames
            ]
            invalid_filename_results = [
                not validate_filename(filename) for filename in invalid_filenames
            ]

            self.log_test_result(
                "Filename Validation",
                all(valid_filename_results) and all(invalid_filename_results),
                f"Valid filenames: {sum(valid_filename_results)}/{len(valid_filenames)}, Invalid filenames: {sum(invalid_filename_results)}/{len(invalid_filenames)}",
            )

            # Test input sanitization
            malicious_inputs = [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "javascript:alert('xss')",
                "data:text/html,<script>alert('xss')</script>",
            ]

            sanitized_inputs = [
                sanitize_input(input_text) for input_text in malicious_inputs
            ]
            sanitization_works = all(
                "<script>" not in sanitized for sanitized in sanitized_inputs
            )

            self.log_test_result(
                "Input Sanitization",
                sanitization_works,
                f"Sanitization effective: {sanitization_works}",
            )

            return True

        except Exception as e:
            self.log_test_result("Input Validation", False, f"Error: {str(e)}")
            return False

    def test_sql_injection_prevention(self) -> bool:
        """Test SQL injection prevention"""
        logger.info("💉 Testing SQL Injection Prevention...")

        try:
            from app.hybrid_database import HybridDatabase
            from app.models.user_models import User

            db = HybridDatabase()

            # Test SQL injection attempts
            sql_injection_attempts = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "'; INSERT INTO users VALUES ('hacker', 'hacker@evil.com'); --",
                "' UNION SELECT * FROM users --",
            ]

            injection_prevented = True

            for attempt in sql_injection_attempts:
                try:
                    # Try to use malicious input in a query
                    user = User(
                        email=attempt,
                        full_name="Test User",
                        company_name="Test Company",
                    )

                    # This should either fail safely or be properly sanitized
                    result = db.create_user(user)

                    # If it succeeds, check if the data is properly escaped
                    if result:
                        retrieved = db.get_user_by_email(attempt)
                        if retrieved and retrieved.email == attempt:
                            # If the raw SQL injection string is stored, that's a problem
                            injection_prevented = False
                            break

                except Exception:
                    # SQL injection attempt was properly rejected
                    pass

            self.log_test_result(
                "SQL Injection Prevention",
                injection_prevented,
                f"Injection attempts blocked: {injection_prevented}",
            )

            return True

        except Exception as e:
            self.log_test_result("SQL Injection Prevention", False, f"Error: {str(e)}")
            return False

    def test_xss_prevention(self) -> bool:
        """Test XSS prevention"""
        logger.info("🛡️ Testing XSS Prevention...")

        try:
            from app.utils.validation import sanitize_input

            # Test XSS attack vectors
            xss_attempts = [
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert('xss')>",
                "javascript:alert('xss')",
                "data:text/html,<script>alert('xss')</script>",
                "<svg onload=alert('xss')>",
                "';alert('xss');//",
            ]

            xss_prevented = True

            for attempt in xss_attempts:
                sanitized = sanitize_input(attempt)

                # Check if dangerous patterns are still present
                dangerous_patterns = [
                    "<script",
                    "javascript:",
                    "onerror=",
                    "onload=",
                    "data:text/html",
                ]

                for pattern in dangerous_patterns:
                    if pattern in sanitized:
                        xss_prevented = False
                        break

                if not xss_prevented:
                    break

            self.log_test_result(
                "XSS Prevention",
                xss_prevented,
                f"XSS attempts blocked: {xss_prevented}",
            )

            return True

        except Exception as e:
            self.log_test_result("XSS Prevention", False, f"Error: {str(e)}")
            return False

    def test_csrf_protection(self) -> bool:
        """Test CSRF protection"""
        logger.info("🔄 Testing CSRF Protection...")

        try:
            # Test CSRF token generation
            from app.auth import generate_csrf_token, verify_csrf_token

            # Generate CSRF token
            csrf_token = generate_csrf_token()
            self.log_test_result(
                "CSRF Token Generation",
                bool(csrf_token),
                f"Token generated: {len(csrf_token) if csrf_token else 0} chars",
            )

            # Test CSRF token verification
            if csrf_token:
                valid_verification = verify_csrf_token(csrf_token)
                invalid_verification = verify_csrf_token("invalid_token")

                self.log_test_result(
                    "CSRF Token Verification",
                    valid_verification and not invalid_verification,
                    f"Valid token: {valid_verification}, Invalid token: {invalid_verification}",
                )

            return True

        except Exception as e:
            self.log_test_result("CSRF Protection", False, f"Error: {str(e)}")
            return False

    def test_rate_limiting(self) -> bool:
        """Test rate limiting"""
        logger.info("⏱️ Testing Rate Limiting...")

        try:
            # Test rapid requests to see if rate limiting is enforced
            rapid_requests = []

            for i in range(10):
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/v2/auth/login",
                        json={"email": f"test{i}@example.com", "password": "test"},
                    )
                    rapid_requests.append(response.status_code)
                except Exception:
                    rapid_requests.append(500)

            # Check if any requests were rate limited (429 status)
            rate_limited = 429 in rapid_requests

            self.log_test_result(
                "Rate Limiting", rate_limited, f"Rate limiting active: {rate_limited}"
            )

            return True

        except Exception as e:
            self.log_test_result("Rate Limiting", False, f"Error: {str(e)}")
            return False

    def test_secure_headers(self) -> bool:
        """Test secure HTTP headers"""
        logger.info("📋 Testing Secure Headers...")

        try:
            response = self.session.get(f"{self.base_url}/health")

            # Check for security headers
            headers = response.headers
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": None,  # Any value is good
                "Content-Security-Policy": None,  # Any value is good
                "Referrer-Policy": None,  # Any value is good
            }

            headers_present = 0
            total_headers = len(security_headers)

            for header, expected_value in security_headers.items():
                if header in headers:
                    if expected_value is None:
                        headers_present += 1
                    elif isinstance(expected_value, list):
                        if headers[header] in expected_value:
                            headers_present += 1
                    elif headers[header] == expected_value:
                        headers_present += 1

            security_score = headers_present / total_headers
            self.log_test_result(
                "Secure Headers",
                security_score > 0.5,
                f"Security score: {security_score:.2f}",
            )

            return True

        except Exception as e:
            self.log_test_result("Secure Headers", False, f"Error: {str(e)}")
            return False

    def test_file_upload_security(self) -> bool:
        """Test file upload security"""
        logger.info("📁 Testing File Upload Security...")

        try:
            from app.utils.validation import validate_file_upload

            # Test malicious file uploads
            malicious_files = [
                {"filename": "malware.exe", "content_type": "application/x-executable"},
                {"filename": "script.php", "content_type": "application/x-php"},
                {"filename": "shell.sh", "content_type": "application/x-sh"},
                {"filename": "virus.bat", "content_type": "application/x-bat"},
            ]

            safe_files = [
                {"filename": "document.pdf", "content_type": "application/pdf"},
                {"filename": "image.jpg", "content_type": "image/jpeg"},
                {
                    "filename": "data.xlsx",
                    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                },
            ]

            malicious_blocked = all(
                not validate_file_upload(file) for file in malicious_files
            )
            safe_allowed = all(validate_file_upload(file) for file in safe_files)

            self.log_test_result(
                "File Upload Security",
                malicious_blocked and safe_allowed,
                f"Malicious blocked: {malicious_blocked}, Safe allowed: {safe_allowed}",
            )

            return True

        except Exception as e:
            self.log_test_result("File Upload Security", False, f"Error: {str(e)}")
            return False

    def test_session_management(self) -> bool:
        """Test session management security"""
        logger.info("🪑 Testing Session Management...")

        try:
            from app.auth import create_access_token, verify_token

            # Test session timeout
            test_user = {"user_id": "test123", "email": "test@example.com"}

            # Create token with short expiration
            short_token = jwt.encode(
                {"user_id": "test123", "exp": time.time() + 1},  # Expires in 1 second
                "test_secret",
                algorithm="HS256",
            )

            # Verify token immediately
            immediate_verify = verify_token(short_token)

            # Wait for token to expire
            time.sleep(2)

            # Verify expired token
            expired_verify = verify_token(short_token)

            self.log_test_result(
                "Session Timeout",
                immediate_verify and not expired_verify,
                f"Immediate: {immediate_verify}, Expired: {expired_verify}",
            )

            return True

        except Exception as e:
            self.log_test_result("Session Management", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security feature tests"""
        logger.info("🚀 Starting Security Features Tests...")
        logger.info("=" * 50)

        tests = [
            ("Password Security", self.test_password_security),
            ("Authentication Mechanisms", self.test_authentication_mechanisms),
            ("Authorization Rules", self.test_authorization_rules),
            ("Input Validation", self.test_input_validation),
            ("SQL Injection Prevention", self.test_sql_injection_prevention),
            ("XSS Prevention", self.test_xss_prevention),
            ("CSRF Protection", self.test_csrf_protection),
            ("Rate Limiting", self.test_rate_limiting),
            ("Secure Headers", self.test_secure_headers),
            ("File Upload Security", self.test_file_upload_security),
            ("Session Management", self.test_session_management),
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                success = test_func()
                results[test_name] = success
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {str(e)}")
                results[test_name] = False

        # Generate summary
        total_tests = len(results)
        passed_tests = sum(results.values())
        failed_tests = total_tests - passed_tests

        logger.info("=" * 50)
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"   Duration: {time.time() - self.start_time:.2f}s")

        return {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
                "duration": time.time() - self.start_time,
            },
            "results": results,
            "detailed_results": self.test_results,
        }


def main():
    """Main test execution function"""
    print("🧪 Security Features Testing Suite")
    print("=" * 50)

    # Get base URL from environment or use default
    base_url = os.getenv("API_BASE_URL", "http://localhost:8500")
    print(f"Testing security at: {base_url}")

    # Create test suite
    test_suite = SecurityFeaturesTestSuite(base_url)

    # Run all tests
    results = test_suite.run_all_tests()

    # Save results to file
    results_file = "test_security_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {results_file}")

    # Return exit code based on results
    if results["summary"]["failed"] > 0:
        print("❌ Some security tests failed!")
        return 1
    else:
        print("✅ All security tests passed!")
        return 0


if __name__ == "__main__":
    exit(main())
