#!/usr/bin/env python3
"""
Security Configuration for Vanta Ledger

This module contains security-related configuration settings and constants.
"""

import os
from typing import List, Set

# Security headers configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": (
        "geolocation=(), microphone=(), camera=(), "
        "payment=(), usb=(), magnetometer=(), gyroscope=(), "
        "accelerometer=(), ambient-light-sensor=(), "
        "autoplay=(), encrypted-media=(), fullscreen=()"
    ),
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "X-Permitted-Cross-Domain-Policies": "none",
    "X-Download-Options": "noopen",
    "X-DNS-Prefetch-Control": "off",
    "Server": "Vanta-Ledger",
}

# Content Security Policy configurations
CSP_POLICIES = {
    "api": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
    "docs": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    ),
    "health": (
        "default-src 'self'; "
        "script-src 'none'; "
        "style-src 'none'; "
        "img-src 'none'; "
        "frame-ancestors 'none'"
    ),
    "default": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    ),
}

# Security monitoring configuration
SECURITY_MONITORING = {
    "max_attack_attempts": 10,
    "attack_time_window": 300,  # 5 minutes
    "block_duration": 3600,  # 1 hour
    "log_suspicious_activity": True,
    "enable_ip_blocking": True,
}

# Request validation configuration
REQUEST_VALIDATION = {
    "max_request_size": 10 * 1024 * 1024,  # 10MB
    "max_header_size": 8192,  # 8KB
    "max_headers": 100,
    "block_suspicious_patterns": True,
    "log_validation_failures": True,
}

# CORS security configuration
CORS_SECURITY = {
    "allowed_methods": {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"},
    "allowed_headers": {
        "Content-Type", "Authorization", "X-Requested-With", 
        "X-Request-ID", "Accept", "Origin"
    },
    "max_age": 86400,  # 24 hours
    "allow_credentials": True,
}

# Security logging configuration
SECURITY_LOGGING = {
    "log_level": "WARNING",
    "log_file": "logs/security.log",
    "log_rotation": "daily",
    "log_retention": 30,  # days
    "log_sensitive_data": False,
}

# Environment-specific security settings
def get_security_settings() -> dict:
    """Get security settings based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return {
            "enable_strict_csp": True,
            "enable_hsts": True,
            "enable_security_monitoring": True,
            "enable_request_validation": True,
            "log_security_events": True,
        }
    elif env == "staging":
        return {
            "enable_strict_csp": True,
            "enable_hsts": False,
            "enable_security_monitoring": True,
            "enable_request_validation": True,
            "log_security_events": True,
        }
    else:  # development
        return {
            "enable_strict_csp": False,
            "enable_hsts": False,
            "enable_security_monitoring": False,
            "enable_request_validation": False,
            "log_security_events": False,
        }

# Security constants
SECURITY_CONSTANTS = {
    "MIN_PASSWORD_LENGTH": 12,
    "MAX_LOGIN_ATTEMPTS": 5,
    "SESSION_TIMEOUT": 3600,  # 1 hour
    "TOKEN_EXPIRY": 86400,  # 24 hours
    "ENCRYPTION_KEY_LENGTH": 32,
    "HASH_ROUNDS": 12,
}
