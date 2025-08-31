#!/usr/bin/env python3
"""
HRM Integration Test Script
Tests the integration of HRM (Hierarchical Reasoning Model) with Vanta Ledger
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from vanta_ledger.services.hrm_service import hrm_service, HRMConfig


class HRMIntegrationTester:
    """Comprehensive tester for HRM integration"""
    
    def __init__(self):
        self.test_results = []
        
    async def test_hrm_service_initialization(self) -> Dict[str, Any]:
        """Test HRM service initialization"""
        print("🔧 Testing HRM Service Initialization...")
        
        try:
            result = {
                "test": "hrm_service_initialization",
                "device": hrm_service.device,
                "model_path": hrm_service.config.model_path,
                "is_loaded": hrm_service.is_loaded,
                "company_contexts": len(hrm_service.company_contexts),
                "success": True
            }
            
            print(f"✅ Device: {result['device']}")
            print(f"✅ Model path: {result['model_path']}")
            print(f"✅ Model loaded: {result['is_loaded']}")
            print(f"✅ Company contexts: {result['company_contexts']}")
            
            return result
            
        except Exception as e:
            print(f"❌ HRM service initialization failed: {e}")
            return {
                "test": "hrm_service_initialization",
                "error": str(e),
                "success": False
            }
    
    async def test_model_loading(self) -> Dict[str, Any]:
        """Test HRM model loading"""
        print("\n🧠 Testing HRM Model Loading...")
        
        try:
            success = await hrm_service.load_model()
            
            result = {
                "test": "hrm_model_loading",
                "model_loaded": success,
                "is_loaded": hrm_service.is_loaded,
                "device": hrm_service.device,
                "success": success
            }
            
            if success:
                print(f"✅ Model loaded successfully")
                print(f"✅ Device: {result['device']}")
                print(f"✅ Model state: {result['is_loaded']}")
            else:
                print(f"⚠️ Model loading failed (this is expected if HRM modules are not available)")
            
            return result
            
        except Exception as e:
            print(f"❌ Model loading test failed: {e}")
            return {
                "test": "hrm_model_loading",
                "error": str(e),
                "success": False
            }
    
    async def test_document_analysis(self) -> Dict[str, Any]:
        """Test HRM document analysis"""
        print("\n📄 Testing HRM Document Analysis...")
        
        try:
            test_documents = [
                {
                    "text": """
                    INVOICE
                    From: TechCorp Solutions
                    Date: 2024-01-15
                    Amount: $1,250.00
                    Services: Cloud hosting and software licenses
                    Due Date: 2024-02-15
                    """,
                    "type": "invoice",
                    "company_id": "tech_company_001"
                },
                {
                    "text": """
                    RECEIPT
                    Vendor: Coffee Shop Express
                    Date: 01/20/2024
                    Items: Coffee $4.50, Sandwich $12.99
                    Total: $17.49
                    Payment: Credit Card
                    """,
                    "type": "receipt",
                    "company_id": "retail_company_002"
                }
            ]
            
            results = []
            for i, doc in enumerate(test_documents):
                try:
                    analysis = await hrm_service.analyze_financial_document(
                        document_text=doc["text"],
                        document_type=doc["type"],
                        company_id=doc["company_id"],
                        business_context={
                            "business_rules": {
                                "approval_threshold": 1000,
                                "expense_categories": ["cloud_services", "meals"],
                                "compliance_rules": ["basic_accounting", "tax_compliance"]
                            }
                        }
                    )
                    
                    results.append({
                        "document": i + 1,
                        "type": doc["type"],
                        "decision": analysis.decision,
                        "confidence": analysis.confidence,
                        "risk_level": analysis.risk_assessment.get('level', 'unknown'),
                        "processing_time": analysis.processing_time,
                        "business_rules_applied": len(analysis.business_rules_applied),
                        "compliance_checks": len(analysis.compliance_checks),
                        "recommendations": len(analysis.recommendations),
                        "success": True
                    })
                    
                    print(f"✅ Document {i+1} ({doc['type']}): Decision={analysis.decision}, Confidence={analysis.confidence:.2f}")
                    
                except Exception as e:
                    results.append({
                        "document": i + 1,
                        "type": doc["type"],
                        "error": str(e),
                        "success": False
                    })
                    print(f"❌ Document {i+1} failed: {e}")
            
            return {
                "test": "hrm_document_analysis",
                "results": results,
                "success": all(r["success"] for r in results)
            }
            
        except Exception as e:
            print(f"❌ Document analysis test failed: {e}")
            return {
                "test": "hrm_document_analysis",
                "error": str(e),
                "success": False
            }
    
    async def test_business_rule_application(self) -> Dict[str, Any]:
        """Test HRM business rule application"""
        print("\n🏢 Testing HRM Business Rule Application...")
        
        try:
            test_rules = [
                {
                    "rule_name": "high_amount_approval",
                    "conditions": {"amount_threshold": 5000},
                    "actions": ["require_approval", "flag_for_review"]
                },
                {
                    "rule_name": "vendor_whitelist",
                    "conditions": {"vendor_check": True},
                    "actions": ["auto_approve", "log_transaction"]
                }
            ]
            
            results = []
            for i, rule in enumerate(test_rules):
                try:
                    # Create mock document for rule testing
                    mock_document = f"Rule: {rule['rule_name']}, Conditions: {rule['conditions']}"
                    
                    analysis = await hrm_service.analyze_financial_document(
                        document_text=mock_document,
                        document_type="business_rule",
                        company_id="test_company",
                        business_context={"business_rules": {rule["rule_name"]: rule["conditions"]}}
                    )
                    
                    results.append({
                        "rule": i + 1,
                        "rule_name": rule["rule_name"],
                        "decision": analysis.decision,
                        "confidence": analysis.confidence,
                        "business_rules_applied": len(analysis.business_rules_applied),
                        "recommendations": len(analysis.recommendations),
                        "success": True
                    })
                    
                    print(f"✅ Rule {i+1} ({rule['rule_name']}): Decision={analysis.decision}, Confidence={analysis.confidence:.2f}")
                    
                except Exception as e:
                    results.append({
                        "rule": i + 1,
                        "rule_name": rule["rule_name"],
                        "error": str(e),
                        "success": False
                    })
                    print(f"❌ Rule {i+1} failed: {e}")
            
            return {
                "test": "hrm_business_rule_application",
                "results": results,
                "success": all(r["success"] for r in results)
            }
            
        except Exception as e:
            print(f"❌ Business rule application test failed: {e}")
            return {
                "test": "hrm_business_rule_application",
                "error": str(e),
                "success": False
            }
    
    async def test_compliance_checking(self) -> Dict[str, Any]:
        """Test HRM compliance checking"""
        print("\n📋 Testing HRM Compliance Checking...")
        
        try:
            test_compliance = [
                {
                    "document_type": "invoice",
                    "regulations": ["basic_accounting", "tax_compliance"],
                    "company_id": "regulated_company_001"
                },
                {
                    "document_type": "receipt",
                    "regulations": ["audit_standards", "expense_policies"],
                    "company_id": "audit_company_002"
                }
            ]
            
            results = []
            for i, compliance in enumerate(test_compliance):
                try:
                    # Create mock document for compliance testing
                    mock_document = f"Document Type: {compliance['document_type']}, Regulations: {compliance['regulations']}"
                    
                    analysis = await hrm_service.analyze_financial_document(
                        document_text=mock_document,
                        document_type=compliance["document_type"],
                        company_id=compliance["company_id"],
                        business_context={"compliance_rules": compliance["regulations"]}
                    )
                    
                    results.append({
                        "compliance": i + 1,
                        "document_type": compliance["document_type"],
                        "regulations": len(compliance["regulations"]),
                        "compliance_checks": len(analysis.compliance_checks),
                        "overall_compliance": all(check.get('status') == 'pass' for check in analysis.compliance_checks),
                        "recommendations": len(analysis.recommendations),
                        "success": True
                    })
                    
                    print(f"✅ Compliance {i+1} ({compliance['document_type']}): Checks={len(analysis.compliance_checks)}, Passed={results[-1]['overall_compliance']}")
                    
                except Exception as e:
                    results.append({
                        "compliance": i + 1,
                        "document_type": compliance["document_type"],
                        "error": str(e),
                        "success": False
                    })
                    print(f"❌ Compliance {i+1} failed: {e}")
            
            return {
                "test": "hrm_compliance_checking",
                "results": results,
                "success": all(r["success"] for r in results)
            }
            
        except Exception as e:
            print(f"❌ Compliance checking test failed: {e}")
            return {
                "test": "hrm_compliance_checking",
                "error": str(e),
                "success": False
            }
    
    async def test_risk_assessment(self) -> Dict[str, Any]:
        """Test HRM risk assessment"""
        print("\n🚨 Testing HRM Risk Assessment...")
        
        try:
            test_risks = [
                {
                    "document_text": "Normal business expense for office supplies",
                    "amount": 150.00,
                    "vendor": "Office Depot",
                    "company_id": "low_risk_company"
                },
                {
                    "document_text": "URGENT: Large payment for confidential services",
                    "amount": 50000.00,
                    "vendor": "Unknown Vendor",
                    "company_id": "high_risk_company"
                }
            ]
            
            results = []
            for i, risk in enumerate(test_risks):
                try:
                    # Create document text with risk factors
                    risk_document = f"Document: {risk['document_text']}"
                    if risk.get('amount'):
                        risk_document += f", Amount: {risk['amount']}"
                    if risk.get('vendor'):
                        risk_document += f", Vendor: {risk['vendor']}"
                    
                    analysis = await hrm_service.analyze_financial_document(
                        document_text=risk_document,
                        document_type="risk_assessment",
                        company_id=risk["company_id"],
                        business_context={"risk_factors": ["amount", "vendor", "content"]}
                    )
                    
                    results.append({
                        "risk": i + 1,
                        "risk_level": analysis.risk_assessment.get('level', 'unknown'),
                        "risk_score": analysis.risk_assessment.get('score', 0.0),
                        "risk_factors": len(analysis.risk_assessment.get('factors', [])),
                        "recommendations": len(analysis.risk_assessment.get('recommendations', [])),
                        "confidence": analysis.confidence,
                        "success": True
                    })
                    
                    print(f"✅ Risk {i+1}: Level={results[-1]['risk_level']}, Score={results[-1]['risk_score']:.2f}")
                    
                except Exception as e:
                    results.append({
                        "risk": i + 1,
                        "error": str(e),
                        "success": False
                    })
                    print(f"❌ Risk {i+1} failed: {e}")
            
            return {
                "test": "hrm_risk_assessment",
                "results": results,
                "success": all(r["success"] for r in results)
            }
            
        except Exception as e:
            print(f"❌ Risk assessment test failed: {e}")
            return {
                "test": "hrm_risk_assessment",
                "error": str(e),
                "success": False
            }
    
    async def test_service_status(self) -> Dict[str, Any]:
        """Test HRM service status"""
        print("\n📊 Testing HRM Service Status...")
        
        try:
            status = await hrm_service.get_service_status()
            
            result = {
                "test": "hrm_service_status",
                "service": status.get('service'),
                "status": status.get('status'),
                "model_loaded": status.get('model_loaded'),
                "device": status.get('device'),
                "capabilities": len(status.get('capabilities', [])),
                "company_contexts": status.get('company_contexts'),
                "success": True
            }
            
            print(f"✅ Service: {result['service']}")
            print(f"✅ Status: {result['status']}")
            print(f"✅ Model loaded: {result['model_loaded']}")
            print(f"✅ Device: {result['device']}")
            print(f"✅ Capabilities: {result['capabilities']}")
            print(f"✅ Company contexts: {result['company_contexts']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Service status test failed: {e}")
            return {
                "test": "hrm_service_status",
                "error": str(e),
                "success": False
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all HRM integration tests"""
        print("🤖 HRM Integration Testing")
        print("=" * 60)
        
        tests = [
            self.test_hrm_service_initialization,
            self.test_model_loading,
            self.test_document_analysis,
            self.test_business_rule_application,
            self.test_compliance_checking,
            self.test_risk_assessment,
            self.test_service_status
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
                self.test_results.append(result)
            except Exception as e:
                error_result = {
                    "test": test.__name__,
                    "error": str(e),
                    "success": False
                }
                results.append(error_result)
                self.test_results.append(error_result)
                print(f"❌ Test {test.__name__} failed: {e}")
        
        # Generate summary
        successful_tests = [r for r in results if r.get("success", False)]
        failed_tests = [r for r in results if not r.get("success", False)]
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(results) if results else 0,
            "test_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Successful: {summary['successful_tests']}/{summary['total_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}/{summary['total_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1%}")
        
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test.get('test', 'Unknown')}: {test.get('error', 'Unknown error')}")
        
        return summary


async def main():
    """Main test runner"""
    tester = HRMIntegrationTester()
    summary = await tester.run_all_tests()
    
    # Save results to file
    output_file = "hrm_integration_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Test results saved to: {output_file}")
    
    # Return exit code based on success rate
    if summary["success_rate"] >= 0.7:
        print("🎉 HRM integration test completed successfully!")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the results.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
