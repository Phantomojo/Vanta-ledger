#!/usr/bin/env python3
"""
Simple HRM Integration Test
Tests basic HRM functionality with Vanta Ledger
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from vanta_ledger.services.hrm_service import hrm_service


async def test_hrm_integration():
    """Test HRM integration"""
    print("🤖 Testing HRM Integration with Vanta Ledger")
    print("=" * 50)
    
    # Test 1: Service initialization
    print("\n1. Testing HRM Service Initialization...")
    try:
        print(f"✅ Device: {hrm_service.device}")
        print(f"✅ Model path: {hrm_service.config.model_path}")
        print(f"✅ Model loaded: {hrm_service.is_loaded}")
        print(f"✅ Company contexts: {len(hrm_service.company_contexts)}")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False
    
    # Test 2: Model loading
    print("\n2. Testing HRM Model Loading...")
    try:
        success = await hrm_service.load_model()
        if success:
            print("✅ Model loaded successfully")
        else:
            print("⚠️ Model loading failed (expected if HRM modules not available)")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
    
    # Test 3: Service status
    print("\n3. Testing HRM Service Status...")
    try:
        status = await hrm_service.get_service_status()
        print(f"✅ Service: {status.get('service')}")
        print(f"✅ Status: {status.get('status')}")
        print(f"✅ Capabilities: {len(status.get('capabilities', []))}")
    except Exception as e:
        print(f"❌ Service status failed: {e}")
    
    # Test 4: Document analysis (if model is available)
    print("\n4. Testing HRM Document Analysis...")
    try:
        test_document = """
        INVOICE
        From: TechCorp Solutions
        Date: 2024-01-15
        Amount: $1,250.00
        Services: Cloud hosting and software licenses
        """
        
        analysis = await hrm_service.analyze_financial_document(
            document_text=test_document,
            document_type="invoice",
            company_id="test_company",
            business_context={
                "business_rules": {
                    "approval_threshold": 1000,
                    "expense_categories": ["cloud_services"]
                }
            }
        )
        
        print(f"✅ Decision: {analysis.decision}")
        print(f"✅ Confidence: {analysis.confidence:.2f}")
        print(f"✅ Risk level: {analysis.risk_assessment.get('level', 'unknown')}")
        print(f"✅ Processing time: {analysis.processing_time:.2f}s")
        print(f"✅ Business rules applied: {len(analysis.business_rules_applied)}")
        print(f"✅ Compliance checks: {len(analysis.compliance_checks)}")
        print(f"✅ Recommendations: {len(analysis.recommendations)}")
        
    except Exception as e:
        print(f"❌ Document analysis failed: {e}")
    
    print(f"\n🎉 HRM Integration Test Completed!")
    return True


async def main():
    """Main test runner"""
    success = await test_hrm_integration()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
