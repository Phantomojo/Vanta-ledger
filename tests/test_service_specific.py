#!/usr/bin/python3
"""
Service-Specific Testing Script for Vanta Ledger
Tests individual services and their functionality
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceTestSuite:
    """Comprehensive service testing suite"""

    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()

    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "timestamp": time.time(),
        }

    def test_llm_service(self) -> bool:
        """Test LLM service functionality"""
        logger.info("🧠 Testing LLM Service...")

        try:
            # Test LLM imports
            from app.services.llm.company_context import CompanyContextManager
            from app.services.llm.hardware_detector import HardwareDetector
            from app.services.local_llm_service import LocalLLMService

            # Test hardware detection
            detector = HardwareDetector()
            hardware_info = detector.detect_hardware()
            self.log_test_result(
                "Hardware Detection", True, f"Detected: {hardware_info}"
            )

            # Test LLM service initialization
            llm_service = LocalLLMService()
            self.log_test_result(
                "LLM Service Init", True, "Service initialized successfully"
            )

            # Test model loading
            model_loaded = llm_service.load_model()
            self.log_test_result(
                "Model Loading",
                model_loaded,
                "Model loaded successfully" if model_loaded else "Model loading failed",
            )

            # Test basic inference
            if model_loaded:
                try:
                    response = llm_service.generate_response(
                        "Hello, how are you?", max_tokens=50
                    )
                    self.log_test_result(
                        "Basic Inference", True, f"Response: {response[:100]}..."
                    )
                except Exception as e:
                    self.log_test_result("Basic Inference", False, f"Error: {str(e)}")

            # Test company context
            context_manager = CompanyContextManager()
            context_loaded = context_manager.load_company_context("test_company")
            self.log_test_result(
                "Company Context",
                context_loaded,
                (
                    "Context loaded successfully"
                    if context_loaded
                    else "Context loading failed"
                ),
            )

            return True

        except Exception as e:
            self.log_test_result("LLM Service", False, f"Error: {str(e)}")
            return False

    def test_document_service(self) -> bool:
        """Test document processing service"""
        logger.info("📄 Testing Document Service...")

        try:
            from app.services.document_processor import DocumentProcessor
            from app.services.enhanced_document_service import EnhancedDocumentService

            # Test document processor
            processor = DocumentProcessor()
            self.log_test_result(
                "Document Processor Init", True, "Processor initialized"
            )

            # Test enhanced document service
            doc_service = EnhancedDocumentService()
            self.log_test_result(
                "Enhanced Document Service", True, "Service initialized"
            )

            # Test document validation
            test_doc = {
                "filename": "test.pdf",
                "content_type": "application/pdf",
                "size": 1024,
            }
            is_valid = doc_service.validate_document(test_doc)
            self.log_test_result(
                "Document Validation", is_valid, "Document validation working"
            )

            return True

        except Exception as e:
            self.log_test_result("Document Service", False, f"Error: {str(e)}")
            return False

    def test_analytics_service(self) -> bool:
        """Test analytics service"""
        logger.info("📊 Testing Analytics Service...")

        try:
            from app.services.ai_analytics_service import AIAnalyticsService
            from app.services.analytics_dashboard import AnalyticsDashboard

            # Test analytics dashboard
            dashboard = AnalyticsDashboard()
            self.log_test_result("Analytics Dashboard", True, "Dashboard initialized")

            # Test AI analytics service
            ai_analytics = AIAnalyticsService()
            self.log_test_result("AI Analytics Service", True, "Service initialized")

            # Test data processing
            test_data = {"metric": "test", "value": 100}
            processed = ai_analytics.process_data(test_data)
            self.log_test_result("Data Processing", True, "Data processing working")

            return True

        except Exception as e:
            self.log_test_result("Analytics Service", False, f"Error: {str(e)}")
            return False

    def test_auth_service(self) -> bool:
        """Test authentication service"""
        logger.info("🔐 Testing Authentication Service...")

        try:
            from app.auth import create_access_token, verify_token
            from app.utils.validation import validate_password

            # Test token creation
            test_user = {"user_id": "test123", "email": "test@example.com"}
            token = create_access_token(test_user)
            self.log_test_result(
                "Token Creation", bool(token), "Token created successfully"
            )

            # Test token verification
            if token:
                verified = verify_token(token)
                self.log_test_result(
                    "Token Verification", bool(verified), "Token verified successfully"
                )

            # Test password validation
            valid_password = validate_password("StrongPass123!")
            self.log_test_result(
                "Password Validation", valid_password, "Password validation working"
            )

            return True

        except Exception as e:
            self.log_test_result("Auth Service", False, f"Error: {str(e)}")
            return False

    def test_database_service(self) -> bool:
        """Test database service"""
        logger.info("🗄️ Testing Database Service...")

        try:
            from app.hybrid_database import HybridDatabase
            from app.models.document_models import Document
            from app.models.financial_models import FinancialRecord

            # Test database initialization
            db = HybridDatabase()
            self.log_test_result("Database Init", True, "Database initialized")

            # Test model imports
            doc_model = Document
            financial_model = FinancialRecord
            self.log_test_result("Model Imports", True, "Models imported successfully")

            return True

        except Exception as e:
            self.log_test_result("Database Service", False, f"Error: {str(e)}")
            return False

    def test_file_service(self) -> bool:
        """Test file management service"""
        logger.info("📁 Testing File Service...")

        try:
            from app.utils.document_utils import DocumentUtils
            from app.utils.file_utils import FileUtils

            # Test file utilities
            file_utils = FileUtils()
            self.log_test_result("File Utils", True, "File utilities initialized")

            # Test document utilities
            doc_utils = DocumentUtils()
            self.log_test_result(
                "Document Utils", True, "Document utilities initialized"
            )

            # Test file path operations
            test_path = "/tmp/test_file.txt"
            is_valid = file_utils.is_valid_file_path(test_path)
            self.log_test_result(
                "File Path Validation", True, "Path validation working"
            )

            return True

        except Exception as e:
            self.log_test_result("File Service", False, f"Error: {str(e)}")
            return False

    def test_integration_service(self) -> bool:
        """Test system integration service"""
        logger.info("🔗 Testing Integration Service...")

        try:
            from app.integration.system_integrator import SystemIntegrator

            # Test system integrator
            integrator = SystemIntegrator()
            self.log_test_result("System Integrator", True, "Integrator initialized")

            # Test service connections
            connections = integrator.check_service_connections()
            self.log_test_result("Service Connections", True, "Connections checked")

            return True

        except Exception as e:
            self.log_test_result("Integration Service", False, f"Error: {str(e)}")
            return False

    def test_optimization_service(self) -> bool:
        """Test performance optimization service"""
        logger.info("⚡ Testing Optimization Service...")

        try:
            from app.optimizations.performance_optimizer import PerformanceOptimizer

            # Test performance optimizer
            optimizer = PerformanceOptimizer()
            self.log_test_result("Performance Optimizer", True, "Optimizer initialized")

            # Test optimization checks
            optimizations = optimizer.get_available_optimizations()
            self.log_test_result(
                "Optimization Checks", True, f"Found {len(optimizations)} optimizations"
            )

            return True

        except Exception as e:
            self.log_test_result("Optimization Service", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all service tests"""
        logger.info("🚀 Starting Service-Specific Tests...")
        logger.info("=" * 50)

        tests = [
            ("LLM Service", self.test_llm_service),
            ("Document Service", self.test_document_service),
            ("Analytics Service", self.test_analytics_service),
            ("Auth Service", self.test_auth_service),
            ("Database Service", self.test_database_service),
            ("File Service", self.test_file_service),
            ("Integration Service", self.test_integration_service),
            ("Optimization Service", self.test_optimization_service),
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
                "success_rate": (passed_tests / total_tests) * 100,
                "duration": time.time() - self.start_time,
            },
            "results": results,
            "detailed_results": self.test_results,
        }


def main():
    """Main test execution function"""
    print("🧪 Service-Specific Testing Suite")
    print("=" * 50)

    # Create test suite
    test_suite = ServiceTestSuite()

    # Run all tests
    results = test_suite.run_all_tests()

    # Save results to file
    results_file = "test_service_results.json"
    with open(results_file, "w") as f:
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
