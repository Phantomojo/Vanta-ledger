#!/usr/bin/env python3
"""
Test Local LLM Integration
Simple test to verify hardware detection and basic functionality
"""

import sys
import os

# Add the virtual environment site-packages to the path
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.12', 'site-packages')
sys.path.insert(0, venv_path)

def test_hardware_detection():
    """Test hardware detection"""
    print("🔍 Testing Hardware Detection...")
    try:
        from backend.app.services.llm.hardware_detector import HardwareDetector
        hd = HardwareDetector()
        result = hd.detect_hardware()
        
        print(f"✅ Hardware Detection Successful!")
        print(f"   GPU: {result.get('gpu', {}).get('name', 'None')}")
        print(f"   Performance Profile: {result.get('performance_profile', 'unknown')}")
        print(f"   CPU Cores: {result.get('cpu', {}).get('cores', 'unknown')}")
        print(f"   Memory: {result.get('memory', {}).get('total', 0) / (1024**3):.1f} GB")
        
        return True
    except Exception as e:
        print(f"❌ Hardware Detection Failed: {str(e)}")
        return False

def test_company_context():
    """Test company context manager"""
    print("\n🏢 Testing Company Context Manager...")
    try:
        from backend.app.services.llm.company_context import CompanyContextManager
        from pymongo import MongoClient
        
        # Mock database connection
        mock_db = type('MockDB', (), {})()
        mock_db.companies = type('MockCollection', (), {
            'find_one': lambda x: {
                '_id': 'test-company-id',
                'name': 'Test Company',
                'industry': 'Technology',
                'currency': 'KES',
                'tax_rate': 16.0
            }
        })()
        
        ccm = CompanyContextManager(mock_db)
        print("✅ Company Context Manager Created Successfully!")
        return True
    except Exception as e:
        print(f"❌ Company Context Manager Failed: {str(e)}")
        return False

def test_basic_imports():
    """Test basic imports"""
    print("\n📦 Testing Basic Imports...")
    try:
        import redis
        import pymongo
        import psutil
        from GPUtil import getGPUs
        print("✅ All Basic Imports Successful!")
        return True
    except Exception as e:
        print(f"❌ Basic Imports Failed: {str(e)}")
        return False

def test_gpu_detection():
    """Test GPU detection specifically"""
    print("\n🎮 Testing GPU Detection...")
    try:
        from GPUtil import getGPUs
        gpus = getGPUs()
        if gpus:
            gpu = gpus[0]
            print(f"✅ GPU Detected: {gpu.name}")
            print(f"   Memory: {gpu.memoryTotal}MB")
            print(f"   Temperature: {gpu.temperature}°C")
            print(f"   Load: {gpu.load * 100 if gpu.load else 0:.1f}%")
            return True
        else:
            print("⚠️  No GPU detected")
            return False
    except Exception as e:
        print(f"❌ GPU Detection Failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧠 Local LLM Integration Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("GPU Detection", test_gpu_detection),
        ("Hardware Detection", test_hardware_detection),
        ("Company Context", test_company_context),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Failed with Exception: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Local LLM integration is ready!")
        print("\n🚀 Next steps:")
        print("1. Download models: python scripts/download_llm_models.py")
        print("2. Start backend: cd backend && uvicorn app.main:app --reload")
        print("3. Test API: curl http://localhost:8000/api/v2/llm/health")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 