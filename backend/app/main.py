#!/usr/bin/env python3
"""
Vanta Ledger - Main FastAPI Application
Advanced document processing and financial data management system
"""

import os
import json
import glob
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import jwt
import pymongo
import psycopg2
import redis
import prometheus_client
from prometheus_client import Counter, Histogram

# Import settings and middleware
from .config import settings
from .middleware import LoggingMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware

# Import authentication
from .auth import AuthService, get_current_user, get_user_by_username

# Import secure file handling
from .utils.file_utils import secure_file_handler

# Import input validation
from .utils.validation import input_validator

# Import document processor
from .services.document_processor import DocumentProcessor
from .services.ai_analytics_service import enhanced_ai_analytics_service
from .services.analytics_dashboard import analytics_dashboard

# Import enhanced document management
from .routes.enhanced_documents import router as enhanced_documents_router

# Import financial management
from .routes.financial import router as financial_router

# Import AI analytics
from .routes.ai_analytics import router as ai_analytics_router

# Import local LLM
from .routes.local_llm import router as local_llm_router
from .routes.auth import router as auth_router
from .routes.documents import router as documents_router
from .routes.companies import router as companies_router
from .routes.projects import router as projects_router
from .routes.ledger import router as ledger_router
from .routes.analytics import router as analytics_router
from .routes.users import router as users_router
from .routes.config import router as config_router
from .routes.notifications import router as notifications_router

# Import startup
from .startup import initialize_services, health_check

# Initialize FastAPI app
app = FastAPI(
    title="Vanta Ledger API",
    description="Advanced document processing and financial data management system with AI analytics and local LLM",
    version=settings.VERSION
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
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

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Database connections
def get_mongo_client():
    return pymongo.MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)

def get_postgres_connection():
    return psycopg2.connect(settings.POSTGRES_URI, connect_timeout=5)

def get_redis_client():
    return redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)

# Authentication - using the new AuthService
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return AuthService.verify_token(credentials.credentials)

# Health check
@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint with service status"""
    return await health_check()

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return prometheus_client.generate_latest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Database test endpoints
@app.get("/test-mongo")
async def test_mongo():
    try:
        client = get_mongo_client()
        db = client.vanta_ledger
        result = db.test.insert_one({"test": "data", "timestamp": datetime.now()})
        db.test.delete_one({"_id": result.inserted_id})
        return {"status": "MongoDB connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(e)}")

@app.get("/test-postgres")
async def test_postgres():
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "PostgreSQL connection successful", "version": version[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PostgreSQL connection failed: {str(e)}")

@app.get("/test-redis")
async def test_redis():
    try:
        r = get_redis_client()
        r.set("test", "data")
        result = r.get("test")
        r.delete("test")
        return {"status": "Redis connection successful", "test_value": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")


# Legacy endpoints for backward compatibility

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500) 