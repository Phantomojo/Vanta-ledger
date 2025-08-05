#!/usr/bin/env python3
"""
Vanta Ledger Backend - Local MongoDB Version
Self-hosted MongoDB for complete data control
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import glob

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import jwt
from passlib.context import CryptContext
import uvicorn
import psycopg2
from psycopg2.extras import RealDictCursor

# MongoDB Local Connection
MONGO_URI = "mongodb://vanta_ledger_app:vanta_ledger_pass@localhost:27017/vanta_ledger"
# Alternative: "mongodb://admin:admin123@localhost:27017/vanta_ledger?authSource=admin"

# Initialize FastAPI app
app = FastAPI(
    title="Vanta Ledger API - Local MongoDB",
    description="Self-hosted document management system with local MongoDB",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client.vanta_ledger
    print("✅ Connected to local MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    client = None
    db = None

# Collections
companies_collection = db.companies if db is not None else None
projects_collection = db.projects if db is not None else None
users_collection = db.users if db is not None else None
ledger_collection = db.ledger if db is not None else None
documents_collection = db.documents if db is not None else None
document_stats_collection = db.document_stats if db is not None else None
extracted_data_collection = db.extracted_data if db is not None else None

# PostgreSQL Connection for extracted data
POSTGRES_URI = "postgresql://vanta_user:kQ5afx%2FQwEInsGMsQH8ka7%2BZPnPThFDe75wZjNHvZuQ%3D@localhost:5432/vanta_ledger"
database = None

def get_database():
    """Get PostgreSQL database connection"""
    global database
    if database is None or database.closed:
        database = psycopg2.connect(POSTGRES_URI)
    return database

async def get_database_async():
    """Get PostgreSQL database connection for async context"""
    return get_database()

# Global cache for document metadata
document_cache = {}
cache_last_updated = None
CACHE_DURATION = 300  # 5 minutes

# Thread pool for file operations
file_executor = ThreadPoolExecutor(max_workers=4)

# Initialize sample data
def initialize_sample_data():
    """Initialize sample data for local MongoDB"""
    try:
        # Sample companies
        if companies_collection is not None and companies_collection.count_documents({}) == 0:
            companies_collection.insert_many([
                {
                    "id": "1",
                    "name": "Vanta Ledger Ltd",
                    "industry": "Technology",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": "2", 
                    "name": "TechCorp Solutions",
                    "industry": "Software",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": "3",
                    "name": "Global Innovations",
                    "industry": "Consulting",
                    "created_at": datetime.now(timezone.utc)
                }
            ])
            print("✅ Sample companies created")

        # Sample projects
        if projects_collection is not None and projects_collection.count_documents({}) == 0:
            projects_collection.insert_many([
                {
                    "id": "1",
                    "name": "Digital Transformation",
                    "company_id": "1",
                    "status": "active",
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31",
                    "budget": 500000,
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": "2",
                    "name": "Cloud Migration",
                    "company_id": "2", 
                    "status": "planning",
                    "start_date": "2025-03-01",
                    "end_date": "2025-08-31",
                    "budget": 300000,
                    "created_at": datetime.now(timezone.utc)
                }
            ])
            print("✅ Sample projects created")

        # Sample users
        if users_collection is not None and users_collection.count_documents({}) == 0:
            hashed_password = pwd_context.hash("admin123")
            users_collection.insert_one({
                "username": "admin",
                "email": "admin@vantaledger.com",
                "hashed_password": hashed_password,
                "role": "admin",
                "created_at": datetime.now(timezone.utc)
            })
            print("✅ Sample users created")

        # Sample ledger entries
        if ledger_collection is not None and ledger_collection.count_documents({}) == 0:
            ledger_collection.insert_many([
                {
                    "id": "1",
                    "project_id": "1",
                    "company_id": "1",
                    "type": "income",
                    "amount": 50000,
                    "description": "Project milestone payment",
                    "date": "2025-01-15",
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "id": "2",
                    "project_id": "1", 
                    "company_id": "1",
                    "type": "expense",
                    "amount": 15000,
                    "description": "Software licenses",
                    "date": "2025-01-20",
                    "created_at": datetime.now(timezone.utc)
                }
            ])
            print("✅ Sample ledger entries created")

    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Document processing functions
def get_document_hash(file_path: str) -> str:
    """Generate MD5 hash for file change detection"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""

