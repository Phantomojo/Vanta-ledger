#!/usr/bin/python3
"""
Database Integration Testing Script for Vanta Ledger
Tests database connections, migrations, and data operations
"""

import os
import sys
import asyncio
import pytest
import time
import json
import psycopg2
import pymongo
import redis
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIntegrationTestSuite:
    """Comprehensive database integration testing suite"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.test_data = {}
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", data: Dict = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "data": data,
            "timestamp": time.time()
        }
    
    def test_postgresql_connection(self) -> bool:
        """Test PostgreSQL connection"""
        logger.info("🐘 Testing PostgreSQL Connection...")
        
        try:
            # Get connection parameters from environment
            db_host = os.getenv("POSTGRES_HOST", "localhost")
            db_port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB", "vanta_ledger")
            db_user = os.getenv("POSTGRES_USER", "postgres")
            db_password = os.getenv("POSTGRES_PASSWORD", "password")
            
            # Test connection
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            self.log_test_result("PostgreSQL Connection", True, f"Connected successfully, Version: {version[0]}")
            return True
            
        except Exception as e:
            self.log_test_result("PostgreSQL Connection", False, f"Error: {str(e)}")
            return False
    
    def test_mongodb_connection(self) -> bool:
        """Test MongoDB connection"""
        logger.info("🍃 Testing MongoDB Connection...")
        
        try:
            # Get connection parameters from environment
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            db_name = os.getenv("MONGODB_DB", "vanta_ledger")
            
            # Test connection
            client = pymongo.MongoClient(mongo_uri)
            db = client[db_name]
            
            # Test basic operation
            result = db.command("ping")
            
            client.close()
            
            self.log_test_result("MongoDB Connection", True, f"Connected successfully, Ping: {result}")
            return True
            
        except Exception as e:
            self.log_test_result("MongoDB Connection", False, f"Error: {str(e)}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Test Redis connection"""
        logger.info("🔴 Testing Redis Connection...")
        
        try:
            # Get connection parameters from environment
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_db = int(os.getenv("REDIS_DB", "0"))
            
            # Test connection
            r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
            
            # Test basic operations
            r.set("test_key", "test_value")
            value = r.get("test_key")
            r.delete("test_key")
            
            r.close()
            
            self.log_test_result("Redis Connection", True, f"Connected successfully, Test value: {value}")
            return True
            
        except Exception as e:
            self.log_test_result("Redis Connection", False, f"Error: {str(e)}")
            return False
    
    def test_database_migrations(self) -> bool:
        """Test database migrations"""
        logger.info("🔄 Testing Database Migrations...")
        
        try:
            from app.hybrid_database import HybridDatabase
            
            # Initialize database
            db = HybridDatabase()
            
            # Test migration status
            migration_status = db.check_migration_status()
            self.log_test_result("Migration Status", True, f"Migration status: {migration_status}")
            
            # Test schema validation
            schema_valid = db.validate_schema()
            self.log_test_result("Schema Validation", schema_valid, "Schema validation completed")
            
            return True
            
        except Exception as e:
            self.log_test_result("Database Migrations", False, f"Error: {str(e)}")
            return False
    
    def test_data_models(self) -> bool:
        """Test data models and their relationships"""
        logger.info("📊 Testing Data Models...")
        
        try:
            from app.models.document_models import Document, DocumentMetadata
            from app.models.financial_models import FinancialRecord, Company
            from app.models.user_models import User, UserProfile
            
            # Test model imports
            models_loaded = all([
                Document, DocumentMetadata,
                FinancialRecord, Company,
                User, UserProfile
            ])
            
            self.log_test_result("Model Imports", models_loaded, "All models imported successfully")
            
            # Test model validation
            test_document = Document(
                filename="test.pdf",
                content_type="application/pdf",
                size=1024,
                upload_date=datetime.now()
            )
            
            test_user = User(
                email="test@example.com",
                full_name="Test User",
                company_name="Test Company"
            )
            
            self.log_test_result("Model Validation", True, "Models can be instantiated")
            
            return True
            
        except Exception as e:
            self.log_test_result("Data Models", False, f"Error: {str(e)}")
            return False
    
    def test_crud_operations(self) -> bool:
        """Test CRUD operations"""
        logger.info("🔄 Testing CRUD Operations...")
        
        try:
            from app.hybrid_database import HybridDatabase
            from app.models.document_models import Document
            from app.models.user_models import User
            
            db = HybridDatabase()
            
            # Test Create operation
            test_user = User(
                email="crud_test@example.com",
                full_name="CRUD Test User",
                company_name="CRUD Test Company"
            )
            
            created_user = db.create_user(test_user)
            self.log_test_result("Create Operation", bool(created_user), f"User created: {created_user.id if created_user else 'Failed'}")
            
            if created_user:
                # Test Read operation
                retrieved_user = db.get_user_by_email("crud_test@example.com")
                self.log_test_result("Read Operation", bool(retrieved_user), f"User retrieved: {retrieved_user.id if retrieved_user else 'Failed'}")
                
                # Test Update operation
                if retrieved_user:
                    retrieved_user.full_name = "Updated CRUD Test User"
                    updated_user = db.update_user(retrieved_user)
                    self.log_test_result("Update Operation", bool(updated_user), f"User updated: {updated_user.id if updated_user else 'Failed'}")
                
                # Test Delete operation
                deleted = db.delete_user(created_user.id)
                self.log_test_result("Delete Operation", deleted, f"User deleted: {deleted}")
            
            return True
            
        except Exception as e:
            self.log_test_result("CRUD Operations", False, f"Error: {str(e)}")
            return False
    
    def test_data_integrity(self) -> bool:
        """Test data integrity constraints"""
        logger.info("🔒 Testing Data Integrity...")
        
        try:
            from app.hybrid_database import HybridDatabase
            from app.models.user_models import User
            
            db = HybridDatabase()
            
            # Test unique constraint
            user1 = User(
                email="integrity_test@example.com",
                full_name="Integrity Test User 1",
                company_name="Integrity Test Company"
            )
            
            user2 = User(
                email="integrity_test@example.com",  # Same email
                full_name="Integrity Test User 2",
                company_name="Integrity Test Company"
            )
            
            # Create first user
            created1 = db.create_user(user1)
            
            # Try to create second user with same email
            try:
                created2 = db.create_user(user2)
                unique_constraint_works = False
            except:
                unique_constraint_works = True
            
            self.log_test_result("Unique Constraint", unique_constraint_works, "Unique constraint enforced")
            
            # Cleanup
            if created1:
                db.delete_user(created1.id)
            
            return True
            
        except Exception as e:
            self.log_test_result("Data Integrity", False, f"Error: {str(e)}")
            return False
    
    def test_performance_queries(self) -> bool:
        """Test query performance"""
        logger.info("⚡ Testing Query Performance...")
        
        try:
            from app.hybrid_database import HybridDatabase
            from app.models.document_models import Document
            from app.models.user_models import User
            
            db = HybridDatabase()
            
            # Create test data
            test_users = []
            for i in range(10):
                user = User(
                    email=f"perf_test_{i}@example.com",
                    full_name=f"Performance Test User {i}",
                    company_name="Performance Test Company"
                )
                created_user = db.create_user(user)
                if created_user:
                    test_users.append(created_user)
            
            # Test query performance
            start_time = time.time()
            users = db.get_all_users()
            query_time = time.time() - start_time
            
            self.log_test_result("Query Performance", query_time < 1.0, f"Query time: {query_time:.3f}s")
            
            # Cleanup
            for user in test_users:
                db.delete_user(user.id)
            
            return True
            
        except Exception as e:
            self.log_test_result("Query Performance", False, f"Error: {str(e)}")
            return False
    
    def test_backup_recovery(self) -> bool:
        """Test backup and recovery procedures"""
        logger.info("💾 Testing Backup and Recovery...")
        
        try:
            from app.hybrid_database import HybridDatabase
            
            db = HybridDatabase()
            
            # Test backup creation
            backup_path = db.create_backup()
            backup_created = os.path.exists(backup_path) if backup_path else False
            
            self.log_test_result("Backup Creation", backup_created, f"Backup created: {backup_path}")
            
            # Test backup validation
            if backup_created:
                backup_valid = db.validate_backup(backup_path)
                self.log_test_result("Backup Validation", backup_valid, "Backup validation completed")
            
            return True
            
        except Exception as e:
            self.log_test_result("Backup and Recovery", False, f"Error: {str(e)}")
            return False
    
    def test_connection_pooling(self) -> bool:
        """Test connection pooling"""
        logger.info("🏊 Testing Connection Pooling...")
        
        try:
            from app.hybrid_database import HybridDatabase
            
            db = HybridDatabase()
            
            # Test multiple concurrent connections
            import threading
            
            def test_connection():
                try:
                    test_db = HybridDatabase()
                    users = test_db.get_all_users()
                    return True
                except:
                    return False
            
            # Create multiple threads
            threads = []
            results = []
            
            for i in range(5):
                thread = threading.Thread(target=lambda: results.append(test_connection()))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            all_successful = all(results)
            self.log_test_result("Connection Pooling", all_successful, f"Concurrent connections: {sum(results)}/5 successful")
            
            return True
            
        except Exception as e:
            self.log_test_result("Connection Pooling", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all database integration tests"""
        logger.info("🚀 Starting Database Integration Tests...")
        logger.info("=" * 50)
        
        tests = [
            ("PostgreSQL Connection", self.test_postgresql_connection),
            ("MongoDB Connection", self.test_mongodb_connection),
            ("Redis Connection", self.test_redis_connection),
            ("Database Migrations", self.test_database_migrations),
            ("Data Models", self.test_data_models),
            ("CRUD Operations", self.test_crud_operations),
            ("Data Integrity", self.test_data_integrity),
            ("Query Performance", self.test_performance_queries),
            ("Backup and Recovery", self.test_backup_recovery),
            ("Connection Pooling", self.test_connection_pooling),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                success = test_func()
                results[test_name] = success
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {str(e)}")
                results[test_name] = False
        
        # Generate summary
        total_tests = len(results)
        passed_tests = sum(results.values())
        failed_tests = total_tests - passed_tests
        
        logger.info("=" * 50)
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"   Duration: {time.time() - self.start_time:.2f}s")
        
        return {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "duration": time.time() - self.start_time
            },
            "results": results,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution function"""
    print("🧪 Database Integration Testing Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = DatabaseIntegrationTestSuite()
    
    # Run all tests
    results = test_suite.run_all_tests()
    
    # Save results to file
    results_file = "test_database_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Return exit code based on results
    if results["summary"]["failed"] > 0:
        print("❌ Some tests failed!")
        return 1
    else:
        print("✅ All tests passed!")
        return 0

if __name__ == "__main__":
    exit(main()) 