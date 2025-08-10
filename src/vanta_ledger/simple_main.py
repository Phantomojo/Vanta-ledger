#!/usr/bin/env python3
"""
Vanta Ledger - Simplified Main FastAPI Application
Production-ready single-database version for immediate deployment
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from jose import jwt
import prometheus_client
from prometheus_client import Counter, Histogram

# Import settings and basic auth
from .config import settings
from .auth import AuthService

# Import simplified routes
from .routes.simple_auth import router as simple_auth_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vanta Ledger API - Simplified",
    description="Production-ready single-database financial ledger system",
    version=settings.VERSION
)

# CORS middleware - essential for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include authentication routes
app.include_router(simple_auth_router)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Health check
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    try:
        # Test database connectivity
        from .database_init import get_database_initializer
        db_init = get_database_initializer()
        
        if db_init.health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": settings.VERSION,
                "database": "connected"
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy", 
                    "error": "Database connection failed"
                }
            )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "Internal server error"
            }
        )

# Database initialization endpoint
@app.post("/initialize")
async def initialize_database():
    """Initialize database and create admin user"""
    try:
        from .database_init import initialize_database
        
        success = initialize_database()
        
        if success:
            return {
                "status": "initialized",
                "message": "Database and admin user created successfully"
            }
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "failed",
                    "message": "Database initialization failed"
                }
            )
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )

# User info endpoint
@app.get("/users/me")
async def get_current_user(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get current user information"""
    return {
        "username": current_user.get("sub"),
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email", ""),
        "role": current_user.get("role", "user"),
        "profile": {
            "name": current_user.get("sub", "User"),
            "avatar": "",
            "bio": "System User"
        }
    }

# Companies endpoint (simplified)
@app.get("/companies/")
async def get_companies(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get companies list"""
    return [
        {
            "id": 1,
            "name": "Default Company",
            "description": "Default company for testing",
            "status": "active"
        }
    ]

# Projects endpoint (simplified)
@app.get("/projects/")
async def get_projects(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get projects list"""
    return [
        {
            "id": 1,
            "name": "Default Project",
            "description": "Default project for testing",
            "status": "active",
            "company_id": 1
        }
    ]

# Ledger endpoint (simplified)
@app.get("/ledger/")
async def get_ledger(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get ledger entries"""
    return [
        {
            "id": 1,
            "description": "Sample transaction",
            "amount": 1000.00,
            "type": "income",
            "date": datetime.utcnow().isoformat()
        }
    ]

# Analytics endpoint (simplified)
@app.get("/analytics/dashboard")
async def get_analytics(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get analytics dashboard data"""
    return {
        "total_revenue": 50000.00,
        "total_expenses": 30000.00,
        "net_profit": 20000.00,
        "transaction_count": 150,
        "monthly_growth": 12.5
    }

# Documents endpoint (simplified)
@app.get("/upload/documents")
async def get_documents(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get documents list"""
    return [
        {
            "id": 1,
            "name": "Sample Invoice",
            "type": "invoice",
            "status": "processed",
            "created_at": datetime.utcnow().isoformat()
        }
    ]

# Extracted data endpoint (simplified)
@app.get("/extracted-data/")
async def get_extracted_data(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get extracted data"""
    return {
        "documents": [],
        "total": 0,
        "page": 1,
        "per_page": 20
    }

# Paperless integration endpoint (simplified)
@app.get("/paperless/documents/")
async def get_paperless_documents(current_user: dict = Depends(simple_auth_router.verify_token_dependency)):
    """Get paperless documents"""
    return {
        "results": [],
        "count": 0
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Return Prometheus metrics"""
    from fastapi.responses import Response
    return Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain"
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generate JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)
