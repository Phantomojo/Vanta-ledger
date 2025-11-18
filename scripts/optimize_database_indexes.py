#!/usr/bin/env python3
"""
Database Index Optimization Script
Creates indexes on frequently queried fields to improve performance
"""

import logging
import os
import sys

import psycopg2
from pymongo import ASCENDING, DESCENDING, MongoClient, TEXT

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vanta_ledger.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def optimize_postgresql_indexes():
    """Create indexes on PostgreSQL tables for better query performance"""
    try:
        conn = psycopg2.connect(settings.POSTGRES_URI)
        cursor = conn.cursor()

        indexes = [
            # Documents table indexes
            (
                "idx_documents_company_id",
                "CREATE INDEX IF NOT EXISTS idx_documents_company_id ON documents(company_id)",
            ),
            (
                "idx_documents_project_id",
                "CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id)",
            ),
            (
                "idx_documents_document_type",
                "CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type)",
            ),
            (
                "idx_documents_upload_date",
                "CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date DESC)",
            ),
            (
                "idx_documents_status",
                "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)",
            ),
            # Composite indexes for common query patterns
            (
                "idx_documents_company_type",
                "CREATE INDEX IF NOT EXISTS idx_documents_company_type ON documents(company_id, document_type)",
            ),
            (
                "idx_documents_company_status",
                "CREATE INDEX IF NOT EXISTS idx_documents_company_status ON documents(company_id, status)",
            ),
            # Ledger entries indexes
            (
                "idx_ledger_company_id",
                "CREATE INDEX IF NOT EXISTS idx_ledger_company_id ON ledger_entries(company_id)",
            ),
            (
                "idx_ledger_project_id",
                "CREATE INDEX IF NOT EXISTS idx_ledger_project_id ON ledger_entries(project_id)",
            ),
            (
                "idx_ledger_transaction_date",
                "CREATE INDEX IF NOT EXISTS idx_ledger_transaction_date ON ledger_entries(transaction_date DESC)",
            ),
            (
                "idx_ledger_entry_type",
                "CREATE INDEX IF NOT EXISTS idx_ledger_entry_type ON ledger_entries(entry_type)",
            ),
            (
                "idx_ledger_approval_status",
                "CREATE INDEX IF NOT EXISTS idx_ledger_approval_status ON ledger_entries(approval_status)",
            ),
            # Composite indexes for ledger
            (
                "idx_ledger_company_date",
                "CREATE INDEX IF NOT EXISTS idx_ledger_company_date ON ledger_entries(company_id, transaction_date DESC)",
            ),
            (
                "idx_ledger_company_type",
                "CREATE INDEX IF NOT EXISTS idx_ledger_company_type ON ledger_entries(company_id, entry_type)",
            ),
            # Projects table indexes
            (
                "idx_projects_company_id",
                "CREATE INDEX IF NOT EXISTS idx_projects_company_id ON projects(company_id)",
            ),
            (
                "idx_projects_status",
                "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)",
            ),
            (
                "idx_projects_start_date",
                "CREATE INDEX IF NOT EXISTS idx_projects_start_date ON projects(start_date DESC)",
            ),
            # Companies table indexes
            (
                "idx_companies_status",
                "CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status)",
            ),
            (
                "idx_companies_name",
                "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)",
            ),
        ]

        for index_name, index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(f"✅ Created index: {index_name}")
            except psycopg2.Error as e:
                logger.warning(f"⚠️  Index {index_name} may already exist: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("✅ PostgreSQL index optimization completed")

    except Exception as e:
        logger.error(f"❌ Error optimizing PostgreSQL indexes: {e}")
        raise


def optimize_mongodb_indexes():
    """Create indexes on MongoDB collections for better query performance"""
    try:
        client = MongoClient(settings.MONGO_URI)
        db = client.vanta_ledger

        # Documents collection indexes
        db.documents.create_index([("company_id", ASCENDING)])
        db.documents.create_index([("project_id", ASCENDING)])
        db.documents.create_index([("postgres_id", ASCENDING)], unique=True)
        db.documents.create_index([("upload_date", DESCENDING)])
        db.documents.create_index([("document_type", ASCENDING)])
        
        # Composite indexes for common queries
        db.documents.create_index([("company_id", ASCENDING), ("document_type", ASCENDING)])
        db.documents.create_index([("company_id", ASCENDING), ("upload_date", DESCENDING)])
        
        # Text search index for document content
        db.documents.create_index([("filename", TEXT), ("ai_analysis.summary", TEXT)])

        # AI analysis specific indexes
        db.documents.create_index([("ai_analysis.classification", ASCENDING)])
        db.documents.create_index([("tags", ASCENDING)])
        db.documents.create_index([("keywords", ASCENDING)])

        # Financial extractions indexes
        db.financial_extractions.create_index([("document_id", ASCENDING)])
        db.financial_extractions.create_index([("postgres_ledger_id", ASCENDING)])
        db.financial_extractions.create_index([("extracted_date", DESCENDING)])

        # Company context indexes (for LLM service)
        if "company_contexts" in db.list_collection_names():
            db.company_contexts.create_index([("company_id", ASCENDING)], unique=True)

        logger.info("✅ MongoDB index optimization completed")

        # Print index statistics
        for collection_name in ["documents", "financial_extractions"]:
            indexes = db[collection_name].index_information()
            logger.info(f"  {collection_name}: {len(indexes)} indexes")

        client.close()

    except Exception as e:
        logger.error(f"❌ Error optimizing MongoDB indexes: {e}")
        raise


def analyze_query_performance():
    """Analyze current query performance"""
    try:
        # MongoDB query analysis
        client = MongoClient(settings.MONGO_URI)
        db = client.vanta_ledger

        # Enable profiling for slow queries (> 100ms)
        db.set_profiling_level(1, slow_ms=100)

        logger.info("✅ Query profiling enabled for slow queries (>100ms)")
        client.close()

    except Exception as e:
        logger.warning(f"⚠️  Could not enable query profiling: {e}")


if __name__ == "__main__":
    logger.info("Starting database index optimization...")

    try:
        optimize_postgresql_indexes()
        optimize_mongodb_indexes()
        analyze_query_performance()

        logger.info("✅ All database optimizations completed successfully!")

    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
        sys.exit(1)
