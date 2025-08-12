#!/usr/bin/python3
"""
API Endpoint Testing Script for Vanta Ledger
Tests all REST API endpoints and their functionality
"""

import os
import sys
import asyncio
import pytest
import time
import json
import requests
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from unittest.mock import Mock, patch

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIEndpointTestSuite:
    """Comprehensive API endpoint testing suite"""
    
    def __init__(self, base_url: str = "http://localhost:8500"):
        self.base_url = base_url
        self.test_results = {}
        self.start_time = time.time()
        self.session = requests.Session()
        self.auth_token = None
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": time.time()
        }
    
    def test_server_health(self) -> bool:
        """Test server health endpoint"""
        logger.info("🏥 Testing Server Health...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Version: {data.get('version', 'N/A')}"
            
            self.log_test_result("Server Health", success, details, response.json() if success else None)
            return success
            
        except Exception as e:
            self.log_test_result("Server Health", False, f"Error: {str(e)}")
            return False
    
    def test_authentication_endpoints(self) -> bool:
        """Test authentication endpoints"""
        logger.info("🔐 Testing Authentication Endpoints...")
        
        # Test user registration
        try:
            register_data = {
                "email": "test@example.com",
                "password": "TestPass123!",
                "full_name": "Test User",
                "company_name": "Test Company"
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/auth/register", json=register_data)
            success = response.status_code in [200, 201, 409]  # 409 if user already exists
            details = f"Registration Status: {response.status_code}"
            
            if success and response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                details += ", Token received"
            
            self.log_test_result("User Registration", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("User Registration", False, f"Error: {str(e)}")
        
        # Test user login
        try:
            login_data = {
                "email": "test@example.com",
                "password": "TestPass123!"
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/auth/login", json=login_data)
            success = response.status_code == 200
            details = f"Login Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.auth_token = data.get("access_token")
                details += ", Token received"
            
            self.log_test_result("User Login", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("User Login", False, f"Error: {str(e)}")
        
        # Test token refresh
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.post(f"{self.base_url}/api/v2/auth/refresh", headers=headers)
                success = response.status_code == 200
                details = f"Refresh Status: {response.status_code}"
                
                if success:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    details += ", New token received"
                
                self.log_test_result("Token Refresh", success, details, response.json() if success else None)
                
            except Exception as e:
                self.log_test_result("Token Refresh", False, f"Error: {str(e)}")
        
        return True
    
    def test_document_endpoints(self) -> bool:
        """Test document processing endpoints"""
        logger.info("📄 Testing Document Endpoints...")
        
        if not self.auth_token:
            self.log_test_result("Document Endpoints", False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test document upload
        try:
            # Create a test document
            test_content = "This is a test document for API testing."
            test_file = base64.b64encode(test_content.encode()).decode()
            
            upload_data = {
                "filename": "test_document.txt",
                "content": test_file,
                "content_type": "text/plain",
                "company_id": "test_company"
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/documents/upload", 
                                       json=upload_data, headers=headers)
            success = response.status_code in [200, 201]
            details = f"Upload Status: {response.status_code}"
            
            if success:
                data = response.json()
                document_id = data.get("document_id")
                details += f", Document ID: {document_id}"
            
            self.log_test_result("Document Upload", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Document Upload", False, f"Error: {str(e)}")
        
        # Test document list
        try:
            response = self.session.get(f"{self.base_url}/api/v2/documents/list", headers=headers)
            success = response.status_code == 200
            details = f"List Status: {response.status_code}"
            
            if success:
                data = response.json()
                doc_count = len(data.get("documents", []))
                details += f", Documents: {doc_count}"
            
            self.log_test_result("Document List", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Document List", False, f"Error: {str(e)}")
        
        # Test document processing
        try:
            response = self.session.post(f"{self.base_url}/api/v2/documents/process", 
                                       json={"company_id": "test_company"}, headers=headers)
            success = response.status_code in [200, 202]  # 202 for async processing
            details = f"Process Status: {response.status_code}"
            
            self.log_test_result("Document Processing", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Document Processing", False, f"Error: {str(e)}")
        
        return True
    
    def test_llm_endpoints(self) -> bool:
        """Test LLM-specific endpoints"""
        logger.info("🧠 Testing LLM Endpoints...")
        
        if not self.auth_token:
            self.log_test_result("LLM Endpoints", False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test LLM health
        try:
            response = self.session.get(f"{self.base_url}/api/v2/llm/health", headers=headers)
            success = response.status_code == 200
            details = f"Health Status: {response.status_code}"
            
            if success:
                data = response.json()
                model_status = data.get("model_status", "unknown")
                details += f", Model: {model_status}"
            
            self.log_test_result("LLM Health", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("LLM Health", False, f"Error: {str(e)}")
        
        # Test LLM query
        try:
            query_data = {
                "prompt": "What is the capital of France?",
                "max_tokens": 50,
                "company_context": "test_company"
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/llm/query", 
                                       json=query_data, headers=headers)
            success = response.status_code in [200, 202]  # 202 for async processing
            details = f"Query Status: {response.status_code}"
            
            if success:
                data = response.json()
                response_text = data.get("response", "")[:100]
                details += f", Response: {response_text}..."
            
            self.log_test_result("LLM Query", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("LLM Query", False, f"Error: {str(e)}")
        
        # Test document analysis
        try:
            analysis_data = {
                "document_id": "test_doc_123",
                "analysis_type": "financial",
                "company_context": "test_company"
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/llm/analyze-document", 
                                       json=analysis_data, headers=headers)
            success = response.status_code in [200, 202]
            details = f"Analysis Status: {response.status_code}"
            
            self.log_test_result("Document Analysis", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Document Analysis", False, f"Error: {str(e)}")
        
        return True
    
    def test_financial_endpoints(self) -> bool:
        """Test financial data endpoints"""
        logger.info("💰 Testing Financial Endpoints...")
        
        if not self.auth_token:
            self.log_test_result("Financial Endpoints", False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test financial records list
        try:
            response = self.session.get(f"{self.base_url}/api/v2/financial/records", headers=headers)
            success = response.status_code == 200
            details = f"Records Status: {response.status_code}"
            
            if success:
                data = response.json()
                record_count = len(data.get("records", []))
                details += f", Records: {record_count}"
            
            self.log_test_result("Financial Records", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Financial Records", False, f"Error: {str(e)}")
        
        # Test financial summary
        try:
            response = self.session.get(f"{self.base_url}/api/v2/financial/summary", headers=headers)
            success = response.status_code == 200
            details = f"Summary Status: {response.status_code}"
            
            self.log_test_result("Financial Summary", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Financial Summary", False, f"Error: {str(e)}")
        
        return True
    
    def test_analytics_endpoints(self) -> bool:
        """Test analytics endpoints"""
        logger.info("📊 Testing Analytics Endpoints...")
        
        if not self.auth_token:
            self.log_test_result("Analytics Endpoints", False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test analytics dashboard
        try:
            response = self.session.get(f"{self.base_url}/api/v2/analytics/dashboard", headers=headers)
            success = response.status_code == 200
            details = f"Dashboard Status: {response.status_code}"
            
            self.log_test_result("Analytics Dashboard", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Analytics Dashboard", False, f"Error: {str(e)}")
        
        # Test analytics reports
        try:
            response = self.session.get(f"{self.base_url}/api/v2/analytics/reports", headers=headers)
            success = response.status_code == 200
            details = f"Reports Status: {response.status_code}"
            
            if success:
                data = response.json()
                report_count = len(data.get("reports", []))
                details += f", Reports: {report_count}"
            
            self.log_test_result("Analytics Reports", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Analytics Reports", False, f"Error: {str(e)}")
        
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling endpoints"""
        logger.info("🚨 Testing Error Handling...")
        
        # Test invalid authentication
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = self.session.get(f"{self.base_url}/api/v2/documents/list", headers=headers)
            success = response.status_code == 401
            details = f"Invalid Auth Status: {response.status_code}"
            
            self.log_test_result("Invalid Authentication", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Invalid Authentication", False, f"Error: {str(e)}")
        
        # Test invalid endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v2/invalid/endpoint")
            success = response.status_code == 404
            details = f"Invalid Endpoint Status: {response.status_code}"
            
            self.log_test_result("Invalid Endpoint", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Invalid Endpoint", False, f"Error: {str(e)}")
        
        # Test malformed request
        try:
            response = self.session.post(f"{self.base_url}/api/v2/auth/login", json={"invalid": "data"})
            success = response.status_code in [400, 422]
            details = f"Malformed Request Status: {response.status_code}"
            
            self.log_test_result("Malformed Request", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Malformed Request", False, f"Error: {str(e)}")
        
        return True
    
    def test_performance_endpoints(self) -> bool:
        """Test performance monitoring endpoints"""
        logger.info("⚡ Testing Performance Endpoints...")
        
        if not self.auth_token:
            self.log_test_result("Performance Endpoints", False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test system status
        try:
            response = self.session.get(f"{self.base_url}/api/v2/system/status", headers=headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                cpu_usage = data.get("cpu_usage", "N/A")
                memory_usage = data.get("memory_usage", "N/A")
                details += f", CPU: {cpu_usage}%, Memory: {memory_usage}%"
            
            self.log_test_result("System Status", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("System Status", False, f"Error: {str(e)}")
        
        # Test performance metrics
        try:
            response = self.session.get(f"{self.base_url}/api/v2/system/metrics", headers=headers)
            success = response.status_code == 200
            details = f"Metrics Status: {response.status_code}"
            
            self.log_test_result("Performance Metrics", success, details, response.json() if success else None)
            
        except Exception as e:
            self.log_test_result("Performance Metrics", False, f"Error: {str(e)}")
        
        return True
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API endpoint tests"""
        logger.info("🚀 Starting API Endpoint Tests...")
        logger.info("=" * 50)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Authentication", self.test_authentication_endpoints),
            ("Document Endpoints", self.test_document_endpoints),
            ("LLM Endpoints", self.test_llm_endpoints),
            ("Financial Endpoints", self.test_financial_endpoints),
            ("Analytics Endpoints", self.test_analytics_endpoints),
            ("Error Handling", self.test_error_handling),
            ("Performance Endpoints", self.test_performance_endpoints),
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
    print("🧪 API Endpoint Testing Suite")
    print("=" * 50)
    
    # Get base URL from environment or use default
    base_url = os.getenv("API_BASE_URL", "http://localhost:8500")
    print(f"Testing API at: {base_url}")
    
    # Create test suite
    test_suite = APIEndpointTestSuite(base_url)
    
    # Run all tests
    results = test_suite.run_all_tests()
    
    # Save results to file
    results_file = "test_api_results.json"
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