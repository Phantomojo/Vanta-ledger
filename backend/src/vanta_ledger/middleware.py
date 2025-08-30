import logging

# Configure logging
import os
import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

# Ensure log directory exists
log_dir = os.path.dirname(settings.LOG_FILE)
if log_dir:  # Only create directory if there's a path
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(settings.LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    def __init__(self, app):
        super().__init__(app)
        self.requests_per_minute: Dict[str, list] = defaultdict(list)
        self.requests_per_hour: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Determine client IP (proxy-aware only if explicitly trusted)
        if settings.TRUST_PROXY:
            xff = request.headers.get("x-forwarded-for")
            client_ip = xff.split(",")[0].strip() if xff else request.client.host
        else:
            client_ip = request.client.host

        # Check rate limits
        current_time = time.time()

        # Clean old requests
        self.requests_per_minute[client_ip] = [
            req_time
            for req_time in self.requests_per_minute[client_ip]
            if current_time - req_time < 60
        ]

        self.requests_per_hour[client_ip] = [
            req_time
            for req_time in self.requests_per_hour[client_ip]
            if current_time - req_time < 3600
        ]

        # Check limits
        if len(self.requests_per_minute[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        if len(self.requests_per_hour[client_ip]) >= settings.RATE_LIMIT_PER_HOUR:
            logger.warning(f"Hourly rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Hourly rate limit exceeded")

        # Add current request
        self.requests_per_minute[client_ip].append(current_time)
        self.requests_per_hour[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(
            settings.RATE_LIMIT_PER_MINUTE
        )
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            settings.RATE_LIMIT_PER_MINUTE - len(self.requests_per_minute[client_ip])
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(settings.RATE_LIMIT_PER_HOUR)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            settings.RATE_LIMIT_PER_HOUR - len(self.requests_per_hour[client_ip])
        )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        # Simplified CSP for compatibility
        if request.url.path == "/docs":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' https://fastapi.tiangolo.com; font-src 'self' https://cdn.jsdelivr.net"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'"
            )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url} from {request.headers.get('x-forwarded-for') or request.client.host}"
        )

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} in {process_time:.3f}s")

        return response
