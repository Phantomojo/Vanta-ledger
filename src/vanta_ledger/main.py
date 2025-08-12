#!/usr/bin/env python3
"""
Vanta Ledger - Main FastAPI Application
Advanced document processing and financial data management system
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import prometheus_client
import psycopg2
import pymongo
import redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from prometheus_client import Counter, Histogram

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
from .routes.extracted_data import router as extracted_data_router

# Import financial management
from .routes.financial import router as financial_router
from .routes.ledger import router as ledger_router

# Import local LLM
from .routes.local_llm import router as local_llm_router
from .routes.notifications import router as notifications_router
from .routes.paperless_integration import router as paperless_router
from .routes.projects import router as projects_router

# Import new frontend compatibility routes
from .routes.simple_auth import router as simple_auth_router
from .routes.users import router as users_router

# Import startup
from .startup import health_check, initialize_services

# from .routes.github_models import router as github_models_router  # Temporarily disabled due to import issues



# Initialize FastAPI app
app = FastAPI(
    title="Vanta Ledger API",
    description="Advanced document processing and financial data management system with AI analytics and local LLM",
    version=settings.VERSION,
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

# Initialize document processor
from .services.document_processor import DocumentProcessor

document_processor = DocumentProcessor()

# Include enhanced document management routes
app.include_router(enhanced_documents_router)

# Include financial management routes
app.include_router(financial_router)

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
# app.include_router(github_models_router)  # Temporarily disabled

# Include frontend compatibility routes
app.include_router(simple_auth_router)
app.include_router(extracted_data_router)
app.include_router(paperless_router)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")


# Database connections
def get_mongo_client():
    """
    Create and return a MongoDB client with a 5-second server selection and connection timeout.

    Returns:
        MongoClient: A configured MongoDB client instance.
    """
    return pymongo.MongoClient(
        settings.MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000
    )


def get_postgres_connection():
    """
    Establish and return a new PostgreSQL database connection with a 5-second timeout.

    Returns:
        connection: A psycopg2 connection object to the PostgreSQL database.
    """
    return psycopg2.connect(settings.POSTGRES_URI, connect_timeout=5)


def get_redis_client():
    """
    Create and return a Redis client instance configured with response decoding enabled.
    """
    return redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)


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
