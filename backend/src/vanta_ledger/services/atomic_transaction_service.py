import os
#!/usr/bin/env python3
"""
Atomic Transaction Service for Vanta Ledger
Inspired by Formance Ledger - Enables atomic multi-posting transactions
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import redis
from pymongo.collection import Collection
from pymongo.database import Database
from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..database import get_mongo_client, get_postgres_engine
from ..config import settings
from ..models.financial_models import (
    AccountType,
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
)
from ..utils.validation import input_validator

logger = logging.getLogger(__name__)


class AtomicTransactionService:
    """Atomic multi-posting transaction service inspired by Formance Ledger"""

    def __init__(self):
        # Database connections
        self.mongo_client = get_mongo_client()
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        self.postgres_engine: Engine = get_postgres_engine()
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URI, decode_responses=True
        )

        # Collections
        self.atomic_transactions: Collection = self.db.atomic_transactions
        self.transaction_groups: Collection = self.db.transaction_groups
        self.journal_entries: Collection = self.db.journal_entries
        self.journal_entry_lines: Collection = self.db.journal_entry_lines

        # Create indexes
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Atomic transaction indexes
            self.atomic_transactions.create_index([("transaction_group_id", 1)])
            self.atomic_transactions.create_index([("status", 1)])
            self.atomic_transactions.create_index([("company_id", 1)])
            self.atomic_transactions.create_index([("created_at", -1)])

            # Transaction group indexes
            self.transaction_groups.create_index([("company_id", 1)])
            self.transaction_groups.create_index([("status", 1)])

            logger.info("Atomic transaction database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating atomic transaction indexes: {str(e)}")

    async def create_atomic_transaction(
        self,
        transactions: List[Dict],
        company_id: UUID,
        metadata: Dict = None,
        group_name: str = None,
        description: str = None,
    ) -> Dict:
        """
        Create atomic transaction across multiple accounts/companies
        
        Args:
            transactions: List of transaction dictionaries
            company_id: Company ID for the transaction
            metadata: Additional metadata for the transaction
            group_name: Optional group name for transaction grouping
            description: Optional description for the transaction group
            
        Returns:
            Dictionary containing transaction group and transaction details
        """
        atomic_transaction_id = None
        try:
            # Validate input
            if not transactions:
                raise ValueError("At least one transaction is required")

            # Create transaction group
            group_id = uuid4()
            group_data = {
                "id": str(group_id),
                "name": group_name or f"Atomic Transaction Group {datetime.now().isoformat()}",
                "description": description,
                "company_id": str(company_id),
                "status": "pending",
                "created_at": datetime.utcnow(),
                "metadata": metadata or {},
            }

            # Create atomic transaction record
            atomic_transaction_id = uuid4()
            atomic_data = {
                "id": str(atomic_transaction_id),
                "company_id": str(company_id),
                "transaction_group_id": str(group_id),
                "status": "pending",
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "rollback_data": {},
            }

            # Validate and prepare transactions
            validated_transactions = []
            total_debit = Decimal("0")
            total_credit = Decimal("0")

            for i, transaction in enumerate(transactions):
                # Validate transaction structure
                validated_tx = self._validate_transaction(transaction, i)
                validated_transactions.append(validated_tx)

                # Calculate totals
                total_debit += Decimal(str(validated_tx.get("debit_amount", "0")))
                total_credit += Decimal(str(validated_tx.get("credit_amount", "0")))

            # Verify double-entry balance
            if total_debit != total_credit:
                raise ValueError(
                    f"Transaction not balanced: Debit={total_debit}, Credit={total_credit}"
                )

            # Store rollback data
            atomic_data["rollback_data"] = {
                "transactions": validated_transactions,
                "total_debit": str(total_debit),
                "total_credit": str(total_credit),
            }

            # Execute atomic transaction
            success = await self._execute_atomic_transaction(
                atomic_data, validated_transactions, company_id
            )

            if success:
                # Update status to completed
                atomic_data["status"] = "completed"
                atomic_data["completed_at"] = datetime.utcnow()
                group_data["status"] = "completed"

                # Save to database
                self.atomic_transactions.insert_one(atomic_data)
                self.transaction_groups.insert_one(group_data)

                logger.info(
                    f"Atomic transaction completed successfully: {atomic_transaction_id}"
                )

                return {
                    "success": True,
                    "atomic_transaction_id": str(atomic_transaction_id),
                    "transaction_group_id": str(group_id),
                    "status": "completed",
                    "total_debit": str(total_debit),
                    "total_credit": str(total_credit),
                    "transaction_count": len(validated_transactions),
                }
            else:
                raise Exception("Failed to execute atomic transaction")

        except Exception as e:
            logger.error(f"Error creating atomic transaction: {str(e)}")
            # Attempt rollback if partial execution occurred
            if atomic_transaction_id:
                await self._rollback_partial_execution(atomic_transaction_id)
            raise

    async def _execute_atomic_transaction(
        self, atomic_data: Dict, transactions: List[Dict], company_id: UUID
    ) -> bool:
        """Execute the atomic transaction with database transaction"""
        try:
            # Use PostgreSQL transaction for ACID compliance
            with self.postgres_engine.begin() as conn:
                # Create journal entries for each transaction
                journal_entries = []
                
                for transaction in transactions:
                    # Create journal entry
                    entry_data = {
                        "entry_number": f"AT-{atomic_data['id'][:8]}-{len(journal_entries) + 1}",
                        "entry_date": datetime.utcnow(),
                        "reference": f"Atomic Transaction {atomic_data['id']}",
                        "description": transaction.get("description", "Atomic transaction entry"),
                        "total_debit": transaction.get("debit_amount", "0"),
                        "total_credit": transaction.get("credit_amount", "0"),
                        "currency": transaction.get("currency", "KES"),
                        "exchange_rate": "1.00",
                        "created_by": atomic_data.get("created_by"),
                        "company_id": str(company_id),
                        "atomic_transaction_id": atomic_data["id"],
                    }

                    # Insert journal entry
                    result = conn.execute(
                        text("""
                            INSERT INTO journal_entries 
                            (entry_number, entry_date, reference, description, total_debit, 
                             total_credit, currency, exchange_rate, created_by, company_id, 
                             atomic_transaction_id, is_posted)
                            VALUES (:entry_number, :entry_date, :reference, :description, 
                                   :total_debit, :total_credit, :currency, :exchange_rate, 
                                   :created_by, :company_id, :atomic_transaction_id, true)
                            RETURNING id
                        """),
                        entry_data
                    )
                    
                    entry_id = result.fetchone()[0]
                    journal_entries.append(entry_id)

                    # Create journal entry lines
                    for line in transaction.get("lines", []):
                        line_data = {
                            "journal_entry_id": entry_id,
                            "account_id": line["account_id"],
                            "description": line.get("description", ""),
                            "debit_amount": line.get("debit_amount", "0"),
                            "credit_amount": line.get("credit_amount", "0"),
                            "line_number": line.get("line_number", 1),
                        }
                        
                        conn.execute(
                            text("""
                                INSERT INTO journal_entry_lines 
                                (journal_entry_id, account_id, description, debit_amount, 
                                 credit_amount, line_number)
                                VALUES (:journal_entry_id, :account_id, :description, 
                                       :debit_amount, :credit_amount, :line_number)
                            """),
                            line_data
                        )

                logger.info(f"Atomic transaction executed successfully with {len(journal_entries)} journal entries")
                return True

        except Exception as e:
            logger.error(f"Error executing atomic transaction: {str(e)}")
            return False

    def _validate_transaction(self, transaction: Dict, index: int) -> Dict:
        """Validate and normalize transaction data"""
        try:
            # Required fields
            required_fields = ["description"]
            for field in required_fields:
                if field not in transaction:
                    raise ValueError(f"Missing required field '{field}' in transaction {index}")

            # Validate lines if present
            if "lines" in transaction:
                if not isinstance(transaction["lines"], list):
                    raise ValueError(f"Lines must be a list in transaction {index}")
                
                for i, line in enumerate(transaction["lines"]):
                    if "account_id" not in line:
                        raise ValueError(f"Missing account_id in line {i} of transaction {index}")
                    
                    # Ensure either debit or credit amount is present
                    debit = Decimal(str(line.get("debit_amount", "0")))
                    credit = Decimal(str(line.get("credit_amount", "0")))
                    
                    if debit == 0 and credit == 0:
                        raise ValueError(f"Line {i} in transaction {index} must have either debit or credit amount")
                    
                    if debit > 0 and credit > 0:
                        raise ValueError(f"Line {i} in transaction {index} cannot have both debit and credit amounts")

            # Normalize transaction
            validated = {
                "description": transaction["description"],
                "debit_amount": str(transaction.get("debit_amount", "0")),
                "credit_amount": str(transaction.get("credit_amount", "0")),
                "currency": transaction.get("currency", "KES"),
                "lines": transaction.get("lines", []),
                "metadata": transaction.get("metadata", {}),
            }

            return validated

        except Exception as e:
            logger.error(f"Error validating transaction {index}: {str(e)}")
            raise

    async def rollback_transaction(self, transaction_id: UUID) -> bool:
        """Rollback atomic transaction"""
        try:
            # Find atomic transaction
            atomic_tx = self.atomic_transactions.find_one({"id": str(transaction_id)})
            if not atomic_tx:
                raise ValueError(f"Atomic transaction {transaction_id} not found")

            if atomic_tx["status"] != "completed":
                raise ValueError(f"Atomic transaction {transaction_id} is not completed")

            # Execute rollback
            success = await self._execute_rollback(atomic_tx)
            
            if success:
                # Update status
                self.atomic_transactions.update_one(
                    {"id": str(transaction_id)},
                    {
                        "$set": {
                            "status": "rolled_back",
                            "rolled_back_at": datetime.utcnow(),
                        }
                    }
                )
                
                logger.info(f"Atomic transaction {transaction_id} rolled back successfully")
                return True
            else:
                raise Exception("Failed to execute rollback")

        except Exception as e:
            logger.error(f"Error rolling back transaction {transaction_id}: {str(e)}")
            return False

    async def _execute_rollback(self, atomic_tx: Dict) -> bool:
        """Execute rollback of atomic transaction"""
        try:
            with self.postgres_engine.begin() as conn:
                # Find and reverse journal entries
                result = conn.execute(
                    text("""
                        SELECT id, entry_number FROM journal_entries 
                        WHERE atomic_transaction_id = :atomic_transaction_id
                    """),
                    {"atomic_transaction_id": atomic_tx["id"]}
                )
                
                journal_entries = result.fetchall()
                
                for entry in journal_entries:
                    # Create reversal entry
                    reversal_data = {
                        "entry_number": f"REV-{entry.entry_number}",
                        "entry_date": datetime.utcnow(),
                        "reference": f"Reversal of {entry.entry_number}",
                        "description": f"Rollback of atomic transaction {atomic_tx['id']}",
                        "total_debit": "0",  # Will be calculated from lines
                        "total_credit": "0",  # Will be calculated from lines
                        "currency": "KES",
                        "exchange_rate": "1.00",
                        "created_by": atomic_tx.get("created_by"),
                        "company_id": atomic_tx["company_id"],
                        "is_posted": True,
                    }
                    
                    # Insert reversal entry
                    reversal_result = conn.execute(
                        text("""
                            INSERT INTO journal_entries 
                            (entry_number, entry_date, reference, description, total_debit, 
                             total_credit, currency, exchange_rate, created_by, company_id, is_posted)
                            VALUES (:entry_number, :entry_date, :reference, :description, 
                                   :total_debit, :total_credit, :currency, :exchange_rate, 
                                   :created_by, :company_id, :is_posted)
                            RETURNING id
                        """),
                        reversal_data
                    )
                    
                    reversal_entry_id = reversal_result.fetchone()[0]
                    
                    # Create reversal lines (swap debit/credit)
                    lines_result = conn.execute(
                        text("""
                            SELECT account_id, description, debit_amount, credit_amount, line_number
                            FROM journal_entry_lines 
                            WHERE journal_entry_id = :journal_entry_id
                        """),
                        {"journal_entry_id": entry.id}
                    )
                    
                    lines = lines_result.fetchall()
                    total_debit = Decimal("0")
                    total_credit = Decimal("0")
                    
                    for line in lines:
                        # Swap debit and credit
                        reversal_line_data = {
                            "journal_entry_id": reversal_entry_id,
                            "account_id": line.account_id,
                            "description": line.description,
                            "debit_amount": str(line.credit_amount),  # Swap
                            "credit_amount": str(line.debit_amount),  # Swap
                            "line_number": line.line_number,
                        }
                        
                        conn.execute(
                            text("""
                                INSERT INTO journal_entry_lines 
                                (journal_entry_id, account_id, description, debit_amount, 
                                 credit_amount, line_number)
                                VALUES (:journal_entry_id, :account_id, :description, 
                                       :debit_amount, :credit_amount, :line_number)
                            """),
                            reversal_line_data
                        )
                        
                        total_debit += Decimal(str(line.credit_amount))
                        total_credit += Decimal(str(line.debit_amount))
                    
                    # Update reversal entry totals
                    conn.execute(
                        text("""
                            UPDATE journal_entries 
                            SET total_debit = :total_debit, total_credit = :total_credit
                            WHERE id = :entry_id
                        """),
                        {
                            "total_debit": str(total_debit),
                            "total_credit": str(total_credit),
                            "entry_id": reversal_entry_id,
                        }
                    )

                logger.info(f"Rollback executed successfully for {len(journal_entries)} journal entries")
                return True

        except Exception as e:
            logger.error(f"Error executing rollback: {str(e)}")
            return False

    async def get_transaction_status(self, transaction_id: UUID) -> Dict:
        """Get transaction status and details"""
        try:
            atomic_tx = self.atomic_transactions.find_one({"id": str(transaction_id)})
            if not atomic_tx:
                raise ValueError(f"Atomic transaction {transaction_id} not found")

            # Get related journal entries
            with self.postgres_engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT id, entry_number, description, total_debit, total_credit, 
                               created_at, is_posted
                        FROM journal_entries 
                        WHERE atomic_transaction_id = :atomic_transaction_id
                        ORDER BY created_at
                    """),
                    {"atomic_transaction_id": str(transaction_id)}
                )
                
                journal_entries = [dict(row) for row in result.fetchall()]

            return {
                "atomic_transaction_id": atomic_tx["id"],
                "status": atomic_tx["status"],
                "company_id": atomic_tx["company_id"],
                "transaction_group_id": atomic_tx["transaction_group_id"],
                "created_at": atomic_tx["created_at"].isoformat(),
                "completed_at": atomic_tx.get("completed_at", ""),
                "rolled_back_at": atomic_tx.get("rolled_back_at", ""),
                "metadata": atomic_tx.get("metadata", {}),
                "journal_entries": journal_entries,
                "journal_entry_count": len(journal_entries),
            }

        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            raise

    async def _rollback_partial_execution(self, transaction_id: UUID):
        """Rollback partial execution if transaction failed"""
        try:
            # This would implement cleanup for partially executed transactions
            logger.warning(f"Attempting rollback of partial execution for {transaction_id}")
            # Implementation would depend on what was partially executed
        except Exception as e:
            logger.error(f"Error in partial rollback: {str(e)}")

    async def list_transaction_groups(
        self, company_id: UUID, status: str = None, limit: int = 50
    ) -> List[Dict]:
        """List transaction groups for a company"""
        try:
            query = {"company_id": str(company_id)}
            if status:
                query["status"] = status

            cursor = self.transaction_groups.find(query).sort("created_at", -1).limit(limit)
            groups = list(cursor)

            return groups

        except Exception as e:
            logger.error(f"Error listing transaction groups: {str(e)}")
            raise


# Global instance
atomic_transaction_service = AtomicTransactionService()
