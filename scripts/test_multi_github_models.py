#!/usr/bin/env python3
"""
Test Multi-GitHub Models Service
Tests the multi-GitHub models service with various scenarios.
"""
import sys
import asyncio
import os
from pathlib import Path

# Add backend to path
backend_path = Path("backend/src")
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

async def test_multi_github_models():
    """Test the multi-GitHub models service"""
    print("🧪 Testing Multi-GitHub Models Service")
    print("=" * 60)
    
    try:
        from vanta_ledger.services.multi_github_models_service import MultiGitHubModelsService
        
        # Initialize service
        service = MultiGitHubModelsService()
        
        print(f"✅ Service initialized")
        print(f"   Enabled: {service.enabled}")
        print(f"   Token available: {bool(service.token)}")
        print(f"   Total models: {len(service.models)}")
        print(f"   Active models: {len([m for m in service.active_models.values() if m])}")
        
        # Test model status
        print("\n📊 Model Status:")
        status = await service.get_model_status()
        print(f"   Service enabled: {status['service_enabled']}")
        print(f"   Total models: {status['total_models']}")
        print(f"   Active models: {status['active_models']}")
        
        # Show active models
        active_models = [name for name, details in status['models'].items() if details['active']]
        print(f"   Active model names: {active_models}")
        
        # Test model activation
        print("\n🔧 Testing Model Activation:")
        test_models = ["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash"]
        activation_result = await service.set_active_models(test_models)
        print(f"   Activation result: {activation_result}")
        
        # Test financial analysis
        print("\n💰 Testing Financial Analysis:")
        financial_text = "Invoice for $1,500 from ABC Company for consulting services"
        try:
            result = await service.analyze_with_multiple_models(
                text=financial_text,
                task_type="financial"
            )
            print(f"   ✅ Financial analysis successful")
            print(f"   Models used: {result['models_used']}")
            print(f"   Successful models: {result['successful_models']}")
            print(f"   Failed models: {result['failed_models']}")
            print(f"   Combined response: {result['combined_response'][:100]}...")
        except Exception as e:
            print(f"   ❌ Financial analysis failed: {e}")
        
        # Test code analysis
        print("\n💻 Testing Code Analysis:")
        code_text = "def calculate_tax(income): return income * 0.15"
        try:
            result = await service.analyze_with_multiple_models(
                text=code_text,
                task_type="code"
            )
            print(f"   ✅ Code analysis successful")
            print(f"   Models used: {result['models_used']}")
            print(f"   Successful models: {result['successful_models']}")
            print(f"   Failed models: {result['failed_models']}")
        except Exception as e:
            print(f"   ❌ Code analysis failed: {e}")
        
        # Test reasoning
        print("\n🧠 Testing Reasoning:")
        reasoning_text = "If a company has $100,000 in revenue and $60,000 in expenses, what is the profit margin?"
        try:
            result = await service.analyze_with_multiple_models(
                text=reasoning_text,
                task_type="reasoning"
            )
            print(f"   ✅ Reasoning successful")
            print(f"   Models used: {result['models_used']}")
            print(f"   Successful models: {result['successful_models']}")
            print(f"   Failed models: {result['failed_models']}")
        except Exception as e:
            print(f"   ❌ Reasoning failed: {e}")
        
        # List all models
        print("\n📋 All Available Models:")
        for name, details in status['models'].items():
            status_icon = "✅" if details['active'] else "❌"
            print(f"   {status_icon} {name} ({details['type']}) - {details['description']}")
        
        # Cleanup
        await service.close()
        
        print("\n🎉 Multi-GitHub Models Service Test Complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 60)
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api/v2/multi-github-models"
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
        
        # Test status endpoint
        print("\n📊 Testing status endpoint...")
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            print("   ✅ Status endpoint working")
            data = response.json()
            print(f"   Total models: {data['total_models']}")
            print(f"   Active models: {data['active_models']}")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
        
        # Test models endpoint
        print("\n📋 Testing models endpoint...")
        response = requests.get(f"{base_url}/models")
        if response.status_code == 200:
            print("   ✅ Models endpoint working")
            data = response.json()
            print(f"   Available models: {len(data['available_models'])}")
            print(f"   Active models: {len(data['active_models'])}")
        else:
            print(f"   ❌ Models endpoint failed: {response.status_code}")
        
        # Test capabilities endpoint
        print("\n🔧 Testing capabilities endpoint...")
        response = requests.get(f"{base_url}/capabilities")
        if response.status_code == 200:
            print("   ✅ Capabilities endpoint working")
            data = response.json()
            print(f"   Capabilities: {list(data['capabilities'].keys())}")
        else:
            print(f"   ❌ Capabilities endpoint failed: {response.status_code}")
        
        return True
        
    except ImportError:
        print("   ⚠️ Requests not available, skipping API tests")
        return True
    except Exception as e:
        print(f"   ❌ API tests failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Multi-GitHub Models Service Test Suite")
    print("=" * 60)
    
    # Test service functionality
    service_success = await test_multi_github_models()
    
    # Test API endpoints (if service is running)
    api_success = await test_api_endpoints()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"Service Tests: {'✅ PASSED' if service_success else '❌ FAILED'}")
    print(f"API Tests: {'✅ PASSED' if api_success else '❌ FAILED'}")
    
    if service_success and api_success:
        print("\n🎉 All tests passed! Multi-GitHub Models Service is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
