#!/usr/bin/env python3
"""
Database Migration: Add Atomic Transaction Tables
Migration script to add atomic transaction support inspired by Formance Ledger
"""

import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def upgrade(engine: Engine):
    """Apply migration to add atomic transaction tables"""
    try:
        with engine.begin() as conn:
            # Create atomic_transactions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS atomic_transactions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    company_id INTEGER REFERENCES companies(id),
                    transaction_group_id UUID,
                    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'rolled_back', 'failed')),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    rolled_back_at TIMESTAMP,
                    rollback_data JSONB
                )
            """))

            # Create transaction_groups table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS transaction_groups (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255),
                    description TEXT,
                    company_id INTEGER REFERENCES companies(id),
                    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """))

            # Add atomic_transaction_id column to journal_entries table
            conn.execute(text("""
                ALTER TABLE journal_entries 
                ADD COLUMN IF NOT EXISTS atomic_transaction_id UUID
            """))

            # Add company_id column to journal_entries table if not exists
            conn.execute(text("""
                ALTER TABLE journal_entries 
                ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)
            """))

            # Create indexes for performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_atomic_transactions_group_id 
                ON atomic_transactions(transaction_group_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_atomic_transactions_status 
                ON atomic_transactions(status)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_atomic_transactions_company_id 
                ON atomic_transactions(company_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_atomic_transactions_created_at 
                ON atomic_transactions(created_at DESC)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_transaction_groups_company_id 
                ON transaction_groups(company_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_transaction_groups_status 
                ON transaction_groups(status)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_journal_entries_atomic_transaction_id 
                ON journal_entries(atomic_transaction_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_journal_entries_company_id 
                ON journal_entries(company_id)
            """))

            # Create MongoDB collections for atomic transactions
            # Note: MongoDB collections are created automatically when first document is inserted
            # This is handled in the AtomicTransactionService

            logger.info("✅ Atomic transaction tables and indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Error creating atomic transaction tables: {str(e)}")
        raise


def downgrade(engine: Engine):
    """Rollback migration to remove atomic transaction tables"""
    try:
        with engine.begin() as conn:
            # Remove indexes
            conn.execute(text("DROP INDEX IF EXISTS idx_journal_entries_company_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_journal_entries_atomic_transaction_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_transaction_groups_status"))
            conn.execute(text("DROP INDEX IF EXISTS idx_transaction_groups_company_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_atomic_transactions_created_at"))
            conn.execute(text("DROP INDEX IF EXISTS idx_atomic_transactions_company_id"))
            conn.execute(text("DROP INDEX IF EXISTS idx_atomic_transactions_status"))
            conn.execute(text("DROP INDEX IF EXISTS idx_atomic_transactions_group_id"))

            # Remove columns from journal_entries
            conn.execute(text("ALTER TABLE journal_entries DROP COLUMN IF EXISTS company_id"))
            conn.execute(text("ALTER TABLE journal_entries DROP COLUMN IF EXISTS atomic_transaction_id"))

            # Drop tables
            conn.execute(text("DROP TABLE IF EXISTS transaction_groups"))
            conn.execute(text("DROP TABLE IF EXISTS atomic_transactions"))

            logger.info("✅ Atomic transaction tables removed successfully")

    except Exception as e:
        logger.error(f"❌ Error removing atomic transaction tables: {str(e)}")
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
                AND table_name IN ('atomic_transactions', 'transaction_groups')
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if len(tables) != 2:
                logger.error(f"❌ Expected 2 tables, found {len(tables)}: {tables}")
                return False

            # Check if columns exist in journal_entries
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'journal_entries' 
                AND column_name IN ('atomic_transaction_id', 'company_id')
            """))
            
            columns = [row[0] for row in result.fetchall()]
            
            if len(columns) != 2:
                logger.error(f"❌ Expected 2 columns in journal_entries, found {len(columns)}: {columns}")
                return False

            # Check if indexes exist
            result = conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename IN ('atomic_transactions', 'transaction_groups', 'journal_entries')
                AND indexname LIKE 'idx_%'
            """))
            
            indexes = [row[0] for row in result.fetchall()]
            expected_indexes = [
                'idx_atomic_transactions_group_id',
                'idx_atomic_transactions_status',
                'idx_atomic_transactions_company_id',
                'idx_atomic_transactions_created_at',
                'idx_transaction_groups_company_id',
                'idx_transaction_groups_status',
                'idx_journal_entries_atomic_transaction_id',
                'idx_journal_entries_company_id'
            ]
            
            missing_indexes = [idx for idx in expected_indexes if idx not in indexes]
            if missing_indexes:
                logger.error(f"❌ Missing indexes: {missing_indexes}")
                return False

            logger.info("✅ Atomic transaction migration verification passed")
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
    
    print("Applying atomic transaction migration...")
    upgrade(engine)
    
    print("Verifying migration...")
    if verify_migration(engine):
        print("✅ Migration applied and verified successfully")
    else:
        print("❌ Migration verification failed")
        sys.exit(1)
