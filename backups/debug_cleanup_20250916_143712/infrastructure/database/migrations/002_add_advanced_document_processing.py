#!/usr/bin/env python3
"""
Database Migration: Add Advanced Document Processing Tables
Migration script to add advanced document processing capabilities inspired by Docling + Documind
"""

import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def upgrade(engine: Engine):
    """Apply migration to add advanced document processing tables"""
    try:
        with engine.begin() as conn:
            # Create document_analyses table for storing analysis results
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS document_analyses (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL,
                    analysis_type VARCHAR(100) NOT NULL,
                    results JSONB,
                    processing_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create extracted_tables table for storing table extraction results
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS extracted_tables (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL,
                    table_id UUID,
                    table_type VARCHAR(100),
                    table_data JSONB,
                    confidence_score DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create layout_analyses table for storing layout analysis results
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS layout_analyses (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL,
                    layout_type VARCHAR(100),
                    layout_data JSONB,
                    confidence_score DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create processing_capabilities table for tracking system capabilities
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS processing_capabilities (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    capability_name VARCHAR(100) UNIQUE NOT NULL,
                    is_available BOOLEAN DEFAULT FALSE,
                    version VARCHAR(50),
                    configuration JSONB,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create indexes for performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_analyses_document_id 
                ON document_analyses(document_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_analyses_analysis_type 
                ON document_analyses(analysis_type)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_analyses_created_at 
                ON document_analyses(created_at DESC)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_extracted_tables_document_id 
                ON extracted_tables(document_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_extracted_tables_table_type 
                ON extracted_tables(table_type)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_extracted_tables_confidence_score 
                ON extracted_tables(confidence_score DESC)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_layout_analyses_document_id 
                ON layout_analyses(document_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_layout_analyses_layout_type 
                ON layout_analyses(layout_type)
            """))

            # Insert default processing capabilities
            conn.execute(text("""
                INSERT INTO processing_capabilities (capability_name, is_available, version, configuration)
                VALUES 
                ('advanced_ocr', true, '1.0.0', '{"engine": "tesseract", "languages": ["eng"]}'),
                ('layout_analysis', true, '1.0.0', '{"model": "layoutlmv3", "max_length": 512}'),
                ('handwritten_text_processing', true, '1.0.0', '{"adaptive_threshold": true}'),
                ('table_extraction', false, '1.0.0', '{"model": "layoutlmv3_table", "enabled": false}')
                ON CONFLICT (capability_name) DO NOTHING
            """))

            logger.info("✅ Advanced document processing tables and indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Error creating advanced document processing tables: {str(e)}")
        raise


def downgrade(engine: Engine):
    """Rollback migration to remove advanced document processing tables"""
    try:
        with engine.begin() as conn:
            # Remove indexes
            conn.execute(text("DROP INDEX IF EXISTS idx_layout_analyses_layout_type"))
            conn.execute(text("DROP INDEX IF EXISTS idx_layout_analyses_document_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_extracted_tables_confidence_score"))
            conn.execute(text("DROP INDEX IF EXISTS idx_extracted_tables_table_type"))
            conn.execute(text("DROP INDEX IF EXISTS idx_extracted_tables_document_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_document_analyses_created_at"))
            conn.execute(text("DROP INDEX IF EXISTS idx_document_analyses_analysis_type"))
            conn.execute(text("DROP INDEX IF EXISTS idx_document_analyses_document_id"))

            # Drop tables
            conn.execute(text("DROP TABLE IF EXISTS processing_capabilities"))
            conn.execute(text("DROP TABLE IF EXISTS layout_analyses"))
            conn.execute(text("DROP TABLE IF EXISTS extracted_tables"))
            conn.execute(text("DROP TABLE IF EXISTS document_analyses"))

            logger.info("✅ Advanced document processing tables removed successfully")

    except Exception as e:
        logger.error(f"❌ Error removing advanced document processing tables: {str(e)}")
        raise


def verify_migration(engine: Engine) -> bool:
    """Verify that the migration was applied correctly"""
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('document_analyses', 'extracted_tables', 'layout_analyses', 'processing_capabilities')
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if len(tables) != 4:
                logger.error(f"❌ Expected 4 tables, found {len(tables)}: {tables}")
                return False

            # Check if indexes exist
            result = conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename IN ('document_analyses', 'extracted_tables', 'layout_analyses')
                AND indexname LIKE 'idx_%'
            """))
            
            indexes = [row[0] for row in result.fetchall()]
            expected_indexes = [
                'idx_document_analyses_document_id',
                'idx_document_analyses_analysis_type',
                'idx_document_analyses_created_at',
                'idx_extracted_tables_document_id',
                'idx_extracted_tables_table_type',
                'idx_extracted_tables_confidence_score',
                'idx_layout_analyses_document_id',
                'idx_layout_analyses_layout_type'
            ]
            
            missing_indexes = [idx for idx in expected_indexes if idx not in indexes]
            if missing_indexes:
                logger.error(f"❌ Missing indexes: {missing_indexes}")
                return False

            # Check if processing capabilities were inserted
            result = conn.execute(text("""
                SELECT COUNT(*) FROM processing_capabilities
            """))
            
            capability_count = result.fetchone()[0]
            if capability_count < 3:
                logger.error(f"❌ Expected at least 3 processing capabilities, found {capability_count}")
                return False

            logger.info("✅ Advanced document processing migration verification passed")
            return True

    except Exception as e:
        logger.error(f"❌ Error verifying migration: {str(e)}")
        return False


if __name__ == "__main__":
    # This script can be run directly for testing
    import sys
    import os
    
    # Add the project root to the path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    from backend.src.vanta_ledger.database import get_postgres_engine
    
    engine = get_postgres_engine()
    
    print("Applying advanced document processing migration...")
    upgrade(engine)
    
    print("Verifying migration...")
    if verify_migration(engine):
        print("✅ Migration applied and verified successfully")
    else:
        print("❌ Migration verification failed")
        sys.exit(1)