def load_document_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """Load and parse document metadata from analysis file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract file info - use analysis file size if txt file doesn't exist
        txt_file_path = file_path.replace('_analysis.json', '.txt')
        try:
            file_stat = os.stat(txt_file_path)
            file_size = file_stat.st_size
        except FileNotFoundError:
            # Use analysis file size if txt file doesn't exist
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
        
        return {
            "id": str(data.get("doc_id", data.get("id", ""))),
            "filename": data.get("filename", f"document_{data.get('doc_id', data.get('id', ''))}.json"),
            "title": data.get("title", f"Document {data.get('doc_id', data.get('id', ''))}"),
            "file_type": data.get("file_type", "application/json"),
            "upload_date": data.get("upload_date", datetime.now().isoformat()),
            "size": file_size,
            "status": "analyzed",
            "category": data.get("category", "unknown"),
            "type": data.get("type", "unknown"),
            "companies": data.get("companies", []),
            "projects": data.get("projects", []),
            "financial_data": data.get("financial_data", []),
            "dates": data.get("dates", []),
            "keywords": data.get("keywords", []),
            "file_hash": get_document_hash(file_path)
        }
    except Exception as e:
        print(f"Error loading metadata from {file_path}: {e}")
        return None

def build_document_cache():
    """Build document cache from processed files"""
    global document_cache, cache_last_updated
    
    if cache_last_updated and (datetime.now(timezone.utc) - cache_last_updated).seconds < CACHE_DURATION:
        return list(document_cache.values())
    
    print("🔄 Building document cache...")
    
    # Find all analysis files
    analysis_files = glob.glob("processed_documents/*_analysis.json")
    
    if not analysis_files:
        print("❌ No analysis files found")
        return []
    
    # Process files in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(load_document_metadata, analysis_files))
    
    # Filter out None results and update cache
    documents = [doc for doc in results if doc is not None]
    documents.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    
    document_cache = {doc["id"]: doc for doc in documents}
    cache_last_updated = datetime.now(timezone.utc)
    
    print(f"✅ Cache built: {len(documents)} documents")
    return documents

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Vanta Ledger Local MongoDB API is operational",
        "database": "local_mongodb",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/simple-auth")
async def simple_auth(username: str, password: str):
    """Simple authentication endpoint"""
    try:
        if username == "admin" and password == "admin123":
            access_token = create_access_token(data={"sub": username})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    try:
        return {
            "username": current_user,
            "role": "admin",
            "email": "admin@vantaledger.com"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/test-auth")
async def test_auth(current_user = Depends(get_current_user)):
    """Test authentication without MongoDB access"""
    return {"message": "Authentication successful", "user": current_user}

@app.get("/companies/")
async def get_companies(current_user = Depends(get_current_user)):
    """Get all companies"""
    try:
        if companies_collection is None:
            return []
        companies = list(companies_collection.find({}, {"_id": 0}))
        return companies
    except Exception as e:
        print(f"Error accessing companies collection: {e}")
        return []

@app.get("/projects/")
async def get_projects(current_user = Depends(get_current_user)):
    """Get all projects"""
    try:
        if projects_collection is None:
            return []
        projects = list(projects_collection.find({}, {"_id": 0}))
        return projects
    except Exception as e:
        print(f"Error accessing projects collection: {e}")
        return []

@app.get("/ledger/")
async def get_ledger(current_user = Depends(get_current_user)):
    """Get all ledger entries"""
    try:
        if ledger_collection is None:
            return []
        ledger = list(ledger_collection.find({}, {"_id": 0}))
        return ledger
    except Exception as e:
        print(f"Error accessing ledger collection: {e}")
        return []

@app.get("/upload/documents")
async def get_uploaded_documents(
    page: int = 1,
    limit: int = 100,
    refresh_cache: bool = False,
    use_mongodb: bool = True,
    current_user = Depends(get_current_user)
):
    """Get uploaded documents - Now with local MongoDB support"""
    try:
        if use_mongodb and documents_collection is not None:
            # Use local MongoDB
            skip = (page - 1) * limit
            
            cursor = documents_collection.find({}).sort("upload_date", -1).skip(skip).limit(limit)
            documents = list(cursor)
            
            total_documents = documents_collection.count_documents({})
            
            # Convert MongoDB documents to API format
            api_documents = []
            for doc in documents:
                api_doc = {
                    "id": doc.get("document_id", doc.get("id", "")),
                    "filename": doc.get("filename", ""),
                    "title": doc.get("title", ""),
                    "file_type": doc.get("file_type", ""),
                    "upload_date": doc.get("upload_date", ""),
                    "size": doc.get("size", 0),
                    "status": doc.get("status", ""),
                    "company_id": None,
                    "project_id": None,
                    "category": doc.get("category", ""),
                    "type": doc.get("type", ""),
                    "companies": doc.get("companies", []),
                    "projects": doc.get("projects", []),
                    "financial_data": doc.get("financial_data", []),
                    "dates": doc.get("dates", []),
                    "keywords": doc.get("keywords", [])
                }
                api_documents.append(api_doc)
            
            return {
                "success": True,
                "documents": api_documents,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_documents,
                    "pages": (total_documents + limit - 1) // limit
                },
                "total_available": total_documents,
                "source": "local_mongodb"
            }
        else:
            # Fallback to file-based approach
            if refresh_cache:
                global cache_last_updated
                cache_last_updated = None
            
            all_documents = build_document_cache()
            
            if not all_documents:
                return {
                    "success": True,
                    "documents": [],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": 0,
                        "pages": 0
                    },
                    "total_available": 0,
                    "source": "file_cache"
                }
            
            total_documents = len(all_documents)
            start_index = (page - 1) * limit
            end_index = start_index + limit
            documents = all_documents[start_index:end_index]
            
            return {
                "success": True,
                "documents": documents,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_documents,
                    "pages": (total_documents + limit - 1) // limit
                },
                "total_available": total_documents,
                "source": "file_cache"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@app.get("/documents/stats")
async def get_document_stats(current_user = Depends(get_current_user)):
    """Get comprehensive document statistics from local MongoDB"""
    try:
        if document_stats_collection is not None:
            # Try to get stats from MongoDB first
            stats_doc = document_stats_collection.find_one({"_id": "current"})
            
            if stats_doc and stats_doc.get("stats"):
                stats = stats_doc["stats"]
                
                return {
                    "success": True,
                    "stats": {
                        "total_documents": stats.get("total_documents", 0),
                        "total_size_mb": (stats.get("total_size", 0) / (1024 * 1024)),
                        "document_types": {t: 1 for t in stats.get("document_types", [])},
                        "companies": {c: 1 for c in stats.get("companies", []) if c},
                        "projects": {p: 1 for p in stats.get("projects", []) if p},
                        "date_range": {
                            "earliest": stats.get("earliest_date"),
                            "latest": stats.get("latest_date")
                        },
                        "financial_summary": {
                            "total_income": stats.get("total_income", 0),
                            "total_expenses": stats.get("total_expenses", 0),
                            "currencies": stats.get("currencies", [])
                        }
                    },
                    "source": "local_mongodb",
                    "last_updated": stats_doc.get("updated_at")
                }
        
        # Fallback to file-based calculation
        documents = build_document_cache()
        
        stats = {
            "total_documents": len(documents),
            "total_size_mb": sum(doc.get('size', 0) for doc in documents) / (1024 * 1024),
            "document_types": {},
            "companies": {},
            "projects": {},
            "date_range": {
                "earliest": None,
                "latest": None
            },
            "financial_summary": {
                "total_income": 0,
                "total_expenses": 0,
                "currencies": set()
            }
        }
        
        dates = []
        
        for doc in documents:
            doc_type = doc.get('type', 'unknown')
            stats['document_types'][doc_type] = stats['document_types'].get(doc_type, 0) + 1
            
            for company in doc.get('companies', []):
                stats['companies'][company] = stats['companies'].get(company, 0) + 1
            
            for project in doc.get('projects', []):
                stats['projects'][project] = stats['projects'].get(project, 0) + 1
            
            if doc.get('upload_date'):
                dates.append(doc['upload_date'])
            
            for financial in doc.get('financial_data', []):
                amount = financial.get('amount', 0)
                currency = financial.get('currency', 'USD')
                f_type = financial.get('type', 'unknown')
                
                stats['financial_summary']['currencies'].add(currency)
                
                if f_type == 'income':
                    stats['financial_summary']['total_income'] += amount
                elif f_type == 'expense':
                    stats['financial_summary']['total_expenses'] += amount
        
        stats['financial_summary']['currencies'] = list(stats['financial_summary']['currencies'])
        
        if dates:
            dates.sort()
            stats['date_range']['earliest'] = dates[0]
            stats['date_range']['latest'] = dates[-1]
        
        return {
            "success": True,
            "stats": stats,
            "source": "file_cache"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/documents/migrate-to-mongodb")
async def migrate_documents_to_mongodb(current_user = Depends(get_current_user)):
    """Migrate all documents to local MongoDB"""
    try:
        if documents_collection is None:
            raise HTTPException(status_code=500, detail="MongoDB not available")
        
        print("🔄 Storing documents in local MongoDB...")
        
        # Get documents from cache
        all_documents = build_document_cache()
        
        if not all_documents:
            return {
                "success": True,
                "message": "No documents to migrate",
                "total_documents": 0
            }
        
        # Clear existing documents
        documents_collection.delete_many({})
        
        # Prepare documents for MongoDB
        mongo_documents = []
        for doc in all_documents:
            mongo_doc = {
                "document_id": doc["id"],
                "filename": doc["filename"],
                "title": doc["title"],
                "file_type": doc["file_type"],
                "upload_date": doc["upload_date"],
                "size": doc["size"],
                "status": doc["status"],
                "category": doc["category"],
                "type": doc["type"],
                "companies": doc["companies"],
                "projects": doc["projects"],
                "financial_data": doc["financial_data"],
                "dates": doc["dates"],
                "keywords": doc["keywords"],
                "file_hash": doc.get("file_hash"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            mongo_documents.append(mongo_doc)
        
        # Insert documents in batches
        batch_size = 1000
        for i in range(0, len(mongo_documents), batch_size):
            batch = mongo_documents[i:i + batch_size]
            documents_collection.insert_many(batch)
        
        # Create indexes for better performance
        documents_collection.create_index("document_id", unique=True)
        documents_collection.create_index("type")
        documents_collection.create_index("category")
        documents_collection.create_index("companies")
        documents_collection.create_index("upload_date")
        documents_collection.create_index("keywords")
        
        print(f"✅ Stored {len(mongo_documents)} documents in local MongoDB")
        
        total_docs = documents_collection.count_documents({})
        
        return {
            "success": True,
            "message": "Documents successfully migrated to local MongoDB",
            "total_documents": total_docs,
            "benefits": [
                "Faster queries with indexed searches",
                "Real-time statistics and aggregations",
                "Better scalability for millions of documents",
                "Complete data ownership and control",
                "Local network performance"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.post("/documents/refresh-cache")
async def refresh_document_cache(current_user = Depends(get_current_user)):
    """Force refresh of document cache"""
    try:
        global cache_last_updated
        cache_last_updated = None
        
        documents = build_document_cache()
        
        return {
            "success": True,
            "message": "Document cache refreshed",
            "total_documents": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache refresh failed: {str(e)}")

@app.get("/extracted-data/")
async def get_extracted_data(
    page: int = 1,
    limit: int = 100,
    min_confidence: float = 0.0,
    has_amount: bool = None,
    transaction_type: str = None,
    category: str = None,
    current_user = Depends(get_current_user)
):
    """Get extracted financial data with filtering options"""
    try:
        db_connection = await get_database_async()
        cursor = db_connection.cursor(cursor_factory=RealDictCursor)
        
        # Build filter conditions
        conditions = ["extraction_method = 'json_analysis'"]
        params = []
        param_count = 0
        
        if min_confidence > 0:
            param_count += 1
            conditions.append(f"confidence_score >= %s")
            params.append(min_confidence)
        
        if has_amount is not None:
            if has_amount:
                conditions.append("amount IS NOT NULL")
            else:
                conditions.append("amount IS NULL")
        
        if transaction_type:
            param_count += 1
            conditions.append(f"transaction_type = %s")
            params.append(transaction_type)
        
        if category:
            param_count += 1
            conditions.append(f"category = %s")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM extracted_data WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['total']
        
        # Get paginated results
        offset = (page - 1) * limit
        query = f"""
        SELECT 
            id,
            document_id,
            filename,
            company_name,
            transaction_date,
            amount,
            currency,
            transaction_type,
            category,
            description,
            reference_number,
            vendor_name,
            invoice_number,
            tax_amount,
            payment_method,
            confidence_score,
            extraction_method,
            extracted_at
        FROM extracted_data 
        WHERE {where_clause}
        ORDER BY extracted_at DESC
        LIMIT %s OFFSET %s
        """
        
        query_params = params + [limit, offset]
        cursor.execute(query, query_params)
        results = cursor.fetchall()
        
        # Convert to API format
        api_documents = []
        for row in results:
            api_doc = {
                "id": row['id'],
                "document_id": row['document_id'],
                "filename": row['filename'],
                "company_name": row['company_name'],
                "transaction_date": str(row['transaction_date']) if row['transaction_date'] else None,
                "amount": float(row['amount']) if row['amount'] else None,
                "currency": row['currency'],
                "transaction_type": row['transaction_type'],
                "category": row['category'],
                "description": row['description'],
                "reference_number": row['reference_number'],
                "vendor_name": row['vendor_name'],
                "invoice_number": row['invoice_number'],
                "tax_amount": float(row['tax_amount']) if row['tax_amount'] else None,
                "payment_method": row['payment_method'],
                "confidence_score": float(row['confidence_score']) if row['confidence_score'] else None,
                "extraction_method": row['extraction_method'],
                "extracted_at": str(row['extracted_at']) if row['extracted_at'] else None
            }
            api_documents.append(api_doc)
        
        cursor.close()
        
        return {
            "success": True,
            "data": api_documents,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extracted data: {str(e)}")

@app.get("/extracted-data/stats")
async def get_extracted_data_stats(current_user = Depends(get_current_user)):
    """Get comprehensive statistics about extracted data"""
    try:
        if extracted_data_collection is None:
            raise HTTPException(status_code=500, detail="Extracted data collection not available")
        
        # Get basic counts
        total_documents = extracted_data_collection.count_documents({})
        documents_with_amounts = extracted_data_collection.count_documents({"amount": {"$exists": True, "$ne": None}})
        documents_with_dates = extracted_data_collection.count_documents({"transaction_date": {"$exists": True, "$ne": None}})
        documents_with_companies = extracted_data_collection.count_documents({"company_name": {"$exists": True, "$ne": None}})
        
        # Get average confidence
        avg_confidence_result = list(extracted_data_collection.aggregate([
            {"$group": {"_id": None, "avg": {"$avg": "$confidence_score"}}}
        ]))
        avg_confidence = avg_confidence_result[0].get("avg", 0.0) if avg_confidence_result else 0.0
        
        # Get transaction type distribution
        transaction_types = list(extracted_data_collection.aggregate([
            {"$group": {"_id": "$transaction_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        
        # Get category distribution
        categories = list(extracted_data_collection.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        
        # Get total financial value
        total_amount_result = list(extracted_data_collection.aggregate([
            {"$match": {"amount": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]))
        total_amount = total_amount_result[0].get("total", 0.0) if total_amount_result else 0.0
        
        return {
            "success": True,
            "statistics": {
                "total_documents": total_documents,
                "documents_with_amounts": documents_with_amounts,
                "documents_with_dates": documents_with_dates,
                "documents_with_companies": documents_with_companies,
                "average_confidence": round(avg_confidence, 3),
                "total_financial_value": total_amount,
                "success_rate": round((total_documents / 3154) * 100, 2) if total_documents > 0 else 0
            },
            "transaction_types": [
                {"type": item["_id"], "count": item["count"]} 
                for item in transaction_types if item["_id"]
            ],
            "categories": [
                {"category": item["_id"], "count": item["count"]} 
                for item in categories if item["_id"]
            ],
            "extraction_summary": {
                "engine_version": "2.0.0",
                "data_source": "processed_json_files",
                "extraction_date": "2025-08-04T01:48:03.497Z"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extracted data stats: {str(e)}")

@app.get("/test-analytics")
async def test_analytics_endpoint(current_user = Depends(get_current_user)):
    """Test analytics endpoint"""
    try:
        db_conn = await get_database_async()
        cursor = db_conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT COUNT(*) as total FROM extracted_data WHERE extraction_method = \'json_analysis\'')
        result = cursor.fetchone()
        cursor.close()
        
        return {
            "success": True,
            "total": result['total']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@app.get("/extracted-data/analytics")
async def get_extracted_data_analytics(current_user = Depends(get_current_user)):
    """Get analytics and statistics for extracted data"""
    try:
        db_connection = await get_database_async()
        cursor = db_connection.cursor(cursor_factory=RealDictCursor)
        
        # Get total counts
        total_query = "SELECT COUNT(*) as total FROM extracted_data WHERE extraction_method = 'json_analysis'"
        cursor.execute(total_query)
        total_count = cursor.fetchone()['total']
        
        # Get confidence statistics
        confidence_query = """
        SELECT 
            AVG(confidence_score) as avg_confidence,
            MIN(confidence_score) as min_confidence,
            MAX(confidence_score) as max_confidence,
            COUNT(CASE WHEN confidence_score >= 0.8 THEN 1 END) as high_confidence_count
        FROM extracted_data 
        WHERE extraction_method = 'json_analysis'
        """
        cursor.execute(confidence_query)
        confidence_result = cursor.fetchone()
        
        # Get amount statistics
        amount_query = """
        SELECT 
            COUNT(CASE WHEN amount IS NOT NULL THEN 1 END) as documents_with_amounts,
            SUM(CASE WHEN amount IS NOT NULL THEN amount ELSE 0 END) as total_amount,
            AVG(CASE WHEN amount IS NOT NULL THEN amount END) as avg_amount,
            MIN(CASE WHEN amount IS NOT NULL THEN amount END) as min_amount,
            MAX(CASE WHEN amount IS NOT NULL THEN amount END) as max_amount
        FROM extracted_data 
        WHERE extraction_method = 'json_analysis'
        """
        cursor.execute(amount_query)
        amount_result = cursor.fetchone()
        
        # Get transaction type distribution
        type_query = """
        SELECT 
            transaction_type,
            COUNT(*) as count
        FROM extracted_data 
        WHERE extraction_method = 'json_analysis' AND transaction_type IS NOT NULL
        GROUP BY transaction_type
        ORDER BY count DESC
        """
        cursor.execute(type_query)
        type_results = cursor.fetchall()
        
        # Get category distribution
        category_query = """
        SELECT 
            category,
            COUNT(*) as count
        FROM extracted_data 
        WHERE extraction_method = 'json_analysis' AND category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10
        """
        cursor.execute(category_query)
        category_results = cursor.fetchall()
        
        cursor.close()
        
        return {
            "success": True,
            "data": {
                "total_documents": total_count,
                "confidence_stats": {
                    "average": float(confidence_result['avg_confidence']) if confidence_result['avg_confidence'] else 0,
                    "minimum": float(confidence_result['min_confidence']) if confidence_result['min_confidence'] else 0,
                    "maximum": float(confidence_result['max_confidence']) if confidence_result['max_confidence'] else 0,
                    "high_confidence_count": confidence_result['high_confidence_count'] if confidence_result['high_confidence_count'] else 0
                },
                "amount_stats": {
                    "documents_with_amounts": amount_result['documents_with_amounts'] if amount_result['documents_with_amounts'] else 0,
                    "total_amount": float(amount_result['total_amount']) if amount_result['total_amount'] else 0,
                    "average_amount": float(amount_result['avg_amount']) if amount_result['avg_amount'] else 0,
                    "minimum_amount": float(amount_result['min_amount']) if amount_result['min_amount'] else 0,
                    "maximum_amount": float(amount_result['max_amount']) if amount_result['max_amount'] else 0
                },
                "transaction_types": [{"type": row['transaction_type'], "count": row['count']} for row in type_results],
                "categories": [{"category": row['category'], "count": row['count']} for row in category_results]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@app.get("/extracted-data/export")
async def export_extracted_data(
    format: str = "json",
    min_confidence: float = 0.0,
    current_user = Depends(get_current_user)
):
    """Export extracted data in various formats"""
    try:
        db_connection = await get_database_async()
        cursor = db_connection.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            document_id,
            filename,
            company_name,
            transaction_date,
            amount,
            currency,
            transaction_type,
            category,
            description,
            reference_number,
            vendor_name,
            invoice_number,
            tax_amount,
            payment_method,
            confidence_score,
            extraction_method,
            extracted_at
        FROM extracted_data 
        WHERE extraction_method = 'json_analysis' 
        AND confidence_score >= %s
        ORDER BY extracted_at DESC
        """
        
        cursor.execute(query, (min_confidence,))
        results = cursor.fetchall()
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Document ID", "Filename", "Company Name", "Transaction Date", 
                "Amount", "Currency", "Transaction Type", "Category", 
                "Description", "Reference Number", "Vendor Name", 
                "Invoice Number", "Tax Amount", "Payment Method", 
                "Confidence Score", "Extraction Method", "Extracted At"
            ])
            
            # Write data
            for row in results:
                writer.writerow([
                    row['document_id'], row['filename'], row['company_name'],
                    row['transaction_date'], row['amount'], row['currency'],
                    row['transaction_type'], row['category'], row['description'],
                    row['reference_number'], row['vendor_name'], row['invoice_number'],
                    row['tax_amount'], row['payment_method'], row['confidence_score'],
                    row['extraction_method'], row['extracted_at']
                ])
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=extracted_data.csv"}
            )
        else:
            # Return JSON
            return {
                "success": True,
                "data": [
                    {
                        "document_id": row['document_id'],
                        "filename": row['filename'],
                        "company_name": row['company_name'],
                        "transaction_date": str(row['transaction_date']) if row['transaction_date'] else None,
                        "amount": float(row['amount']) if row['amount'] else None,
                        "currency": row['currency'],
                        "transaction_type": row['transaction_type'],
                        "category": row['category'],
                        "description": row['description'],
                        "reference_number": row['reference_number'],
                        "vendor_name": row['vendor_name'],
                        "invoice_number": row['invoice_number'],
                        "tax_amount": float(row['tax_amount']) if row['tax_amount'] else None,
                        "payment_method": row['payment_method'],
                        "confidence_score": float(row['confidence_score']) if row['confidence_score'] else None,
                        "extraction_method": row['extraction_method'],
                        "extracted_at": str(row['extracted_at']) if row['extracted_at'] else None
                    }
                    for row in results
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Initialize data on startup
if __name__ == "__main__":
    print("🚀 Starting Vanta Ledger Local MongoDB API...")
    print("📊 Database: vanta_ledger")
    print("🌐 Server: http://localhost:8500")
    print("👤 Admin Login: admin/admin123")
    
    # Initialize sample data
    initialize_sample_data()
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=8500) 