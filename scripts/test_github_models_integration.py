#!/usr/bin/env python3
"""
Test GitHub Models Integration
Comprehensive test of the GitHub Models service and all its capabilities
"""

import os
import json
import asyncio
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if GitHub Models is properly configured"""
    token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print("❌ GITHUB_TOKEN not found in environment!")
        print("💡 Set it with: export GITHUB_TOKEN='your_token_here'")
        print("💡 Or add it to your .env file: GITHUB_TOKEN=your_token_here")
        return False
    
    print(f"✅ GitHub Token found: {token[:10]}...***")
    return True

async def test_github_models_service():
    """Test the GitHub Models service directly"""
    print("\n🚀 Testing GitHub Models Service...")
    
    try:
        from src.vanta_ledger.services.github_models_service import github_models_service
        
        print(f"✅ Service enabled: {github_models_service.enabled}")
        print(f"✅ Default model: {github_models_service.default_model}")
        print(f"✅ Available prompts: {github_models_service.get_available_prompts()}")
        
        return github_models_service
        
    except ImportError as e:
        print(f"❌ Failed to import GitHub Models service: {e}")
        return None
    except Exception as e:
        print(f"❌ Error initializing GitHub Models service: {e}")
        return None

async def test_document_analysis(service):
    """Test financial document analysis"""
    print("\n📄 Testing Document Analysis...")
    
    sample_invoice = """
    INVOICE #INV-2024-001
    
    TechCorp Solutions Inc.
    123 Innovation Drive
    Tech City, TC 12345
    
    Bill To:
    Startup Company LLC
    456 Business Blvd
    Business City, BC 67890
    
    Date: 2024-01-15
    Due Date: 2024-02-14
    
    Description                  Qty    Unit Price    Total
    Software Development         40     $150.00       $6,000.00
    Consulting Services          10     $200.00       $2,000.00
    Project Management           1      $500.00       $500.00
    
    Subtotal:                                         $8,500.00
    Tax (8.5%):                                       $722.50
    Total Amount:                                     $9,222.50
    
    Payment Terms: Net 30
    """
    
    try:
        result = await service.analyze_financial_document(sample_invoice, "invoice")
        
        print("✅ Document Analysis Results:")
        print(f"   Vendor: {result.get('vendor', 'N/A')}")
        print(f"   Amount: ${result.get('amount', 'N/A')}")
        print(f"   Invoice #: {result.get('invoice_number', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Document analysis failed: {e}")
        return None

async def test_expense_categorization(service):
    """Test expense categorization"""
    print("\n💰 Testing Expense Categorization...")
    
    test_expenses = [
        {
            "description": "Microsoft Office 365 Business Premium subscription",
            "amount": 22.00,
            "vendor": "Microsoft Corporation"
        },
        {
            "description": "Lunch meeting with potential client",
            "amount": 85.50,
            "vendor": "Downtown Bistro"
        },
        {
            "description": "New laptops for development team",
            "amount": 2499.99,
            "vendor": "Dell Technologies"
        }
    ]
    
    results = []
    
    for expense in test_expenses:
        try:
            result = await service.categorize_expense(
                description=expense["description"],
                amount=expense["amount"],
                vendor=expense["vendor"]
            )
            
            print(f"✅ Expense: {expense['description'][:50]}...")
            print(f"   Category: {result.get('category', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}%")
            print(f"   Tax Deductible: {result.get('tax_deductible', 'N/A')}")
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Expense categorization failed: {e}")
            results.append(None)
    
    return results

async def test_financial_insights(service):
    """Test financial insights generation"""
    print("\n📊 Testing Financial Insights...")
    
    sample_financial_data = {
        "total_expenses": 125000,
        "total_revenue": 200000,
        "monthly_trend": "+12.5%",
        "expense_categories": {
            "Software & Subscriptions": 35000,
            "Marketing & Advertising": 28000,
            "Office Supplies & Equipment": 15000,
            "Professional Services": 20000,
            "Travel & Transportation": 12000,
            "Other": 15000
        },
        "top_vendors": [
            {"name": "Microsoft", "amount": 15000},
            {"name": "Google Ads", "amount": 12000},
            {"name": "AWS", "amount": 8000}
        ],
        "vendor_concentration": {
            "top_vendor_percentage": 25
        }
    }
    
    try:
        result = await service.generate_financial_insights(
            financial_data=sample_financial_data,
            period="Q1 2024",
            company_size="startup",
            industry="technology"
        )
        
        print("✅ Financial Insights Generated:")
        print(f"   Executive Summary: {result.get('executive_summary', 'N/A')[:100]}...")
        print(f"   Key Insights: {len(result.get('key_insights', []))} insights")
        print(f"   Recommendations: {len(result.get('recommendations', []))} recommendations")
        print(f"   Risk Level: {result.get('risk_assessment', {}).get('overall_level', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Financial insights generation failed: {e}")
        return None

async def test_report_generation(service):
    """Test comprehensive report generation"""
    print("\n📈 Testing Report Generation...")
    
    sample_financial_data = {
        "revenue": 250000,
        "expenses": 180000,
        "net_profit": 70000,
        "profit_margin": 28.0,
        "categories": {
            "Software": 45000,
            "Marketing": 35000,
            "Operations": 60000,
            "Admin": 40000
        },
        "growth": 15.5,
        "cash_flow": 85000
    }
    
    try:
        result = await service.generate_financial_report(
            financial_data=sample_financial_data,
            report_type="quarterly",
            period="Q1 2024",
            company_name="TechStart Inc.",
            context="Fast-growing technology startup in scaling phase"
        )
        
        print("✅ Financial Report Generated:")
        print(f"   Report Title: {result.get('report_metadata', {}).get('title', 'N/A')}")
        print(f"   Executive Summary: {len(result.get('executive_summary', {}).get('key_highlights', []))} highlights")
        print(f"   KPIs: {len(result.get('kpis', []))} metrics")
        print(f"   Recommendations: {len(result.get('recommendations', []))} recommendations")
        print(f"   Confidence: {result.get('confidence_level', 'N/A')}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return None

async def test_natural_language_query(service):
    """Test natural language querying"""
    print("\n🤖 Testing Natural Language Query...")
    
    context_data = {
        "total_expenses": 125000,
        "top_expense_category": "Software & Subscriptions",
        "monthly_growth": 12.5,
        "vendor_count": 45,
        "recent_transactions": [
            {"vendor": "Microsoft", "amount": 500, "category": "Software"},
            {"vendor": "AWS", "amount": 1200, "category": "Infrastructure"},
            {"vendor": "Office Depot", "amount": 150, "category": "Supplies"}
        ]
    }
    
    queries = [
        "What is our biggest expense category and how much are we spending on it?",
        "Are we growing too fast? What should we watch out for?",
        "Which vendor should we negotiate better rates with?"
    ]
    
    results = []
    
    for query in queries:
        try:
            result = await service.natural_language_query(query, context_data)
            
            print(f"✅ Query: {query}")
            print(f"   Answer: {result.get('direct_answer', 'N/A')[:100]}...")
            print(f"   Confidence: {result.get('confidence', 'N/A')}%")
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Natural language query failed: {e}")
            results.append(None)
    
    return results

async def test_system_analysis():
    """Test system analysis service"""
    print("\n🔧 Testing System Analysis Service...")
    
    try:
        from src.vanta_ledger.services.system_analysis_service import system_analysis_service
        
        print(f"✅ System Analysis Service enabled: {system_analysis_service.enabled}")
        
        if system_analysis_service.enabled:
            # Test system health analysis
            print("   Testing system health analysis...")
            health_result = await system_analysis_service.analyze_system_health(include_logs=False)
            
            print(f"   System Status: {health_result.get('system_status', 'N/A')}")
            print(f"   Health Score: {health_result.get('overall_health_score', 'N/A')}")
            print(f"   Critical Alerts: {len(health_result.get('critical_alerts', []))}")
            
            return health_result
        
    except Exception as e:
        print(f"❌ System analysis service test failed: {e}")
        return None

async def test_api_endpoints():
    """Test API endpoints (if server is running)"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import httpx
        
        base_url = "http://localhost:8500"
        
        # Test health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/github-models/health")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ GitHub Models API Health:")
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Token Configured: {data.get('token_configured', 'N/A')}")
                print(f"   Available Prompts: {len(data.get('available_prompts', []))}")
                return data
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return None
                
    except ImportError:
        print("❌ httpx not available for API testing")
        return None
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return None

