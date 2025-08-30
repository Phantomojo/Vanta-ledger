#!/usr/bin/env python3
"""
Vanta Ledger - Main FastAPI Application
Advanced document processing and financial data management system
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

# Optional Prometheus metrics; provide safe fallbacks if not installed
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False

    class Counter:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass

    class Histogram:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass

    class _PromStub:
        @staticmethod
        def generate_latest():
            return b""

    prometheus_client = _PromStub()  # type: ignore

# Remove direct DB/Redis imports; import lazily within helper functions to tolerate missing drivers
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

# Import authentication
from .auth import AuthService

# Import settings and middleware
from .config import settings
from .middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)

# Import AI analytics
from .routes.ai_analytics import router as ai_analytics_router
from .routes.analytics import router as analytics_router
from .routes.auth import router as auth_router
from .routes.companies import router as companies_router
from .routes.config import router as config_router
from .routes.documents import router as documents_router

# Import enhanced document management
from .routes.enhanced_documents import router as enhanced_documents_router
from .routes.advanced_documents import router as advanced_documents_router
from .routes.semantic_search import router as semantic_search_router
from .routes.extracted_data import router as extracted_data_router

# Import financial management
from .routes.financial import router as financial_router
from .routes.ledger import router as ledger_router
from .routes.atomic_transactions import router as atomic_transactions_router

# Import local LLM
from .routes.local_llm import router as local_llm_router
from .routes.notifications import router as notifications_router
from .routes.paperless_integration import router as paperless_router
from .routes.projects import router as projects_router

# System health routes
from .routes.system_health import router as system_health_router

# Import new frontend compatibility routes
from .routes.simple_auth import router as simple_auth_router
from .routes.users import router as users_router

# Import startup
from .startup import health_check, initialize_services

from .routes.github_models import router as github_models_router  # Enabled after adding safe service shim



# Initialize FastAPI app (disable docs in production)
docs_url = "/docs" if settings.DEBUG else None
redoc_url = "/redoc" if settings.DEBUG else None
openapi_url = "/openapi.json" if settings.DEBUG else None
app = FastAPI(
    title="Vanta Ledger API",
    description="Advanced document processing and financial data management system with AI analytics and local LLM",
    version=settings.VERSION,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Initializes required services asynchronously when the application starts.
    """
    # Validate required runtime configuration now (not at import time)
    settings.validate_required_config()
    if not settings.DEBUG and not settings.SECRET_KEY:
        # Defensive check: validate_required_config should have raised
        raise RuntimeError("SECRET_KEY must be configured in production")
    await initialize_services()


# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Document processor will be initialized when needed in routes

# Include enhanced document management routes
app.include_router(enhanced_documents_router)
app.include_router(advanced_documents_router)
app.include_router(semantic_search_router)

# Include financial management routes
app.include_router(financial_router)
app.include_router(atomic_transactions_router)

# Include AI analytics routes
app.include_router(ai_analytics_router)

