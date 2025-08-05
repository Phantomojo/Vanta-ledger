#!/usr/bin/env python3
"""
Hybrid Database Manager for Vanta Ledger Backend
===============================================

Manages both PostgreSQL (for structured financial data) and MongoDB (for document storage)
with proper integration and transaction handling.

Author: Vanta Ledger Team
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from decimal import Decimal

# Database imports
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Date, Text, Boolean, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure
from pymongo.database import Database
from pymongo.collection import Collection

# Configure logging
logger = logging.getLogger(__name__)

class HybridDatabaseManager:
    """Manages both PostgreSQL and MongoDB databases with integrated operations"""
    
    def __init__(self):
        # Database configuration
        self.postgres_uri = os.getenv("POSTGRES_URI", "postgresql://vanta_user:vanta_password@localhost:5432/vanta_ledger")
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/vanta_ledger")
        
        # Database connections
        self.postgres_engine = None
        self.mongo_client = None
        self.mongo_db = None
        self.Base = declarative_base()
        
        # Initialize connections
        self._connect_databases()
    
    def _connect_databases(self):
        """Connect to both databases"""
        try:
            # Connect to PostgreSQL
            self.postgres_engine = create_engine(
                self.postgres_uri,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            logger.info("✅ Connected to PostgreSQL")
            
            # Connect to MongoDB
            self.mongo_client = MongoClient(
                self.mongo_uri,
                maxPoolSize=50,
                serverSelectionTimeoutMS=5000
            )
            self.mongo_db = self.mongo_client.vanta_ledger
            logger.info("✅ Connected to MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of both databases"""
        health_status = {
            "postgresql": {"status": "unknown", "error": None},
            "mongodb": {"status": "unknown", "error": None},
            "overall": "unknown"
        }
        
        # Check PostgreSQL
        try:
            with self.postgres_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health_status["postgresql"]["status"] = "healthy"
        except Exception as e:
            health_status["postgresql"]["status"] = "unhealthy"
            health_status["postgresql"]["error"] = str(e)
        
        # Check MongoDB
        try:
            self.mongo_client.admin.command('ping')
            health_status["mongodb"]["status"] = "healthy"
        except Exception as e:
            health_status["mongodb"]["status"] = "unhealthy"
            health_status["mongodb"]["error"] = str(e)
        
        # Overall status
        if (health_status["postgresql"]["status"] == "healthy" and 
            health_status["mongodb"]["status"] == "healthy"):
            health_status["overall"] = "healthy"
        else:
            health_status["overall"] = "unhealthy"
        
        return health_status
    
    # PostgreSQL Operations (Structured Financial Data)
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get all companies from PostgreSQL"""
        try:
            with self.postgres_engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, name, registration_number, industry, 
                           address, contact_info, tax_info, status, 
                           created_at, updated_at
                    FROM companies 
                    WHERE status = 'active'
                    ORDER BY name
                """))
                
                companies = []
                for row in result:
                    company = dict(row)
                    # Parse JSON fields
                    if company.get("address"):
                        company["address"] = json.loads(company["address"])
                    if company.get("contact_info"):
                        company["contact_info"] = json.loads(company["contact_info"])
                    if company.get("tax_info"):
                        company["tax_info"] = json.loads(company["tax_info"])
                    
                    companies.append(company)
                
                return companies
                
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            raise
    
    def get_projects(self, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get projects from PostgreSQL"""
        try:
            query = """
                SELECT p.id, p.name, p.client, p.value, p.start_date, p.end_date,
                       p.status, p.description, p.created_at, p.updated_at,
                       c.name as company_name, c.id as company_id
                FROM projects p
                JOIN companies c ON p.company_id = c.id
                WHERE p.status = 'active'
            """
            params = {}
            
            if company_id:
                query += " AND p.company_id = :company_id"
                params["company_id"] = company_id
            
            query += " ORDER BY p.created_at DESC"
            
            with self.postgres_engine.connect() as conn:
                result = conn.execute(text(query), params)
                
                projects = []
                for row in result:
                    projects.append(dict(row))
                
                return projects
                
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            raise
    
    def create_ledger_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a ledger entry in PostgreSQL (ACID compliant)"""
        try:
            with self.postgres_engine.begin() as conn:
                result = conn.execute(text("""
                    INSERT INTO ledger_entries 
                    (company_id, project_id, entry_type, category, description,
                     amount, currency, reference_number, transaction_date, approval_status)
                    VALUES (:company_id, :project_id, :entry_type, :category, :description,
                           :amount, :currency, :reference_number, :transaction_date, :approval_status)
                    RETURNING id, company_id, project_id, entry_type, category, description,
                              amount, currency, reference_number, transaction_date, approval_status,
                              created_at
                """), entry_data)
                
                ledger_entry = dict(result.fetchone())
                logger.info(f"Created ledger entry: {ledger_entry['id']}")
                return ledger_entry
                
        except Exception as e:
            logger.error(f"Error creating ledger entry: {e}")
            raise
    
    def get_ledger_entries(self, company_id: Optional[int] = None, 
                          project_id: Optional[int] = None,
                          entry_type: Optional[str] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get ledger entries from PostgreSQL"""
        try:
            query = """
                SELECT le.id, le.company_id, le.project_id, le.entry_type, le.category,
                       le.description, le.amount, le.currency, le.reference_number,
                       le.transaction_date, le.approval_status, le.created_at,
                       c.name as company_name, p.name as project_name
                FROM ledger_entries le
                JOIN companies c ON le.company_id = c.id
                LEFT JOIN projects p ON le.project_id = p.id
                WHERE 1=1
            """
            params = {}
            
            if company_id:
                query += " AND le.company_id = :company_id"
                params["company_id"] = company_id
            
            if project_id:
                query += " AND le.project_id = :project_id"
                params["project_id"] = project_id
            
            if entry_type:
                query += " AND le.entry_type = :entry_type"
                params["entry_type"] = entry_type
            
            query += " ORDER BY le.transaction_date DESC LIMIT :limit"
            params["limit"] = limit
            
            with self.postgres_engine.connect() as conn:
                result = conn.execute(text(query), params)
                
                entries = []
                for row in result:
                    entries.append(dict(row))
                
                return entries
                
        except Exception as e:
            logger.error(f"Error getting ledger entries: {e}")
            raise
    
    # MongoDB Operations (Document Storage & AI Analysis)
    
    def upload_document(self, file_data: Dict[str, Any], 
                       ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Upload document to both databases"""
        try:
            # 1. Store file metadata in PostgreSQL
            postgres_doc = {
                "company_id": file_data["company_id"],
                "project_id": file_data.get("project_id"),
                "document_type": ai_analysis.get("classification", "unknown"),
                "filename": file_data["filename"],
                "file_path": file_data["file_path"],
                "file_size": file_data["file_size"],
                "mime_type": file_data["mime_type"],
                "uploader_id": file_data.get("uploader_id")
            }
            
            # Insert into PostgreSQL
            with self.postgres_engine.begin() as conn:
                result = conn.execute(text("""
                    INSERT INTO documents 
                    (company_id, project_id, document_type, filename, file_path, 
                     file_size, mime_type, uploader_id)
                    VALUES (:company_id, :project_id, :document_type, :filename,
                           :file_path, :file_size, :mime_type, :uploader_id)
                    RETURNING id
                """), postgres_doc)
                postgres_id = result.fetchone()[0]
            
            # 2. Store full document with AI analysis in MongoDB
            mongo_doc = {
                "postgres_id": postgres_id,
                "company_id": file_data["company_id"],
                "project_id": file_data.get("project_id"),
                "filename": file_data["filename"],
                "file_path": file_data["file_path"],
                "file_size": file_data["file_size"],
                "mime_type": file_data["mime_type"],
                "upload_date": datetime.now(timezone.utc),
                "uploader_id": file_data.get("uploader_id"),
                "document_type": ai_analysis.get("classification", "unknown"),
                "category": self._get_document_category(ai_analysis.get("classification", "unknown")),
                "ai_analysis": ai_analysis,
                "business_insights": self._extract_business_insights(ai_analysis),
                "tags": ai_analysis.get("tags", []),
                "keywords": ai_analysis.get("keywords", [])
            }
            
            mongo_result = self.mongo_db.documents.insert_one(mongo_doc)
            
            # 3. Update PostgreSQL with MongoDB reference
            with self.postgres_engine.begin() as conn:
                conn.execute(text("""
                    UPDATE documents 
                    SET mongo_document_id = :mongo_id 
                    WHERE id = :postgres_id
                """), {
                    "mongo_id": str(mongo_result.inserted_id),
                    "postgres_id": postgres_id
                })
            
            return {
                "postgres_id": postgres_id,
                "mongo_id": str(mongo_result.inserted_id),
                "status": "uploaded",
                "document_type": ai_analysis.get("classification", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise
    
    def get_documents(self, company_id: Optional[int] = None,
                     project_id: Optional[int] = None,
                     document_type: Optional[str] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Get documents from MongoDB with PostgreSQL metadata"""
        try:
            # Build MongoDB query
            mongo_query = {}
            if company_id:
                mongo_query["company_id"] = company_id
            if project_id:
                mongo_query["project_id"] = project_id
            if document_type:
                mongo_query["document_type"] = document_type
            
            # Get documents from MongoDB
            mongo_docs = list(self.mongo_db.documents.find(mongo_query).limit(limit))
            
            # Get corresponding PostgreSQL metadata
            postgres_ids = [doc["postgres_id"] for doc in mongo_docs if doc.get("postgres_id")]
            
            postgres_metadata = {}
            if postgres_ids:
                with self.postgres_engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT id, company_id, project_id, document_type, filename,
                               file_path, file_size, mime_type, upload_date, status
                        FROM documents 
                        WHERE id = ANY(:ids)
                    """), {"ids": postgres_ids})
                    
                    for row in result:
                        postgres_metadata[row["id"]] = dict(row)
            
            # Merge results
            documents = []
            for mongo_doc in mongo_docs:
                postgres_id = mongo_doc.get("postgres_id")
                if postgres_id and postgres_id in postgres_metadata:
                    doc = {
                        **postgres_metadata[postgres_id],
                        "mongo_id": str(mongo_doc["_id"]),
                        "ai_analysis": mongo_doc.get("ai_analysis", {}),
                        "business_insights": mongo_doc.get("business_insights", {}),
                        "tags": mongo_doc.get("tags", []),
                        "keywords": mongo_doc.get("keywords", [])
                    }
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            raise
    
    def search_documents(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search documents using MongoDB text search"""
        try:
            # Build MongoDB query
            mongo_query = {"$text": {"$search": query}}
            if filters:
                mongo_query.update(filters)
            
            # Perform text search in MongoDB
            mongo_docs = list(self.mongo_db.documents.find(mongo_query).limit(100))
            
            # Get corresponding PostgreSQL data
            postgres_ids = [doc["postgres_id"] for doc in mongo_docs if doc.get("postgres_id")]
            
            if postgres_ids:
                with self.postgres_engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT d.*, c.name as company_name, p.name as project_name
                        FROM documents d
                        JOIN companies c ON d.company_id = c.id
                        LEFT JOIN projects p ON d.project_id = p.id
                        WHERE d.id = ANY(:ids)
                    """), {"ids": postgres_ids})
                    
                    postgres_data = {row["id"]: dict(row) for row in result}
                    
                    # Merge results
                    documents = []
                    for mongo_doc in mongo_docs:
                        postgres_id = mongo_doc.get("postgres_id")
                        if postgres_id and postgres_id in postgres_data:
                            doc = {
                                **postgres_data[postgres_id],
                                "mongo_id": str(mongo_doc["_id"]),
                                "ai_analysis": mongo_doc.get("ai_analysis", {}),
                                "business_insights": mongo_doc.get("business_insights", {}),
                                "tags": mongo_doc.get("tags", []),
                                "keywords": mongo_doc.get("keywords", [])
                            }
                            documents.append(doc)
                    
                    return documents
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    # Hybrid Operations (Cross-Database)
    
    def extract_financial_data_from_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Extract financial data from document and create ledger entry"""
        try:
            # Get document from MongoDB
            mongo_doc = self.mongo_db.documents.find_one({"postgres_id": document_id})
            if not mongo_doc:
                raise ValueError(f"Document {document_id} not found")
            
            # Extract financial data from AI analysis
            ai_analysis = mongo_doc.get("ai_analysis", {})
            financial_data = ai_analysis.get("extracted_data", {})
            amounts = financial_data.get("amounts", [])
            
            if not amounts:
                logger.warning(f"No financial amounts found in document {document_id}")
                return None
            
            # Use the largest amount as the main transaction
            main_amount = max(amounts, key=lambda x: x["value"])
            
            # Create ledger entry in PostgreSQL
            ledger_entry = {
                "company_id": mongo_doc["company_id"],
                "project_id": mongo_doc.get("project_id"),
                "entry_type": self._determine_entry_type(ai_analysis.get("classification", "unknown")),
                "category": self._get_transaction_category(ai_analysis.get("classification", "unknown")),
                "description": f"Extracted from {mongo_doc['filename']}",
                "amount": main_amount["value"],
                "currency": main_amount.get("currency", "KES"),
                "reference_number": ai_analysis.get("invoice_number"),
                "transaction_date": datetime.now().date(),
                "approval_status": "pending"
            }
            
            # Create ledger entry
            created_entry = self.create_ledger_entry(ledger_entry)
            
            # Store extraction details in MongoDB
            extraction_record = {
                "document_id": document_id,
                "postgres_ledger_id": created_entry["id"],
                "amount": main_amount["value"],
                "currency": main_amount.get("currency", "KES"),
                "transaction_type": ledger_entry["entry_type"],
                "vendor_name": ai_analysis.get("vendor_name"),
                "invoice_number": ai_analysis.get("invoice_number"),
                "tax_amount": self._extract_tax_amount(amounts),
                "tax_rate": self._calculate_tax_rate(amounts),
                "confidence_score": main_amount.get("confidence", 0.0),
                "extracted_date": datetime.now(timezone.utc)
            }
            
            self.mongo_db.financial_extractions.insert_one(extraction_record)
            
            return {
                "ledger_id": created_entry["id"],
                "amount": main_amount["value"],
                "status": "extracted",
                "confidence": main_amount.get("confidence", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {e}")
            raise
    
    def get_financial_summary(self, company_id: Optional[int] = None,
                             project_id: Optional[int] = None,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get financial summary from PostgreSQL"""
        try:
            query = """
                SELECT 
                    SUM(CASE WHEN entry_type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN entry_type = 'expense' THEN amount ELSE 0 END) as total_expenses,
                    SUM(CASE WHEN entry_type = 'withdrawal' THEN amount ELSE 0 END) as total_withdrawals,
                    COUNT(*) as transaction_count
                FROM ledger_entries
                WHERE 1=1
            """
            params = {}
            
            if company_id:
                query += " AND company_id = :company_id"
                params["company_id"] = company_id
            
            if project_id:
                query += " AND project_id = :project_id"
                params["project_id"] = project_id
            
            if start_date:
                query += " AND transaction_date >= :start_date"
                params["start_date"] = start_date
            
            if end_date:
                query += " AND transaction_date <= :end_date"
                params["end_date"] = end_date
            
            with self.postgres_engine.connect() as conn:
                result = conn.execute(text(query), params)
                summary = dict(result.fetchone())
                
                # Calculate net amount
                summary["net_amount"] = (
                    summary["total_income"] - 
                    summary["total_expenses"] - 
                    summary["total_withdrawals"]
                )
                
                return summary
                
        except Exception as e:
            logger.error(f"Error getting financial summary: {e}")
            raise
    
    # Helper Methods
    
    def _get_document_category(self, doc_type: str) -> str:
        """Map document type to category"""
        categories = {
            "invoice": "financial",
            "receipt": "financial", 
            "bank_statement": "financial",
            "contract": "legal",
            "agreement": "legal",
            "tender_document": "legal",
            "nca_certificate": "compliance",
            "tax_compliance": "compliance",
            "license": "compliance",
            "proposal": "project",
            "report": "project"
        }
        return categories.get(doc_type, "general")
    
    def _extract_business_insights(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business insights from AI analysis"""
        insights = {
            "risk_score": 0.0,
            "payment_status": "unknown",
            "vendor_name": None,
            "project_code": None,
            "compliance_status": "unknown"
        }
        
        # Extract vendor from entities
        entities = ai_analysis.get("extracted_data", {}).get("entities", {})
        if entities.get("companies"):
            insights["vendor_name"] = entities["companies"][0]
        
        # Extract project code
        if entities.get("project_codes"):
            insights["project_code"] = entities["project_codes"][0]
        
        # Calculate risk score based on document type and content
        doc_type = ai_analysis.get("classification", "")
        if doc_type in ["invoice", "receipt"]:
            insights["risk_score"] = 0.1
        elif doc_type in ["contract", "agreement"]:
            insights["risk_score"] = 0.3
        elif doc_type in ["nca_certificate", "tax_compliance"]:
            insights["risk_score"] = 0.5
        
        return insights
    
    def _determine_entry_type(self, doc_type: str) -> str:
        """Determine ledger entry type from document type"""
        if doc_type in ["invoice", "receipt"]:
            return "expense"
        elif doc_type in ["payment_confirmation", "bank_credit"]:
            return "income"
        else:
            return "expense"  # Default
    
    def _get_transaction_category(self, doc_type: str) -> str:
        """Get transaction category from document type"""
        categories = {
            "invoice": "materials",
            "receipt": "expenses",
            "contract": "contracts",
            "nca_certificate": "compliance",
            "tax_compliance": "taxes"
        }
        return categories.get(doc_type, "general")
    
    def _extract_tax_amount(self, amounts: List[Dict[str, Any]]) -> Optional[float]:
        """Extract tax amount from amounts list"""
        for amount in amounts:
            if amount.get("type") == "tax":
                return amount["value"]
        return None
    
    def _calculate_tax_rate(self, amounts: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate tax rate from amounts"""
        tax_amount = self._extract_tax_amount(amounts)
        subtotal = sum(amount["value"] for amount in amounts if amount.get("type") == "subtotal")
        
        if tax_amount and subtotal:
            return (tax_amount / subtotal) * 100
        return None

# Global instance
hybrid_db = HybridDatabaseManager() 