async def main():
    """Run comprehensive GitHub Models integration tests"""
    print("🧪 GitHub Models Integration Test Suite")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please configure GITHUB_TOKEN.")
        return
    
    # Test service initialization
    service = await test_github_models_service()
    if not service or not service.enabled:
        print("❌ GitHub Models service not available. Check your configuration.")
        return
    
    # Run all tests
    tests = [
        ("Document Analysis", test_document_analysis(service)),
        ("Expense Categorization", test_expense_categorization(service)),
        ("Financial Insights", test_financial_insights(service)),
        ("Report Generation", test_report_generation(service)),
        ("Natural Language Query", test_natural_language_query(service)),
        ("System Analysis", test_system_analysis()),
        ("API Endpoints", test_api_endpoints())
    ]
    
    results = {}
    
    for test_name, test_coro in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_coro
            results[test_name] = result
            print(f"✅ {test_name} completed successfully")
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = None
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 Test Summary")
    print("=" * 50)
    
    successful_tests = sum(1 for result in results.values() if result is not None)
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed Tests: {total_tests - successful_tests}/{total_tests}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result is not None else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    if successful_tests == total_tests:
        print(f"\n🎉 All tests passed! GitHub Models integration is working perfectly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the error messages above.")
    
    print(f"\n💡 To use GitHub Models in your application:")
    print(f"   1. Set GITHUB_TOKEN environment variable")
    print(f"   2. Import services from src.vanta_ledger.services")
    print(f"   3. Use the /github-models API endpoints")
    print(f"   4. Upload documents via /github-models/analyze-document-upload")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())