# Include local LLM routes
app.include_router(local_llm_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(companies_router)
app.include_router(projects_router)
app.include_router(ledger_router)
app.include_router(analytics_router)
app.include_router(users_router)
app.include_router(config_router)
app.include_router(notifications_router)
app.include_router(system_health_router)
if settings.ENABLE_GITHUB_MODELS:
    app.include_router(github_models_router)

# Include frontend compatibility routes
if settings.DEBUG:
    app.include_router(simple_auth_router)
app.include_router(extracted_data_router)
app.include_router(paperless_router)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")

# Request ID and global error handler middleware
import uuid

@app.middleware("http")
async def request_id_and_error_handler(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    try:
        response = await call_next(request)
    except Exception as e:
        logger = logging.getLogger("vanta_ledger.main")
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={
                "type": "about:blank",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred.",
                "instance": str(request.url.path),
                "request_id": request_id,
            },
        )
    response.headers["X-Request-ID"] = request_id
    return response


# Database connections (imported from database module)
from .database import get_mongo_client, get_postgres_connection, get_redis_client


# Authentication - using the new AuthService
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the provided HTTP Bearer token and returns the associated user or authentication context.

    Parameters:
        credentials (HTTPAuthorizationCredentials): The HTTP Bearer credentials extracted from the request.

    Returns:
        The result of token verification, typically user information or authentication context.
    """
    return AuthService.verify_token(credentials.credentials)


if settings.DEBUG:
    # Test route
    @app.get("/test-companies")
    async def test_companies_endpoint():
        """Test endpoint for companies"""
        return {
            "companies": [
                {"id": 1, "name": "Acme Corporation", "industry": "Technology", "revenue": 5000000.0},
                {"id": 2, "name": "Global Industries Ltd", "industry": "Manufacturing", "revenue": 12000000.0},
            ],
            "total_count": 2,
            "page": 1,
            "limit": 20,
            "total_pages": 1,
        }

    # Test endpoint for ledger data
    @app.get("/test-ledger")
    async def test_ledger_endpoint():
        """Test endpoint for ledger data"""
        return {
            "transactions": [
                {
                    "id": 1,
                    "transaction_date": "2025-08-16T15:00:00",
                    "description": "Office supplies purchase",
                    "amount": 1250.50,
                    "account_name": "Office Expenses",
                    "transaction_type": "debit",
                    "reference": "INV-001"
                },
                {
                    "id": 2,
                    "transaction_date": "2025-08-16T14:30:00",
                    "description": "Client payment received",
                    "amount": 5000.00,
                    "account_name": "Accounts Receivable",
                    "transaction_type": "credit",
                    "reference": "REC-001"
                }
            ],
            "total_count": 2
        }

    # Test endpoint for documents
    @app.get("/test-documents")
    async def test_documents_endpoint():
        """Test endpoint for documents"""
        return {
            "documents": [
                {
                    "id": 1,
                    "filename": "invoice_001.pdf",
                    "document_type": "invoice",
                    "status": "processed",
                    "upload_date": "2025-08-16T15:00:00",
                    "company_id": 1
                },
                {
                    "id": 2,
                    "filename": "receipt_001.pdf",
                    "document_type": "receipt",
                    "status": "processed",
                    "upload_date": "2025-08-16T14:30:00",
                    "company_id": 1
                }
            ],
            "total_count": 2
        }

    # Test upload endpoint
    @app.post("/test-upload-document")
    async def test_upload_document():
        """Test endpoint for document upload (no auth required)"""
        return {
            "status": "success",
            "message": "Document upload test endpoint working",
            "document_id": "test_123",
            "filename": "test_document.pdf",
            "upload_timestamp": "2025-08-16T16:00:00"
        }

# Health check
@app.get("/health")
async def health_check_endpoint():
    """
    Asynchronously returns the current health status of the service.
    """
    logger = logging.getLogger("vanta_ledger.main")
    try:
        return await health_check()
    except Exception as e:
        logger.error("Health check endpoint failed: Internal server error")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": "Internal server error"},
        )


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """
    Return the latest Prometheus metrics data for monitoring and observability systems.
    """
    from fastapi.responses import Response

    return Response(
        content=prometheus_client.generate_latest(), media_type="text/plain"
    )

# Readiness endpoint
@app.get("/ready")
async def readiness():
    logger = logging.getLogger("vanta_ledger.ready")
    details = {"postgres": None, "mongo": None, "redis": None}
    ok = True

    # Postgres check
    if settings.POSTGRES_URI:
        try:
            conn = get_postgres_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            conn.close()
            details["postgres"] = {"status": "ok"}
        except Exception as e:
            ok = False
            details["postgres"] = {"status": "error", "error": str(e)}
    else:
        details["postgres"] = {"status": "skipped", "reason": "POSTGRES_URI not set"}

    # Mongo check
    if settings.MONGO_URI:
        try:
            client = get_mongo_client()
            client.admin.command("ping")
            details["mongo"] = {"status": "ok"}
        except Exception as e:
            ok = False
            details["mongo"] = {"status": "error", "error": str(e)}
    else:
        details["mongo"] = {"status": "skipped", "reason": "MONGO_URI not set"}

    # Redis check
    if settings.REDIS_URI:
        try:
            r = get_redis_client()
            r.ping()
            details["redis"] = {"status": "ok"}
        except Exception as e:
            ok = False
            details["redis"] = {"status": "error", "error": str(e)}
    else:
        details["redis"] = {"status": "skipped", "reason": "REDIS_URI not set"}

    status_code = 200 if ok or settings.ALLOW_MISSING_DATABASES else 503
    overall = "ready" if status_code == 200 else "not_ready"
    return JSONResponse(status_code=status_code, content={"status": overall, "details": details})


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generate a JWT access token with an expiration time.

    Parameters:
        data (dict): The payload to include in the token.
        expires_delta (Optional[timedelta]): Optional duration until the token expires. Defaults to 15 minutes if not provided.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# Database test endpoints
@app.get("/test-mongo")
async def test_mongo():
    """
    Test MongoDB connectivity by inserting and deleting a test document.

    Returns:
        dict: A status message indicating whether the MongoDB connection was successful.

    Raises:
        HTTPException: If the MongoDB connection or operation fails.
    """
    try:
        client = get_mongo_client()
        db = client.vanta_ledger
        result = db.test.insert_one({"test": "data", "timestamp": datetime.now()})
        db.test.delete_one({"_id": result.inserted_id})
        return {"status": "MongoDB connection successful"}
    except Exception as e:
        logger.error("MongoDB connection failed: Connection error")
        raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/test-postgres")
async def test_postgres():
    """
    Test connectivity to the PostgreSQL database and return the server version.

    Returns:
        dict: A dictionary containing the connection status and PostgreSQL server version.

    Raises:
        HTTPException: If the connection or query fails, returns a 500 error with details.
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "PostgreSQL connection successful", "version": version[0]}
    except Exception as e:
        logger.error("PostgreSQL connection failed: Connection error")
        raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/test-redis")
async def test_redis():
    """
    Test Redis connectivity by performing a set, get, and delete operation on a test key.

    Returns:
        dict: A status message indicating success and the value retrieved from Redis.

    Raises:
        HTTPException: If any Redis operation fails, returns a 500 error with details.
    """
    try:
        r = get_redis_client()
        r.set("test", "data")
        result = r.get("test")
        r.delete("test")
        return {"status": "Redis connection successful", "test_value": result}
    except Exception as e:
        logger.error("Redis connection failed: Connection error")
        raise HTTPException(status_code=500, detail="Database connection failed")


# Legacy endpoints for backward compatibility

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8500)  # Use localhost for security
