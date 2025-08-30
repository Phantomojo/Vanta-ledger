#!/usr/bin/python3
"""
Comprehensive Test Runner for Vanta Ledger
Executes all testing scripts and generates unified reports
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """Master test runner for all Vanta Ledger tests"""
    
    def __init__(self, base_url: str = "http://localhost:8500"):
        self.base_url = base_url
        self.test_results = {}
        self.start_time = time.time()
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def log_test_result(self, test_suite: str, success: bool, details: str = "", data: Dict = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_suite}: {details}")
        self.test_results[test_suite] = {
            "success": success,
            "details": details,
            "data": data,
            "timestamp": time.time()
        }
    
    def run_minimal_test(self) -> bool:
        """Run minimal LLM test"""
        logger.info("🧪 Running Minimal LLM Test...")
        
        try:
            result = subprocess.run(["/usr/bin/python3", "test_minimal.py"], 
                                  capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            details = f"Return code: {result.returncode}"
            
            if result.stdout:
                details += f", Output: {result.stdout.strip()[:100]}..."
            
            self.log_test_result("Minimal LLM Test", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_test_result("Minimal LLM Test", False, "Test timed out after 5 minutes")
            return False
        except Exception as e:
            self.log_test_result("Minimal LLM Test", False, f"Error: {str(e)}")
            return False
    
    def run_service_tests(self) -> bool:
        """Run service-specific tests"""
        logger.info("🔧 Running Service-Specific Tests...")
        
        try:
            result = subprocess.run(["/usr/bin/python3", "tests/test_service_specific.py"], 
                                  capture_output=True, text=True, timeout=600)
            
            success = result.returncode == 0
            details = f"Return code: {result.returncode}"
            
            if result.stdout:
                details += f", Output: {result.stdout.strip()[:100]}..."
            
            self.log_test_result("Service Tests", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_test_result("Service Tests", False, "Test timed out after 10 minutes")
            return False
        except Exception as e:
            self.log_test_result("Service Tests", False, f"Error: {str(e)}")
            return False
    
    def run_api_tests(self) -> bool:
        """Run API endpoint tests"""
        logger.info("🌐 Running API Endpoint Tests...")
        
        try:
            # Set environment variable for API base URL
            env = os.environ.copy()
            env["API_BASE_URL"] = self.base_url
            
            result = subprocess.run(["/usr/bin/python3", "tests/test_api_endpoints.py"], 
                                  capture_output=True, text=True, timeout=600, env=env)
            
            success = result.returncode == 0
            details = f"Return code: {result.returncode}"
            
            if result.stdout:
                details += f", Output: {result.stdout.strip()[:100]}..."
            
            self.log_test_result("API Tests", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_test_result("API Tests", False, "Test timed out after 10 minutes")
            return False
        except Exception as e:
            self.log_test_result("API Tests", False, f"Error: {str(e)}")
            return False
    
    def run_database_tests(self) -> bool:
        """Run database integration tests"""
        logger.info("🗄️ Running Database Integration Tests...")
        
        try:
            result = subprocess.run(["/usr/bin/python3", "tests/test_database_integration.py"], 
                                  capture_output=True, text=True, timeout=600)
            
            success = result.returncode == 0
            details = f"Return code: {result.returncode}"
            
            if result.stdout:
                details += f", Output: {result.stdout.strip()[:100]}..."
            
            self.log_test_result("Database Tests", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_test_result("Database Tests", False, "Test timed out after 10 minutes")
            return False
        except Exception as e:
            self.log_test_result("Database Tests", False, f"Error: {str(e)}")
            return False
    
    def run_security_tests(self) -> bool:
        """Run security feature tests"""
        logger.info("🔒 Running Security Feature Tests...")
        
        try:
            # Set environment variable for API base URL
            env = os.environ.copy()
            env["API_BASE_URL"] = self.base_url
            
            result = subprocess.run(["/usr/bin/python3", "tests/test_security_features.py"], 
                                  capture_output=True, text=True, timeout=600, env=env)
            
            success = result.returncode == 0
            details = f"Return code: {result.returncode}"
            
            if result.stdout:
                details += f", Output: {result.stdout.strip()[:100]}..."
            
            self.log_test_result("Security Tests", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_test_result("Security Tests", False, "Test timed out after 10 minutes")
            return False
        except Exception as e:
            self.log_test_result("Security Tests", False, f"Error: {str(e)}")
            return False
    
    def run_existing_tests(self) -> bool:
        """Run existing pytest tests"""
        logger.info("🧪 Running Existing Pytest Tests...")
        
        try:
            result = subprocess.run(["/usr/bin/python3", "-m", "pytest", "tests/", "-v"], 
                                  capture_output=True, text=True, timeout=900)
            
            success = result.returncode == 0
            details = f"Return code: {result.returncode}"
            
            if result.stdout:
                # Extract test summary from pytest output
                lines = result.stdout.split('\n')
                for line in lines:
                    if "passed" in line.lower() and "failed" in line.lower():
                        details += f", Summary: {line.strip()}"
                        break
            
            self.log_test_result("Pytest Tests", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_test_result("Pytest Tests", False, "Test timed out after 15 minutes")
            return False
        except Exception as e:
            self.log_test_result("Pytest Tests", False, f"Error: {str(e)}")
            return False
    
    def check_system_health(self) -> bool:
        """Check system health before running tests"""
        logger.info("🏥 Checking System Health...")
        
        try:
            # Check if backend is running
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=10)
            health_ok = response.status_code == 200
            
            # Check if databases are accessible
            db_ok = True
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=os.getenv("POSTGRES_HOST", "localhost"),
                    port=os.getenv("POSTGRES_PORT", "5432"),
                    database=os.getenv("POSTGRES_DB", "vanta_ledger"),
                    user=os.getenv("POSTGRES_USER", "postgres"),
                    password=os.getenv("POSTGRES_PASSWORD", "password")
                )
                conn.close()
            except:
                db_ok = False
            
            # Check if model files exist
            model_ok = os.path.exists("models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
            
            overall_health = health_ok and db_ok and model_ok
            details = f"Backend: {health_ok}, Database: {db_ok}, Models: {model_ok}"
            
            self.log_test_result("System Health", overall_health, details)
            return overall_health
            
        except Exception as e:
            self.log_test_result("System Health", False, f"Error: {str(e)}")
            return False
    
    def collect_test_reports(self) -> Dict[str, Any]:
        """Collect results from individual test reports"""
        reports = {}
        
        report_files = [
            "test_service_results.json",
            "test_api_results.json", 
            "test_database_results.json",
            "test_security_results.json"
        ]
        
        for report_file in report_files:
            if os.path.exists(report_file):
                try:
                    with open(report_file, 'r') as f:
                        reports[report_file] = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not read report {report_file}: {e}")
        
        return reports
    
    def generate_unified_report(self) -> Dict[str, Any]:
        """Generate unified test report"""
        logger.info("📊 Generating Unified Test Report...")
        
        # Collect individual reports
        individual_reports = self.collect_test_reports()
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for report_name, report_data in individual_reports.items():
            if "summary" in report_data:
                summary = report_data["summary"]
                total_tests += summary.get("total", 0)
                total_passed += summary.get("passed", 0)
                total_failed += summary.get("failed", 0)
        
        # Calculate overall success rate
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Generate unified report
        unified_report = {
            "timestamp": datetime.now().isoformat(),
            "test_duration": time.time() - self.start_time,
            "overall_summary": {
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "success_rate": overall_success_rate,
                "overall_status": "PASS" if overall_success_rate >= 80 else "FAIL"
            },
            "suite_results": self.test_results,
            "individual_reports": individual_reports,
            "recommendations": self.generate_recommendations(individual_reports)
        }
        
        return unified_report
    
    def generate_recommendations(self, reports: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check overall success rate
        total_tests = 0
        total_passed = 0
        
        for report_name, report_data in reports.items():
            if "summary" in report_data:
                summary = report_data["summary"]
                total_tests += summary.get("total", 0)
                total_passed += summary.get("passed", 0)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate < 80:
            recommendations.append("Overall test success rate is below 80%. Review failed tests and fix critical issues.")
        
        if success_rate < 60:
            recommendations.append("Critical: Many tests are failing. System may not be ready for production.")
        
        # Check specific areas
        for report_name, report_data in reports.items():
            if "summary" in report_data:
                summary = report_data["summary"]
                suite_success_rate = summary.get("success_rate", 0)
                
                if "security" in report_name.lower() and suite_success_rate < 90:
                    recommendations.append("Security tests have failures. Address security issues immediately.")
                
                if "database" in report_name.lower() and suite_success_rate < 80:
                    recommendations.append("Database tests have failures. Check database connectivity and configuration.")
                
                if "api" in report_name.lower() and suite_success_rate < 80:
                    recommendations.append("API tests have failures. Verify API endpoints and authentication.")
        
        if not recommendations:
            recommendations.append("All tests passed successfully. System appears ready for deployment.")
        
        return recommendations
    
    def save_reports(self, unified_report: Dict[str, Any]):
        """Save all test reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save unified report
        unified_report_file = self.reports_dir / f"unified_test_report_{timestamp}.json"
        with open(unified_report_file, 'w') as f:
            json.dump(unified_report, f, indent=2, default=str)
        
        # Save summary report
        summary_report = {
            "timestamp": unified_report["timestamp"],
            "overall_summary": unified_report["overall_summary"],
            "recommendations": unified_report["recommendations"]
        }
        
        summary_file = self.reports_dir / f"test_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary_report, f, indent=2, default=str)
        
        # Move individual reports to reports directory
        for report_file in ["test_service_results.json", "test_api_results.json", 
                           "test_database_results.json", "test_security_results.json"]:
            if os.path.exists(report_file):
                try:
                    import shutil
                    shutil.move(report_file, self.reports_dir / report_file)
                except Exception as e:
                    logger.warning(f"Could not move {report_file}: {e}")
        
        logger.info(f"📄 Reports saved to: {self.reports_dir}")
        logger.info(f"📄 Unified report: {unified_report_file}")
        logger.info(f"📄 Summary report: {summary_file}")
    
    def run_all_tests(self, skip_health_check: bool = False) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        logger.info("=" * 60)
        logger.info(f"Testing against: {self.base_url}")
        logger.info(f"Reports directory: {self.reports_dir}")
        logger.info("=" * 60)
        
        # Check system health first
        if not skip_health_check:
            if not self.check_system_health():
                logger.error("❌ System health check failed. Some tests may not work properly.")
                logger.info("You can skip health check with --skip-health-check")
        
        # Run all test suites
        test_suites = [
            ("Minimal LLM Test", self.run_minimal_test),
            ("Service Tests", self.run_service_tests),
            ("API Tests", self.run_api_tests),
            ("Database Tests", self.run_database_tests),
            ("Security Tests", self.run_security_tests),
            ("Pytest Tests", self.run_existing_tests),
        ]
        
        for suite_name, test_func in test_suites:
            try:
                test_func()
            except Exception as e:
                logger.error(f"❌ {suite_name} failed with exception: {str(e)}")
                self.log_test_result(suite_name, False, f"Exception: {str(e)}")
        
        # Generate unified report
        unified_report = self.generate_unified_report()
        
        # Save reports
        self.save_reports(unified_report)
        
        # Print final summary
        logger.info("=" * 60)
        logger.info("📊 FINAL TEST SUMMARY")
        logger.info("=" * 60)
        
        summary = unified_report["overall_summary"]
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed_tests']}")
        logger.info(f"Failed: {summary['failed_tests']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Overall Status: {summary['overall_status']}")
        logger.info(f"Duration: {unified_report['test_duration']:.2f}s")
        
        logger.info("\n📋 RECOMMENDATIONS:")
        for rec in unified_report["recommendations"]:
            logger.info(f"  • {rec}")
        
        logger.info("=" * 60)
        
        return unified_report

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner for Vanta Ledger")
    parser.add_argument("--base-url", default="http://localhost:8500", 
                       help="Base URL for API tests")
    parser.add_argument("--skip-health-check", action="store_true",
                       help="Skip system health check before running tests")
    parser.add_argument("--quick", action="store_true",
                       help="Run only essential tests (minimal + service)")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = ComprehensiveTestRunner(args.base_url)
    
    if args.quick:
        logger.info("🏃 Running Quick Test Suite...")
        # Run only essential tests
        runner.check_system_health()
        runner.run_minimal_test()
        runner.run_service_tests()
    else:
        # Run all tests
        runner.run_all_tests(skip_health_check=args.skip_health_check)
    
    # Return exit code based on results
    if runner.test_results:
        failed_tests = sum(1 for result in runner.test_results.values() if not result["success"])
        if failed_tests > 0:
            logger.error(f"❌ {failed_tests} test suites failed!")
            return 1
        else:
            logger.info("✅ All test suites passed!")
            return 0
    else:
        logger.error("❌ No tests were executed!")
        return 1

if __name__ == "__main__":
    exit(main()) 