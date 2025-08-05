#!/usr/bin/env python3
"""
Migrate Processed Documents to Secure Hybrid Database
====================================================

This script migrates the processed documents from the data/processed_documents directory
to our secure hybrid database system (PostgreSQL + MongoDB).

Author: Vanta Ledger Team
"""

import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Database imports
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
POSTGRES_URI = "postgresql://vanta_user:kQ5afx/QwEInsGMsQH8ka7+ZPnPThFDe75wZjNHvZuQ=@localhost:5432/vanta_ledger"
MONGO_URI = "mongodb://admin:THq2ibwBwnNCHUqbKFlSHrkmo3eSpzPGPX4AZg2V7yU=@localhost:27017/vanta_ledger?authSource=admin"

# Paths
PROCESSED_DOCUMENTS_DIR = "../data/processed_documents"
UPLOADS_DIR = "../data/uploads"

class DocumentMigrator:
    """Migrates processed documents to the hybrid database"""
    
    def __init__(self):
        self.postgres_engine = None
        self.mongo_client = None
        self.mongo_db = None
        
    def connect_databases(self):
        """Connect to both databases"""
        try:
            # Connect to PostgreSQL
            self.postgres_engine = create_engine(POSTGRES_URI)
            logger.info("✅ Connected to PostgreSQL")
            
            # Connect to MongoDB
            self.mongo_client = MongoClient(MONGO_URI)
            self.mongo_db = self.mongo_client.vanta_ledger
            logger.info("✅ Connected to MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def load_processing_report(self) -> Dict[str, Any]:
        """Load the processing report to understand the data structure"""
        try:
            report_path = os.path.join(PROCESSED_DOCUMENTS_DIR, "processing_report.json")
            with open(report_path, 'r') as f:
                report = json.load(f)
            logger.info(f"✅ Loaded processing report: {report['processing_summary']['total_files_processed']} files")
            return report
        except Exception as e:
            logger.error(f"❌ Failed to load processing report: {e}")
            raise
    
    def load_document_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load analysis and entities data for a document"""
        try:
            base_name = filename.replace('.txt', '')
            
            # Load analysis data
            analysis_path = os.path.join(PROCESSED_DOCUMENTS_DIR, f"{base_name}_analysis.json")
            entities_path = os.path.join(PROCESSED_DOCUMENTS_DIR, f"{base_name}_entities.json")
            ledger_path = os.path.join(PROCESSED_DOCUMENTS_DIR, f"{base_name}_ledger.json")
            
            document_data = {
                "filename": filename,
                "base_name": base_name,
                "analysis": None,
                "entities": None,
                "ledger": None
            }
            
            # Load analysis
            if os.path.exists(analysis_path):
                with open(analysis_path, 'r') as f:
                    document_data["analysis"] = json.load(f)
            
            # Load entities
            if os.path.exists(entities_path):
                with open(entities_path, 'r') as f:
                    document_data["entities"] = json.load(f)
            
            # Load ledger (if exists)
            if os.path.exists(ledger_path):
                with open(ledger_path, 'r') as f:
                    document_data["ledger"] = json.load(f)
            
            return document_data
            
        except Exception as e:
            logger.error(f"❌ Failed to load document data for {filename}: {e}")
            return None
    
    def migrate_document_to_postgresql(self, document_data: Dict[str, Any], company_id: int = 1):
        """Migrate document metadata to PostgreSQL"""
        try:
            with self.postgres_engine.begin() as conn:
                # Insert document metadata
                result = conn.execute(text("""
                    INSERT INTO documents 
                    (company_id, document_type, filename, file_path, file_size, mime_type, upload_date, status)
                    VALUES (:company_id, :document_type, :filename, :file_path, :file_size, :mime_type, :upload_date, 'active')
                    RETURNING id
                """), {
                    "company_id": company_id,
                    "document_type": "financial_document",
                    "filename": document_data["filename"],
                    "file_path": f"processed_documents/{document_data['filename']}",
                    "file_size": 0,  # Will be updated if file exists
                    "mime_type": "text/plain",
                    "upload_date": datetime.now(timezone.utc)
                })
                
                document_id = result.fetchone()[0]
                logger.info(f"✅ Migrated document {document_data['filename']} to PostgreSQL (ID: {document_id})")
                return document_id
                
        except Exception as e:
            logger.error(f"❌ Failed to migrate document {document_data['filename']} to PostgreSQL: {e}")
            return None
    
    def migrate_document_to_mongodb(self, document_data: Dict[str, Any], postgres_id: int):
        """Migrate document data to MongoDB"""
        try:
            mongo_document = {
                "postgres_id": postgres_id,
                "filename": document_data["filename"],
                "base_name": document_data["base_name"],
                "analysis": document_data["analysis"],
                "entities": document_data["entities"],
                "ledger": document_data["ledger"],
                "metadata": {
                    "upload_date": datetime.now(timezone.utc),
                    "processing_date": datetime.now(timezone.utc),
                    "status": "active"
                }
            }
            
            # Insert into MongoDB
            result = self.mongo_db.documents.insert_one(mongo_document)
            logger.info(f"✅ Migrated document {document_data['filename']} to MongoDB (ID: {result.inserted_id})")
            
            # Update PostgreSQL with MongoDB ID
            with self.postgres_engine.begin() as conn:
                conn.execute(text("""
                    UPDATE documents 
                    SET mongo_document_id = :mongo_id 
                    WHERE id = :postgres_id
                """), {
                    "mongo_id": str(result.inserted_id),
                    "postgres_id": postgres_id
                })
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate document {document_data['filename']} to MongoDB: {e}")
            return None
    
    def migrate_ledger_entries(self, document_data: Dict[str, Any], document_id: int, company_id: int = 1):
        """Migrate ledger entries to PostgreSQL"""
        if not document_data.get("ledger"):
            return
        
        try:
            ledger_data = document_data["ledger"]
            
            with self.postgres_engine.begin() as conn:
                for entry in ledger_data.get("entries", []):
                    conn.execute(text("""
                        INSERT INTO ledger_entries 
                        (company_id, document_id, entry_type, category, description, amount, currency, reference_number, transaction_date, approval_status)
                        VALUES (:company_id, :document_id, :entry_type, :category, :description, :amount, :currency, :reference_number, :transaction_date, 'pending')
                    """), {
                        "company_id": company_id,
                        "document_id": document_id,
                        "entry_type": entry.get("type", "expense"),
                        "category": entry.get("category", "general"),
                        "description": entry.get("description", ""),
                        "amount": entry.get("amount", 0.0),
                        "currency": entry.get("currency", "KES"),
                        "reference_number": entry.get("reference", ""),
                        "transaction_date": datetime.now(timezone.utc).date()
                    })
            
            logger.info(f"✅ Migrated ledger entries for document {document_data['filename']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate ledger entries for {document_data['filename']}: {e}")
    
    def migrate_documents(self, limit: int = None):
        """Migrate all processed documents"""
        try:
            # Load processing report
            report = self.load_processing_report()
            files_to_process = report["files_processed"]
            
            if limit:
                files_to_process = files_to_process[:limit]
            
            logger.info(f"🚀 Starting migration of {len(files_to_process)} documents...")
            
            migrated_count = 0
            failed_count = 0
            
            for filename in files_to_process:
                try:
                    # Load document data
                    document_data = self.load_document_data(filename)
                    if not document_data:
                        failed_count += 1
                        continue
                    
                    # Migrate to PostgreSQL
                    postgres_id = self.migrate_document_to_postgresql(document_data)
                    if not postgres_id:
                        failed_count += 1
                        continue
                    
                    # Migrate to MongoDB
                    mongo_id = self.migrate_document_to_mongodb(document_data, postgres_id)
                    if not mongo_id:
                        failed_count += 1
                        continue
                    
                    # Migrate ledger entries
                    self.migrate_ledger_entries(document_data, postgres_id)
                    
                    migrated_count += 1
                    
                    if migrated_count % 100 == 0:
                        logger.info(f"📊 Progress: {migrated_count}/{len(files_to_process)} documents migrated")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to migrate {filename}: {e}")
                    failed_count += 1
            
            logger.info(f"✅ Migration completed!")
            logger.info(f"   📊 Successfully migrated: {migrated_count} documents")
            logger.info(f"   ❌ Failed migrations: {failed_count} documents")
            
            return migrated_count, failed_count
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
    
    def create_migration_summary(self, migrated_count: int, failed_count: int):
        """Create a migration summary report"""
        summary = {
            "migration_date": datetime.now(timezone.utc).isoformat(),
            "migrated_documents": migrated_count,
            "failed_migrations": failed_count,
            "total_processed": migrated_count + failed_count,
            "success_rate": f"{(migrated_count / (migrated_count + failed_count) * 100):.2f}%" if (migrated_count + failed_count) > 0 else "0%",
            "database_info": {
                "postgresql": "vanta_ledger",
                "mongodb": "vanta_ledger",
                "redis": "vanta_ledger"
            }
        }
        
        # Save summary
        summary_path = os.path.join(PROCESSED_DOCUMENTS_DIR, "migration_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"📋 Migration summary saved to: {summary_path}")
        return summary

def main():
    """Main migration function"""
    try:
        migrator = DocumentMigrator()
        
        # Connect to databases
        migrator.connect_databases()
        
        # Start migration (migrate ALL documents)
        migrated_count, failed_count = migrator.migrate_documents()
        
        # Create summary
        summary = migrator.create_migration_summary(migrated_count, failed_count)
        
        print("\n🎉 Document Migration Complete!")
        print("=" * 50)
        print(f"✅ Successfully migrated: {migrated_count} documents")
        print(f"❌ Failed migrations: {failed_count} documents")
        print(f"📊 Success rate: {summary['success_rate']}")
        print("\n📊 Database Status:")
        print("   PostgreSQL: Documents metadata and ledger entries")
        print("   MongoDB: Document analysis and entities data")
        print("   Redis: Caching and session management")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    main() 