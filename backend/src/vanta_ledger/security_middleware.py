#!/usr/bin/env python3
"""
Enhanced Security Middleware for Vanta Ledger

This module provides comprehensive security middleware including:
- Enhanced security headers
- Request validation
- Security monitoring
- Attack detection and prevention
"""

import logging
import re
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

logger = logging.getLogger(__name__)


class EnhancedSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enhanced security headers middleware with comprehensive protection."""

    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # XSS protection (legacy but still useful)
            "X-XSS-Protection": "1; mode=block",
            
            # Force HTTPS
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=(), "
                "accelerometer=(), ambient-light-sensor=(), "
                "autoplay=(), encrypted-media=(), fullscreen=()"
            ),
            
            # Cross-Origin policies
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            
            # Additional security headers
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "X-DNS-Prefetch-Control": "off",
            
            # Remove server information
            "Server": "Vanta-Ledger",
        }

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Dynamic Content Security Policy based on endpoint
        csp = self._get_csp_for_endpoint(request.url.path)
        response.headers["Content-Security-Policy"] = csp
        
        # Add security-related response headers
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
        
        return response

    def _get_csp_for_endpoint(self, path: str) -> str:
        """Generate appropriate CSP for different endpoints."""
        
        # API endpoints - strict CSP
        if path.startswith("/api/"):
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        
        # Documentation endpoints - more permissive for Swagger UI
        elif path.startswith("/docs") or path.startswith("/redoc"):
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        
        # Health check and metrics - minimal CSP
        elif path in ["/health", "/metrics", "/"]:
            return (
                "default-src 'self'; "
                "script-src 'none'; "
                "style-src 'none'; "
                "img-src 'none'; "
                "frame-ancestors 'none'"
            )
        
        # Default strict CSP
        else:
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate and sanitize incoming requests."""

    def __init__(self, app):
        super().__init__(app)
        
        # Suspicious patterns to detect
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'vbscript:',  # VBScript URLs
            r'on\w+\s*=',  # Event handlers
            r'expression\s*\(',  # CSS expressions
            r'url\s*\(',  # CSS URLs
            r'@import',  # CSS imports
            r'<iframe[^>]*>',  # Iframe tags
            r'<object[^>]*>',  # Object tags
            r'<embed[^>]*>',  # Embed tags
            r'<link[^>]*>',  # Link tags
            r'<meta[^>]*>',  # Meta tags
            r'<form[^>]*>',  # Form tags
            r'<input[^>]*>',  # Input tags
            r'<textarea[^>]*>',  # Textarea tags
            r'<select[^>]*>',  # Select tags
            r'<option[^>]*>',  # Option tags
            r'<button[^>]*>',  # Button tags
            r'<a[^>]*>',  # Anchor tags
            r'<img[^>]*>',  # Image tags
            r'<video[^>]*>',  # Video tags
            r'<audio[^>]*>',  # Audio tags
            r'<source[^>]*>',  # Source tags
            r'<track[^>]*>',  # Track tags
            r'<canvas[^>]*>',  # Canvas tags
            r'<svg[^>]*>',  # SVG tags
            r'<math[^>]*>',  # Math tags
            r'<table[^>]*>',  # Table tags
            r'<tr[^>]*>',  # Table row tags
            r'<td[^>]*>',  # Table cell tags
            r'<th[^>]*>',  # Table header tags
            r'<thead[^>]*>',  # Table head tags
            r'<tbody[^>]*>',  # Table body tags
            r'<tfoot[^>]*>',  # Table foot tags
            r'<col[^>]*>',  # Column tags
            r'<colgroup[^>]*>',  # Column group tags
            r'<caption[^>]*>',  # Caption tags
            r'<fieldset[^>]*>',  # Fieldset tags
            r'<legend[^>]*>',  # Legend tags
            r'<label[^>]*>',  # Label tags
            r'<output[^>]*>',  # Output tags
            r'<progress[^>]*>',  # Progress tags
            r'<meter[^>]*>',  # Meter tags
            r'<details[^>]*>',  # Details tags
            r'<summary[^>]*>',  # Summary tags
            r'<dialog[^>]*>',  # Dialog tags
            r'<menu[^>]*>',  # Menu tags
            r'<menuitem[^>]*>',  # Menu item tags
            r'<command[^>]*>',  # Command tags
            r'<keygen[^>]*>',  # Keygen tags
            r'<isindex[^>]*>',  # Isindex tags
            r'<listing[^>]*>',  # Listing tags
            r'<plaintext[^>]*>',  # Plaintext tags
            r'<xmp[^>]*>',  # XMP tags
            r'<noembed[^>]*>',  # Noembed tags
            r'<noframes[^>]*>',  # Noframes tags
            r'<noscript[^>]*>',  # Noscript tags
            r'<applet[^>]*>',  # Applet tags
            r'<param[^>]*>',  # Param tags
            r'<area[^>]*>',  # Area tags
            r'<base[^>]*>',  # Base tags
            r'<bgsound[^>]*>',  # Bgsound tags
            r'<blink[^>]*>',  # Blink tags
            r'<body[^>]*>',  # Body tags
            r'<br[^>]*>',  # Break tags
            r'<center[^>]*>',  # Center tags
            r'<cite[^>]*>',  # Cite tags
            r'<code[^>]*>',  # Code tags
            r'<dd[^>]*>',  # Definition description tags
            r'<dfn[^>]*>',  # Definition tags
            r'<dir[^>]*>',  # Directory tags
            r'<div[^>]*>',  # Division tags
            r'<dl[^>]*>',  # Definition list tags
            r'<dt[^>]*>',  # Definition term tags
            r'<em[^>]*>',  # Emphasis tags
            r'<font[^>]*>',  # Font tags
            r'<h[1-6][^>]*>',  # Heading tags
            r'<head[^>]*>',  # Head tags
            r'<hr[^>]*>',  # Horizontal rule tags
            r'<html[^>]*>',  # HTML tags
            r'<i[^>]*>',  # Italic tags
            r'<kbd[^>]*>',  # Keyboard tags
            r'<li[^>]*>',  # List item tags
            r'<map[^>]*>',  # Map tags
            r'<marquee[^>]*>',  # Marquee tags
            r'<nobr[^>]*>',  # Nobr tags
            r'<ol[^>]*>',  # Ordered list tags
            r'<p[^>]*>',  # Paragraph tags
            r'<pre[^>]*>',  # Preformatted tags
            r'<q[^>]*>',  # Quote tags
            r'<s[^>]*>',  # Strikethrough tags
            r'<samp[^>]*>',  # Sample tags
            r'<small[^>]*>',  # Small tags
            r'<span[^>]*>',  # Span tags
            r'<strike[^>]*>',  # Strike tags
            r'<strong[^>]*>',  # Strong tags
            r'<sub[^>]*>',  # Subscript tags
            r'<sup[^>]*>',  # Superscript tags
            r'<tt[^>]*>',  # Teletype tags
            r'<u[^>]*>',  # Underline tags
            r'<ul[^>]*>',  # Unordered list tags
            r'<var[^>]*>',  # Variable tags
            r'<wbr[^>]*>',  # Word break tags
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.suspicious_patterns]

    async def dispatch(self, request: Request, call_next):
        # Validate request headers
        if not self._validate_headers(request):
            logger.warning(f"Suspicious headers detected from {request.client.host}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request headers"}
            )
        
        # Validate request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await self._get_request_body(request)
            if body and not self._validate_body(body):
                logger.warning(f"Suspicious content detected in request body from {request.client.host}")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid request content"}
                )
        
        response = await call_next(request)
        return response

    def _validate_headers(self, request: Request) -> bool:
        """Validate request headers for suspicious content."""
        for header_name, header_value in request.headers.items():
            if self._contains_suspicious_content(header_value):
                return False
        return True

    def _validate_body(self, body: str) -> bool:
        """Validate request body for suspicious content."""
        return not self._contains_suspicious_content(body)

    def _contains_suspicious_content(self, content: str) -> bool:
        """Check if content contains suspicious patterns."""
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                return True
        return False

    async def _get_request_body(self, request: Request) -> Optional[str]:
        """Safely get request body."""
        try:
            body = await request.body()
            return body.decode('utf-8', errors='ignore')
        except Exception:
            return None


class SecurityMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for security monitoring and attack detection."""

    def __init__(self, app):
        super().__init__(app)
        self.attack_attempts: Dict[str, List[float]] = {}
        self.blocked_ips: Set[str] = set()
        self.max_attempts = 10
        self.time_window = 300  # 5 minutes

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP {client_ip} attempted to access {request.url}")
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Monitor for suspicious activity
        if response.status_code >= 400:
            self._record_attack_attempt(client_ip)
        
        # Check if IP should be blocked
        if self._should_block_ip(client_ip):
            self.blocked_ips.add(client_ip)
            logger.warning(f"IP {client_ip} blocked due to suspicious activity")
        
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        if settings.TRUST_PROXY:
            xff = request.headers.get("x-forwarded-for")
            return xff.split(",")[0].strip() if xff else request.client.host
        return request.client.host

    def _record_attack_attempt(self, client_ip: str):
        """Record an attack attempt from an IP."""
        current_time = time.time()
        if client_ip not in self.attack_attempts:
            self.attack_attempts[client_ip] = []
        
        self.attack_attempts[client_ip].append(current_time)
        
        # Clean old attempts
        self.attack_attempts[client_ip] = [
            attempt_time for attempt_time in self.attack_attempts[client_ip]
            if current_time - attempt_time < self.time_window
        ]

    def _should_block_ip(self, client_ip: str) -> bool:
        """Check if an IP should be blocked."""
        if client_ip not in self.attack_attempts:
            return False
        
        attempts = self.attack_attempts[client_ip]
        return len(attempts) >= self.max_attempts


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware with security considerations."""

    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = set(settings.ALLOWED_ORIGINS)
        self.allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"}
        self.allowed_headers = {
            "Content-Type", "Authorization", "X-Requested-With", 
            "X-Request-ID", "Accept", "Origin"
        }

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            return self._handle_preflight_request(origin)
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = "X-Request-ID"
        
        return response

    def _handle_preflight_request(self, origin: str) -> Response:
        """Handle CORS preflight requests."""
        if not origin or not self._is_origin_allowed(origin):
            return JSONResponse(
                status_code=403,
                content={"error": "CORS policy violation"}
            )
        
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400",  # 24 hours
        }
        
        return Response(status_code=200, headers=headers)

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        if "*" in self.allowed_origins:
            return True
        
        parsed_origin = urlparse(origin)
        origin_domain = f"{parsed_origin.scheme}://{parsed_origin.netloc}"
        
        return origin_domain in self.allowed_origins
