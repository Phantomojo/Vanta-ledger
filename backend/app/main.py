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

# Authentication endpoints
@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Secure login endpoint with password hashing"""
    try:
        # Get user from database (implement proper user management)
        user = await get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/auth/logout")
async def logout(current_user: dict = Depends(verify_token)):
    """Logout endpoint - add token to blacklist"""
    try:
        # Add token to blacklist (implement token revocation)
        await blacklist_token(current_user.get("jti"))
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/auth/refresh")
async def refresh_token(current_user: dict = Depends(verify_token)):
    """Refresh access token"""
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": current_user.get("sub"), "user_id": current_user.get("user_id")}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

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

# Document upload and processing endpoints
@app.post("/upload/documents")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(verify_token)
):
    """Upload and process a new document securely"""
    temp_file_path = None
    try:
        # Get user ID from token
        user_id = current_user.get("user_id", "unknown")
        
        # Save file securely using the secure file handler
        temp_file_path, secure_filename = secure_file_handler.save_file_securely(
            file, user_id, settings.UPLOAD_DIR
        )
        
        # Process document
        result = document_processor.process_document(str(temp_file_path), file.filename)
        
        # Add security metadata
        result["security"] = {
            "uploaded_by": user_id,
            "secure_filename": secure_filename,
            "original_filename": file.filename,
            "file_size": file.size,
            "upload_timestamp": datetime.now().isoformat()
        }
        
        return {
            "message": "Document uploaded and processed successfully",
            "doc_id": result['doc_id'],
            "original_filename": result['original_filename'],
            "type": result['analysis']['type'],
            "summary": result['analysis']['summary'],
            "security": result["security"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")
    finally:
        # Always cleanup temporary file
        if temp_file_path:
            secure_file_handler.cleanup_temp_file(temp_file_path)

@app.get("/upload/documents")
async def list_documents(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(verify_token)
):
    """List all processed documents with pagination"""
    try:
        documents = document_processor.list_documents()
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_docs = documents[start_idx:end_idx]
        
        return {
            "documents": paginated_docs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(documents),
                "pages": (len(documents) + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.get("/upload/documents/{document_id}")
async def get_document_details(
    document_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get detailed information about a specific document"""
    try:
        # Get analysis data
        analysis = document_processor.get_document_analysis(document_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get text content
        content = document_processor.get_document_content(document_id)
        if not content:
            content = "Document content not available"
        
        return {
            "doc_id": document_id,
            "content": content,
            "analysis": analysis,
            "metadata": {
                "type": analysis.get('type'),
                "word_count": analysis.get('metadata', {}).get('word_count', 0),
                "processed_at": analysis.get('processed_at')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document details: {str(e)}")

@app.get("/upload/documents/{document_id}/content")
async def get_document_content(
    document_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get raw text content of a document"""
    try:
        content = document_processor.get_document_content(document_id)
        if not content:
            raise HTTPException(status_code=404, detail="Document content not found")
        
        return {"content": content}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document content: {str(e)}")

@app.post("/upload/documents/{document_id}/analyze")
async def reanalyze_document(
    document_id: str,
    current_user: dict = Depends(verify_token)
):
    """Re-analyze a document with updated AI processing"""
    try:
        # Get existing content
        content = document_processor.get_document_content(document_id)
        if not content:
            raise HTTPException(status_code=404, detail="Document content not found")
        
        # Re-analyze
        analysis = document_processor._analyze_document(content, document_id)
        document_processor._store_analysis(document_id, analysis)
        
        return {
            "message": "Document re-analyzed successfully",
            "doc_id": document_id,
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-analyze document: {str(e)}")

# Legacy endpoints for backward compatibility
@app.get("/companies/")
async def get_companies(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(verify_token)
):
    """Get all companies with secure pagination"""
    try:
        # Validate pagination parameters
        page, limit = input_validator.validate_pagination_params(page, limit, max_limit=100)
        
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Get total count using parameterized query
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_count = cursor.fetchone()[0]
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get companies with secure parameterized query
        cursor.execute(
            "SELECT postgres_id, name, industry, revenue FROM companies ORDER BY name LIMIT %s OFFSET %s",
            (limit, offset)
        )
        companies = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "companies": [
                {
                    "id": company[0],
                    "name": company[1],
                    "industry": company[2],
                    "revenue": company[3]
                }
                for company in companies
            ],
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@app.get("/companies/{company_id}")
async def get_company(company_id: int, current_user: dict = Depends(verify_token)):
    """Get company by ID with input validation"""
    try:
        # Validate company_id
        company_id = input_validator.validate_integer(company_id, min_value=1, field_name="company_id")
        
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Use parameterized query to prevent SQL injection
        cursor.execute(
            "SELECT postgres_id, name, industry, revenue FROM companies WHERE postgres_id = %s",
            (company_id,)
        )
        company = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return {
            "id": company[0],
            "name": company[1],
            "industry": company[2],
            "revenue": company[3]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_company: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@app.get("/projects/")
async def get_projects(current_user: dict = Depends(verify_token)):
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT postgres_id, name, status, budget FROM projects LIMIT 50")
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": project[0],  # Map postgres_id to id for frontend compatibility
                "name": project[1],
                "status": project[2],
                "budget": project[3]
            }
            for project in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")

@app.get("/projects/{project_id}")
async def get_project(project_id: int, current_user: dict = Depends(verify_token)):
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT postgres_id, name, status, budget FROM projects WHERE postgres_id = %s", (project_id,))
        project = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "id": project[0],
            "name": project[1],
            "status": project[2],
            "budget": project[3]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project: {str(e)}")

@app.get("/ledger/")
async def get_ledger_entries(current_user: dict = Depends(verify_token)):
    try:
        client = get_mongo_client()
        db = client.vanta_ledger
        collection = db.ledger_entries
        
        entries = list(collection.find({}, {"_id": 0}).limit(50))
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ledger entries: {str(e)}")

@app.get("/ledger/company/{company_id}")
async def get_company_ledger(company_id: str, current_user: dict = Depends(verify_token)):
    try:
        client = get_mongo_client()
        db = client.vanta_ledger
        collection = db.ledger_entries
        
        entries = list(collection.find({"company_id": company_id}, {"_id": 0}))
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch company ledger: {str(e)}")

@app.get("/extracted-data/analytics")
async def get_analytics(current_user: dict = Depends(verify_token)):
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Get financial analytics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount
            FROM financial_transactions
        """)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="No financial data found")
        
        return {
            "total_transactions": result[0] or 0,
            "total_amount": float(result[1]) if result[1] else 0,
            "average_amount": float(result[2]) if result[2] else 0,
            "min_amount": float(result[3]) if result[3] else 0,
            "max_amount": float(result[4]) if result[4] else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

# Additional endpoints for completeness
@app.get("/users/")
async def get_users(current_user: dict = Depends(verify_token)):
    return [{"id": 1, "username": "admin", "role": "admin"}]

@app.get("/config/")
async def get_config(current_user: dict = Depends(verify_token)):
    return {
        "version": settings.VERSION,
        "features": {
            "document_processing": True,
            "ocr": True,
            "ai_analysis": True,
            "file_upload": True
        }
    }

@app.get("/notifications/")
async def get_notifications(current_user: dict = Depends(verify_token)):
    return []

@app.get("/notifications/settings/")
async def get_notification_settings(current_user: dict = Depends(verify_token)):
    return {"email": True, "push": False}

# AI Analytics Endpoints
@app.post("/ai/analyze-document/{document_id}")
async def analyze_document_ai(document_id: str, current_user: dict = Depends(verify_token)):
    """Analyze document using AI/LLM for intelligent insights"""
    try:
        # Get document from database
        client = get_mongo_client()
        db = client.vanta_ledger
        collection = db.processed_documents
        
        document = collection.find_one({"document_id": document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Analyze with AI
        analysis = await ai_analytics_service.analyze_document_intelligence(document)
        
        # Save analysis to database
        collection.update_one(
            {"document_id": document_id},
            {"$set": {"ai_analysis": analysis}}
        )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@app.get("/ai/company-report/{company_id}")
async def generate_company_report(company_id: str, current_user: dict = Depends(verify_token)):
    """Generate comprehensive company report using AI analysis"""
    try:
        # Get all documents for company
        client = get_mongo_client()
        db = client.vanta_ledger
        collection = db.processed_documents
        
        documents = list(collection.find({"company": company_id}))
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found for company")
        
        # Generate AI report
        report = await ai_analytics_service.generate_company_report(company_id, documents)
        
        # Save report to database
        db.ai_reports.insert_one(report)
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company report generation failed: {str(e)}")

@app.get("/ai/system-analytics")
async def generate_system_analytics(current_user: dict = Depends(verify_token)):
    """Generate system-wide analytics and insights using AI"""
    try:
        # Get all documents
        client = get_mongo_client()
        db = client.vanta_ledger
        collection = db.processed_documents
        
        all_documents = list(collection.find({}))
        if not all_documents:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Generate AI analytics
        analytics = await ai_analytics_service.generate_system_analytics(all_documents)
        
        # Save analytics to database
        db.system_analytics.insert_one(analytics)
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System analytics generation failed: {str(e)}")

@app.get("/ai/reports/")
async def list_ai_reports(current_user: dict = Depends(verify_token)):
    """List all AI-generated reports"""
    try:
        client = get_mongo_client()
        db = client.vanta_ledger
        
        # Get company reports
        company_reports = list(db.ai_reports.find({}, {"_id": 0}).limit(20))
        
        # Get system analytics
        system_analytics = list(db.system_analytics.find({}, {"_id": 0}).limit(10))
        
        return {
            "company_reports": company_reports,
            "system_analytics": system_analytics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI reports: {str(e)}")

@app.get("/ai/reports/{report_id}")
async def get_ai_report(report_id: str, current_user: dict = Depends(verify_token)):
    """Get specific AI report"""
    try:
        client = get_mongo_client()
        db = client.vanta_ledger
        
        # Try to find in company reports
        report = db.ai_reports.find_one({"company_id": report_id}, {"_id": 0})
        if report:
            return report
        
        # Try to find in system analytics
        report = db.system_analytics.find_one({"report_date": report_id}, {"_id": 0})
        if report:
            return report
        
        raise HTTPException(status_code=404, detail="Report not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

# Analytics Dashboard Endpoints
@app.get("/dashboard/overview")
async def get_dashboard_overview(current_user: dict = Depends(verify_token)):
    """Get comprehensive dashboard overview"""
    try:
        mongo_client = get_mongo_client()
        postgres_conn = get_postgres_connection()
        
        overview = await analytics_dashboard.get_dashboard_overview(mongo_client, postgres_conn)
        
        postgres_conn.close()
        
        return overview
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard overview failed: {str(e)}")

@app.get("/dashboard/company/{company_id}")
async def get_company_dashboard(company_id: str, current_user: dict = Depends(verify_token)):
    """Get company-specific dashboard"""
    try:
        mongo_client = get_mongo_client()
        postgres_conn = get_postgres_connection()
        
        company_dashboard = await analytics_dashboard.get_company_dashboard(company_id, mongo_client, postgres_conn)
        
        postgres_conn.close()
        
        return company_dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company dashboard failed: {str(e)}")

@app.get("/analytics/financial")
async def get_financial_analytics(current_user: dict = Depends(verify_token)):
    """Get detailed financial analytics"""
    try:
        mongo_client = get_mongo_client()
        postgres_conn = get_postgres_connection()
        
        # Get financial data from both databases
        mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
        postgres_data = await analytics_dashboard._get_postgres_analytics(postgres_conn)
        
        financial_analytics = analytics_dashboard._combine_financial_data(mongo_data, postgres_data)
        
        postgres_conn.close()
        
        return financial_analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial analytics failed: {str(e)}")

@app.get("/analytics/compliance")
async def get_compliance_analytics(current_user: dict = Depends(verify_token)):
    """Get compliance analytics"""
    try:
        mongo_client = get_mongo_client()
        
        mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
        compliance_analytics = analytics_dashboard._get_compliance_metrics(mongo_data)
        
        return compliance_analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance analytics failed: {str(e)}")

@app.get("/analytics/processing")
async def get_processing_analytics(current_user: dict = Depends(verify_token)):
    """Get processing analytics"""
    try:
        mongo_client = get_mongo_client()
        
        mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
        processing_analytics = analytics_dashboard._get_processing_metrics(mongo_data)
        
        return processing_analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing analytics failed: {str(e)}")

@app.get("/analytics/trends")
async def get_trends_analytics(current_user: dict = Depends(verify_token)):
    """Get trends analytics"""
    try:
        mongo_client = get_mongo_client()
        
        mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
        trends_analytics = await analytics_dashboard._get_trends(mongo_data)
        
        return trends_analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trends analytics failed: {str(e)}")

@app.get("/analytics/alerts")
async def get_system_alerts(current_user: dict = Depends(verify_token)):
    """Get system alerts"""
    try:
        mongo_client = get_mongo_client()
        
        mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
        alerts = await analytics_dashboard._get_alerts(mongo_data)
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System alerts failed: {str(e)}")

@app.get("/analytics/top-performers")
async def get_top_performers(current_user: dict = Depends(verify_token)):
    """Get top performing companies"""
    try:
        mongo_client = get_mongo_client()
        
        mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
        top_performers = analytics_dashboard._get_top_performers(mongo_data)
        
        return top_performers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Top performers analytics failed: {str(e)}")

@app.get("/analytics/risk-analysis")
async def get_risk_analysis(current_user: dict = Depends(verify_token)):
    """Get comprehensive risk analysis"""
    try:
        mongo_client = get_mongo_client()
        
        mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
        risk_analysis = analytics_dashboard._get_risk_analysis(mongo_data)
        
        return risk_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500) 