#!/usr/bin/env python3
"""
Test Atomic Transactions
Comprehensive tests for atomic transaction functionality inspired by Formance Ledger
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from decimal import Decimal
from typing import Dict, List
from uuid import UUID, uuid4

# Add the project root to the path
sys.path.append('.')

from backend.src.vanta_ledger.services.atomic_transaction_service import AtomicTransactionService
from backend.src.vanta_ledger.database import get_postgres_engine, get_mongo_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AtomicTransactionTester:
    """Test suite for atomic transactions"""

    def __init__(self):
        self.service = AtomicTransactionService()
        self.test_company_id = UUID('12345678-1234-5678-9abc-123456789abc')
        self.test_user_id = UUID('87654321-4321-8765-cba9-987654321cba')

    async def test_basic_atomic_transaction(self):
        """Test basic atomic transaction creation"""
        logger.info("🧪 Testing basic atomic transaction...")
        
        # Create a simple balanced transaction
        transactions = [
            {
                "description": "Test transaction 1",
                "lines": [
                    {
                        "account_id": str(uuid4()),
                        "description": "Cash payment",
                        "debit_amount": "1000.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": str(uuid4()),
                        "description": "Revenue",
                        "debit_amount": "0.00",
                        "credit_amount": "1000.00",
                    }
                ]
            }
        ]

        try:
            result = await self.service.create_atomic_transaction(
                transactions=transactions,
                company_id=self.test_company_id,
                group_name="Test Group 1",
                description="Basic atomic transaction test"
            )

            assert result["success"] is True
            assert result["status"] == "completed"
            assert result["total_debit"] == "1000.00"
            assert result["total_credit"] == "1000.00"
            assert result["transaction_count"] == 1

            logger.info("✅ Basic atomic transaction test passed")
            return result["atomic_transaction_id"]

        except Exception as e:
            logger.error(f"❌ Basic atomic transaction test failed: {str(e)}")
            raise

    async def test_multi_transaction_atomic(self):
        """Test atomic transaction with multiple sub-transactions"""
        logger.info("🧪 Testing multi-transaction atomic...")
        
        # Create multiple transactions that must all succeed
        transactions = [
            {
                "description": "Cash receipt",
                "lines": [
                    {
                        "account_id": str(uuid4()),
                        "description": "Cash",
                        "debit_amount": "500.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": str(uuid4()),
                        "description": "Accounts Receivable",
                        "debit_amount": "0.00",
                        "credit_amount": "500.00",
                    }
                ]
            },
            {
                "description": "Expense payment",
                "lines": [
                    {
                        "account_id": str(uuid4()),
                        "description": "Office Supplies",
                        "debit_amount": "200.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": str(uuid4()),
                        "description": "Cash",
                        "debit_amount": "0.00",
                        "credit_amount": "200.00",
                    }
                ]
            }
        ]

        try:
            result = await self.service.create_atomic_transaction(
                transactions=transactions,
                company_id=self.test_company_id,
                group_name="Multi Transaction Test",
                description="Multiple transactions in one atomic operation"
            )

            assert result["success"] is True
            assert result["status"] == "completed"
            assert result["transaction_count"] == 2

            logger.info("✅ Multi-transaction atomic test passed")
            return result["atomic_transaction_id"]

        except Exception as e:
            logger.error(f"❌ Multi-transaction atomic test failed: {str(e)}")
            raise

    async def test_unbalanced_transaction_failure(self):
        """Test that unbalanced transactions are rejected"""
        logger.info("🧪 Testing unbalanced transaction rejection...")
        
        # Create an unbalanced transaction
        transactions = [
            {
                "description": "Unbalanced transaction",
                "lines": [
                    {
                        "account_id": str(uuid4()),
                        "description": "Cash",
                        "debit_amount": "1000.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": str(uuid4()),
                        "description": "Revenue",
                        "debit_amount": "0.00",
                        "credit_amount": "900.00",  # Not balanced!
                    }
                ]
            }
        ]

        try:
            await self.service.create_atomic_transaction(
                transactions=transactions,
                company_id=self.test_company_id
            )
            
            logger.error("❌ Unbalanced transaction should have been rejected")
            raise AssertionError("Unbalanced transaction was not rejected")

        except ValueError as e:
            assert "not balanced" in str(e)
            logger.info("✅ Unbalanced transaction correctly rejected")
        except Exception as e:
            logger.error(f"❌ Unexpected error in unbalanced test: {str(e)}")
            raise

    async def test_transaction_rollback(self, transaction_id: str):
        """Test transaction rollback functionality"""
        logger.info(f"🧪 Testing transaction rollback for {transaction_id}...")
        
        try:
            # Get initial status
            initial_status = await self.service.get_transaction_status(UUID(transaction_id))
            assert initial_status["status"] == "completed"

            # Perform rollback
            rollback_success = await self.service.rollback_transaction(UUID(transaction_id))
            assert rollback_success is True

            # Check final status
            final_status = await self.service.get_transaction_status(UUID(transaction_id))
            assert final_status["status"] == "rolled_back"

            logger.info("✅ Transaction rollback test passed")

        except Exception as e:
            logger.error(f"❌ Transaction rollback test failed: {str(e)}")
            raise

    async def test_transaction_validation(self):
        """Test transaction validation without execution"""
        logger.info("🧪 Testing transaction validation...")
        
        # Valid transaction
        valid_transactions = [
            {
                "description": "Valid transaction",
                "lines": [
                    {
                        "account_id": str(uuid4()),
                        "description": "Test",
                        "debit_amount": "100.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": str(uuid4()),
                        "description": "Test",
                        "debit_amount": "0.00",
                        "credit_amount": "100.00",
                    }
                ]
            }
        ]

        try:
            # Test validation
            for i, transaction in enumerate(valid_transactions):
                validated = self.service._validate_transaction(transaction, i)
                assert validated["description"] == transaction["description"]
                assert len(validated["lines"]) == 2

            logger.info("✅ Transaction validation test passed")

        except Exception as e:
            logger.error(f"❌ Transaction validation test failed: {str(e)}")
            raise

    async def test_transaction_groups(self):
        """Test transaction group listing"""
        logger.info("🧪 Testing transaction groups...")
        
        try:
            groups = await self.service.list_transaction_groups(
                company_id=self.test_company_id,
                limit=10
            )

            assert isinstance(groups, list)
            logger.info(f"✅ Found {len(groups)} transaction groups")

        except Exception as e:
            logger.error(f"❌ Transaction groups test failed: {str(e)}")
            raise

    async def test_cross_company_transaction(self):
        """Test cross-company transaction capabilities"""
        logger.info("🧪 Testing cross-company transaction...")
        
        # Create transaction with metadata indicating cross-company transfer
        transactions = [
            {
                "description": "Intercompany transfer",
                "lines": [
                    {
                        "account_id": str(uuid4()),
                        "description": "Intercompany receivable",
                        "debit_amount": "5000.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": str(uuid4()),
                        "description": "Intercompany payable",
                        "debit_amount": "0.00",
                        "credit_amount": "5000.00",
                    }
                ]
            }
        ]

        metadata = {
            "transaction_type": "intercompany_transfer",
            "source_company": str(self.test_company_id),
            "target_company": str(uuid4()),
            "transfer_reason": "Loan repayment"
        }

        try:
            result = await self.service.create_atomic_transaction(
                transactions=transactions,
                company_id=self.test_company_id,
                metadata=metadata,
                group_name="Cross Company Transfer",
                description="Intercompany financial transfer"
            )

            assert result["success"] is True
            assert result["status"] == "completed"

            # Verify metadata was stored
            status = await self.service.get_transaction_status(UUID(result["atomic_transaction_id"]))
            assert status["metadata"]["transaction_type"] == "intercompany_transfer"

            logger.info("✅ Cross-company transaction test passed")
            return result["atomic_transaction_id"]

        except Exception as e:
            logger.error(f"❌ Cross-company transaction test failed: {str(e)}")
            raise

    async def run_all_tests(self):
        """Run all atomic transaction tests"""
        logger.info("🚀 Starting atomic transaction test suite...")
        
        test_results = []
        
        try:
            # Test 1: Basic atomic transaction
            transaction_id_1 = await self.test_basic_atomic_transaction()
            test_results.append(("Basic Atomic Transaction", "PASSED"))

            # Test 2: Multi-transaction atomic
            transaction_id_2 = await self.test_multi_transaction_atomic()
            test_results.append(("Multi-Transaction Atomic", "PASSED"))

            # Test 3: Unbalanced transaction rejection
            await self.test_unbalanced_transaction_failure()
            test_results.append(("Unbalanced Transaction Rejection", "PASSED"))

            # Test 4: Transaction validation
            await self.test_transaction_validation()
            test_results.append(("Transaction Validation", "PASSED"))

            # Test 5: Transaction groups
            await self.test_transaction_groups()
            test_results.append(("Transaction Groups", "PASSED"))

            # Test 6: Cross-company transaction
            transaction_id_3 = await self.test_cross_company_transaction()
            test_results.append(("Cross-Company Transaction", "PASSED"))

            # Test 7: Transaction rollback
            await self.test_transaction_rollback(transaction_id_1)
            test_results.append(("Transaction Rollback", "PASSED"))

            # Print test summary
            logger.info("\n" + "="*50)
            logger.info("📊 ATOMIC TRANSACTION TEST RESULTS")
            logger.info("="*50)
            
            passed = 0
            for test_name, result in test_results:
                logger.info(f"{'✅' if result == 'PASSED' else '❌'} {test_name}: {result}")
                if result == "PASSED":
                    passed += 1

            logger.info(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")
            
            if passed == len(test_results):
                logger.info("🎉 All atomic transaction tests passed!")
                return True
            else:
                logger.error("❌ Some tests failed")
                return False

        except Exception as e:
            logger.error(f"❌ Test suite failed with error: {str(e)}")
            return False


async def main():
    """Main test runner"""
    tester = AtomicTransactionTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 Atomic transaction implementation is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Atomic transaction implementation has issues!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
