#!/usr/bin/env python3
"""
Database Migration: Add Semantic Search Tables
Migration script to add semantic search capabilities inspired by Paperless-AI
"""

import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def upgrade(engine: Engine):
    """Apply migration to add semantic search tables"""
    try:
        with engine.begin() as conn:
            # Create document_embeddings table for storing semantic embeddings
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL,
                    embedding_type VARCHAR(100) NOT NULL,
                    embedding JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create search_index table for storing search analytics
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS search_index (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    search_term TEXT NOT NULL,
                    document_id UUID NOT NULL,
                    relevance_score DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create ai_tags table for storing AI-generated tags
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ai_tags (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL,
                    tag VARCHAR(255) NOT NULL,
                    tag_type VARCHAR(100),
                    confidence_score DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create search_history table for storing search analytics
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    company_id UUID NOT NULL,
                    search_query TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create indexes for performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id 
                ON document_embeddings(document_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_embeddings_embedding_type 
                ON document_embeddings(embedding_type)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_embeddings_created_at 
                ON document_embeddings(created_at DESC)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_search_index_search_term 
                ON search_index USING gin(to_tsvector('english', search_term))
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_search_index_document_id 
                ON search_index(document_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_search_index_relevance_score 
                ON search_index(relevance_score DESC)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_tags_document_id 
                ON ai_tags(document_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_tags_tag_type 
                ON ai_tags(tag_type)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_tags_confidence_score 
                ON ai_tags(confidence_score DESC)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_search_history_user_id 
                ON search_history(user_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_search_history_company_id 
                ON search_history(company_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_search_history_search_query 
                ON search_history USING gin(to_tsvector('english', search_query))
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_search_history_created_at 
                ON search_history(created_at DESC)
            """))

            logger.info("✅ Semantic search tables and indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Error creating semantic search tables: {str(e)}")
        raise


def downgrade(engine: Engine):
    """Rollback migration to remove semantic search tables"""
    try:
        with engine.begin() as conn:
            # Remove indexes
            conn.execute(text("DROP INDEX IF EXISTS idx_search_history_created_at"))
            conn.execute(text("DROP INDEX IF EXISTS idx_search_history_search_query"))
            conn.execute(text("DROP INDEX IF EXISTS idx_search_history_company_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_search_history_user_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_ai_tags_confidence_score"))
            conn.execute(text("DROP INDEX IF EXISTS idx_ai_tags_tag_type"))
            conn.execute(text("DROP INDEX IF EXISTS idx_ai_tags_document_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_search_index_relevance_score"))
            conn.execute(text("DROP INDEX IF EXISTS idx_search_index_document_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_search_index_search_term"))
            conn.execute(text("DROP INDEX IF EXISTS idx_document_embeddings_created_at"))
            conn.execute(text("DROP INDEX IF EXISTS idx_document_embeddings_embedding_type"))
            conn.execute(text("DROP INDEX IF EXISTS idx_document_embeddings_document_id"))

            # Drop tables
            conn.execute(text("DROP TABLE IF EXISTS search_history"))
            conn.execute(text("DROP TABLE IF EXISTS ai_tags"))
            conn.execute(text("DROP TABLE IF EXISTS search_index"))
            conn.execute(text("DROP TABLE IF EXISTS document_embeddings"))

            logger.info("✅ Semantic search tables removed successfully")

    except Exception as e:
        logger.error(f"❌ Error removing semantic search tables: {str(e)}")
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
                AND table_name IN ('document_embeddings', 'search_index', 'ai_tags', 'search_history')
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if len(tables) != 4:
                logger.error(f"❌ Expected 4 tables, found {len(tables)}: {tables}")
                return False

            # Check if indexes exist
            result = conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename IN ('document_embeddings', 'search_index', 'ai_tags', 'search_history')
                AND indexname LIKE 'idx_%'
            """))
            
            indexes = [row[0] for row in result.fetchall()]
            expected_indexes = [
                'idx_document_embeddings_document_id',
                'idx_document_embeddings_embedding_type',
                'idx_document_embeddings_created_at',
                'idx_search_index_document_id',
                'idx_search_index_relevance_score',
                'idx_ai_tags_document_id',
                'idx_ai_tags_tag_type',
                'idx_ai_tags_confidence_score',
                'idx_search_history_user_id',
                'idx_search_history_company_id',
                'idx_search_history_created_at'
            ]
            
            missing_indexes = [idx for idx in expected_indexes if idx not in indexes]
            if missing_indexes:
                logger.error(f"❌ Missing indexes: {missing_indexes}")
                return False

            logger.info("✅ Semantic search migration verification passed")
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
    
    print("Applying semantic search migration...")
    upgrade(engine)
    
    print("Verifying migration...")
    if verify_migration(engine):
        print("✅ Migration applied and verified successfully")
    else:
        print("❌ Migration verification failed")
        sys.exit(1)
