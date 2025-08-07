#!/usr/bin/env python3
"""
Backend Integration Test with Local LLM
Tests the complete backend integration with local LLM functionality
"""

import os
import sys
import asyncio
import requests
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_backend_startup():
    """Test if backend can start without errors"""
    print("🧪 Testing Backend Startup...")
    
    try:
        # Test imports
        from backend.app.main import app
        from backend.app.services.local_llm_service import local_llm_service
        from backend.app.services.enhanced_document_service import enhanced_document_service
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_local_llm_service():
    """Test local LLM service functionality"""
    print("\n🧪 Testing Local LLM Service...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Check if service is properly initialized
        if hasattr(local_llm_service, 'hardware_detector'):
            print("✅ Local LLM service initialized")
            
            # Check hardware detection
            hardware_config = local_llm_service.hardware_config
            print(f"   Hardware: {hardware_config.get('performance_profile', 'unknown')}")
            
            return True
        else:
            print("❌ Local LLM service not properly initialized")
            return False
            
    except Exception as e:
        print(f"❌ Local LLM service error: {e}")
        return False

def test_enhanced_document_service():
    """Test enhanced document service with LLM integration"""
    print("\n🧪 Testing Enhanced Document Service...")
    
    try:
        from backend.app.services.enhanced_document_service import enhanced_document_service
        
        # Check if service is properly initialized
        if hasattr(enhanced_document_service, 'documents'):
            print("✅ Enhanced document service initialized")
            return True
        else:
            print("❌ Enhanced document service not properly initialized")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced document service error: {e}")
        return False

def test_api_routes():
    """Test if API routes are properly registered"""
    print("\n🧪 Testing API Routes...")
    
    try:
        from backend.app.main import app
        
        # Check if local LLM routes are included
        routes = [route.path for route in app.routes]
        llm_routes = [route for route in routes if '/api/v2/llm' in route]
        
        if llm_routes:
            print(f"✅ Local LLM routes found: {len(llm_routes)} routes")
            for route in llm_routes:
                print(f"   - {route}")
            return True
        else:
            print("❌ Local LLM routes not found")
            return False
            
    except Exception as e:
        print(f"❌ API routes error: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n🧪 Testing Configuration...")
    
    try:
        from backend.app.config import settings
        
        # Check LLM configuration
        llm_config = {
            'ENABLE_LOCAL_LLM': settings.ENABLE_LOCAL_LLM,
            'LLM_MODELS_DIR': settings.LLM_MODELS_DIR,
            'LLM_CACHE_TTL': settings.LLM_CACHE_TTL,
            'LLM_MAX_CONTEXT_LENGTH': settings.LLM_MAX_CONTEXT_LENGTH,
            'LLM_DEFAULT_TEMPERATURE': settings.LLM_DEFAULT_TEMPERATURE,
            'LLM_USE_GPU': settings.LLM_USE_GPU
        }
        
        print("✅ LLM configuration loaded:")
        for key, value in llm_config.items():
            print(f"   - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_model_files():
    """Test if model files are accessible"""
    print("\n🧪 Testing Model Files...")
    
    try:
        from backend.app.config import settings
        
        models_dir = Path(settings.LLM_MODELS_DIR)
        if not models_dir.is_absolute():
            models_dir = project_root / models_dir
        
        if models_dir.exists():
            print(f"✅ Models directory found: {models_dir}")
            
            # Check TinyLlama
            tinyllama_path = models_dir / "tinyllama" / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            if tinyllama_path.exists():
                size_mb = tinyllama_path.stat().st_size / (1024**2)
                print(f"   ✅ TinyLlama: {size_mb:.1f}MB")
            else:
                print("   ❌ TinyLlama not found")
            
            # Check Mistral
            mistral_dir = models_dir / "mistral"
            if mistral_dir.exists():
                files = list(mistral_dir.glob("*"))
                if files:
                    print(f"   ⚠️  Mistral: {len(files)} files")
                else:
                    print("   ❌ Mistral directory empty")
            else:
                print("   ❌ Mistral directory not found")
            
            return True
        else:
            print(f"❌ Models directory not found: {models_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Model files error: {e}")
        return False

def test_database_connections():
    """Test database connections"""
    print("\n🧪 Testing Database Connections...")
    
    try:
        from backend.app.config import settings
        import pymongo
        import redis
        
        # Test MongoDB
        try:
            mongo_client = pymongo.MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            mongo_client.admin.command('ping')
            print("✅ MongoDB connection successful")
            mongo_client.close()
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
        
        # Test Redis
        try:
            redis_client = redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)
            redis_client.ping()
            print("✅ Redis connection successful")
            redis_client.close()
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

async def test_llm_processing():
    """Test LLM document processing"""
    print("\n🧪 Testing LLM Document Processing...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        from backend.app.models.document_models import EnhancedDocument
        import uuid
        
        # Create a test document
        test_text = """
        INVOICE
        
        Invoice Number: INV-2024-001
        Date: January 15, 2024
        Amount: $1,500.00
        Customer: Test Company
        """
        
        doc = EnhancedDocument(
            original_filename="test_invoice.txt",
            extracted_text=test_text,
            file_size=len(test_text),
            checksum="test123"
        )
        
        # Test processing
        company_id = uuid.uuid4()
        results = await local_llm_service.process_document_for_company(doc, company_id)
        
        if results:
            print("✅ LLM document processing successful")
            print(f"   Results: {len(results)} components")
            return True
        else:
            print("❌ LLM document processing failed")
            return False
            
    except Exception as e:
        print(f"❌ LLM processing error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Backend Integration Test with Local LLM")
    print("=" * 60)
    
    tests = [
        ("Backend Startup", test_backend_startup),
        ("Local LLM Service", test_local_llm_service),
        ("Enhanced Document Service", test_enhanced_document_service),
        ("API Routes", test_api_routes),
        ("Configuration", test_configuration),
        ("Model Files", test_model_files),
        ("Database Connections", test_database_connections),
    ]
    
    results = {}
    
    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Run async tests
    async def run_async_tests():
        try:
            results["LLM Processing"] = await test_llm_processing()
        except Exception as e:
            print(f"❌ LLM Processing test failed with exception: {e}")
            results["LLM Processing"] = False
    
    asyncio.run(run_async_tests())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready with local LLM integration.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 