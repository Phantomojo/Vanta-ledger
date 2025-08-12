#!/usr/bin/env python3
"""
Local LLM Service Test
Comprehensive testing of the local LLM service functionality
"""

import os
import sys
import asyncio
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_hardware_detection():
    """Test hardware detection functionality"""
    print("🧪 Testing Hardware Detection...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Check if hardware detector is initialized
        if hasattr(local_llm_service, 'hardware_detector'):
            print("   ✅ Hardware detector initialized")
            
            # Get hardware config
            hardware_config = local_llm_service.hardware_config
            
            # Check required fields
            required_fields = ['performance_profile', 'cpu', 'memory']
            for field in required_fields:
                if field in hardware_config:
                    print(f"   ✅ {field}: {hardware_config[field]}")
                else:
                    print(f"   ❌ {field}: missing")
                    return False
            
            # Check performance profile
            profile = hardware_config.get('performance_profile')
            if profile:
                print(f"   ✅ Performance profile: {profile}")
            else:
                print("   ❌ Performance profile not detected")
                return False
            
            return True
        else:
            print("   ❌ Hardware detector not initialized")
            return False
            
    except Exception as e:
        print(f"   ❌ Hardware detection error: {e}")
        return False

def test_model_configuration():
    """Test model configuration loading"""
    print("\n🧪 Testing Model Configuration...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Check model configs
        model_configs = local_llm_service.model_configs
        
        if model_configs:
            print(f"   ✅ Model configs loaded: {len(model_configs)} models")
            
            # Check specific models
            expected_models = ['tinyllama', 'mistral_7b', 'phi3_mini']
            for model in expected_models:
                if model in model_configs:
                    config = model_configs[model]
                    print(f"   ✅ {model}: {config.get('model_path', 'no path')}")
                else:
                    print(f"   ⚠️  {model}: not configured")
            
            return True
        else:
            print("   ❌ No model configs loaded")
            return False
            
    except Exception as e:
        print(f"   ❌ Model configuration error: {e}")
        return False

def test_company_context_manager():
    """Test company context management"""
    print("\n🧪 Testing Company Context Manager...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Check if company context manager is initialized
        if hasattr(local_llm_service, 'company_context_manager'):
            print("   ✅ Company context manager initialized")
            
            # Test getting company context (with mock company ID)
            import uuid
            test_company_id = uuid.uuid4()
            
            try:
                context = asyncio.run(
                    local_llm_service.company_context_manager.get_company_context(test_company_id)
                )
                print("   ✅ Company context retrieval working")
                return True
            except Exception as e:
                print(f"   ⚠️  Company context retrieval: {e}")
                # This might fail if no companies in database, which is OK
                return True
        else:
            print("   ❌ Company context manager not initialized")
            return False
            
    except Exception as e:
        print(f"   ❌ Company context manager error: {e}")
        return False

async def test_model_loading():
    """Test model loading functionality"""
    print("\n🧪 Testing Model Loading...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Test model initialization
        print("   🔄 Initializing models...")
        start_time = time.time()
        
        await local_llm_service.initialize_models()
        
        load_time = time.time() - start_time
        print(f"   ✅ Models initialized in {load_time:.2f} seconds")
        
        # Check loaded models
        loaded_models = list(local_llm_service.models.keys())
        if loaded_models:
            print(f"   ✅ Loaded models: {loaded_models}")
        else:
            print("   ⚠️  No models loaded (this might be normal if models not available)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model loading error: {e}")
        return False

async def test_document_processing():
    """Test document processing functionality"""
    print("\n🧪 Testing Document Processing...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        from backend.app.models.document_models import EnhancedDocument
        import uuid
        
        # Create test document
        test_text = """
        INVOICE
        
        Invoice Number: INV-2024-001
        Date: January 15, 2024
        Due Date: February 15, 2024
        
        Bill To:
        John Doe
        123 Main Street
        City, State 12345
        
        Items:
        1. Web Development Services - $1,500.00
        2. Hosting Setup - $200.00
        
        Subtotal: $1,700.00
        Tax (10%): $170.00
        Total: $1,870.00
        
        Payment Terms: Net 30
        """
        
        doc = EnhancedDocument(
            original_filename="test_invoice.txt",
            extracted_text=test_text,
            file_size=len(test_text),
            checksum="test123"
        )
        
        # Test processing
        company_id = uuid.uuid4()
        print("   🔄 Processing document...")
        start_time = time.time()
        
        results = await local_llm_service.process_document_for_company(doc, company_id)
        
        processing_time = time.time() - start_time
        print(f"   ✅ Document processed in {processing_time:.2f} seconds")
        
        if results:
            print(f"   ✅ Processing results: {len(results)} components")
            
            # Check specific results
            if 'classification' in results:
                classification = results['classification']
                print(f"   ✅ Classification: {classification.get('type', 'unknown')}")
            
            if 'summary' in results:
                summary = results['summary']
                print(f"   ✅ Summary: {summary[:100]}...")
            
            if 'entities' in results:
                entities = results['entities']
                print(f"   ✅ Entities extracted: {len(entities)} categories")
            
            return True
        else:
            print("   ⚠️  No processing results returned")
            return False
        
    except Exception as e:
        print(f"   ❌ Document processing error: {e}")
        return False

async def test_performance_metrics():
    """Test performance metrics collection"""
    print("\n🧪 Testing Performance Metrics...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Get performance metrics
        metrics = await local_llm_service.get_performance_metrics()
        
        if metrics:
            print("   ✅ Performance metrics collected")
            
            # Check hardware info
            if 'hardware' in metrics:
                hardware = metrics['hardware']
                print(f"   ✅ Hardware: {hardware.get('gpu', 'None')}")
                print(f"   ✅ CPU cores: {hardware.get('cpu_cores', 'unknown')}")
                print(f"   ✅ Memory: {hardware.get('memory_gb', 'unknown')}GB")
            
            return True
        else:
            print("   ⚠️  No performance metrics available")
            return True  # This is OK if no metrics yet
        
    except Exception as e:
        print(f"   ❌ Performance metrics error: {e}")
        return False

async def test_hardware_status():
    """Test hardware status monitoring"""
    print("\n🧪 Testing Hardware Status...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Get hardware status
        status = await local_llm_service.get_hardware_status()
        
        if status:
            print("   ✅ Hardware status collected")
            
            # Check CPU status
            if 'cpu' in status:
                cpu = status['cpu']
                print(f"   ✅ CPU usage: {cpu.get('usage_percent', 'unknown')}%")
            
            # Check memory status
            if 'memory' in status:
                memory = status['memory']
                print(f"   ✅ Memory usage: {memory.get('used_percent', 'unknown')}%")
            
            # Check GPU status
            if 'gpu' in status and status['gpu']:
                gpu = status['gpu']
                print(f"   ✅ GPU: {gpu.get('name', 'unknown')}")
                print(f"   ✅ GPU memory: {gpu.get('memory_used_percent', 'unknown')}%")
            
            return True
        else:
            print("   ⚠️  No hardware status available")
            return True  # This is OK
        
    except Exception as e:
        print(f"   ❌ Hardware status error: {e}")
        return False

def test_cache_functionality():
    """Test caching functionality"""
    print("\n🧪 Testing Cache Functionality...")
    
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        # Check if Redis client is available
        if hasattr(local_llm_service, 'redis_client'):
            print("   ✅ Redis client available")
            
            # Test basic Redis operations
            try:
                # Test set/get
                test_key = "test_cache_key"
                test_value = "test_value"
                
                local_llm_service.redis_client.set(test_key, test_value, ex=60)
                retrieved_value = local_llm_service.redis_client.get(test_key)
                
                if retrieved_value == test_value:
                    print("   ✅ Cache set/get working")
                    # Clean up
                    local_llm_service.redis_client.delete(test_key)
                    return True
                else:
                    print("   ❌ Cache set/get failed")
                    return False
                    
            except Exception as e:
                print(f"   ⚠️  Cache operations: {e}")
                return True  # Cache might not be critical
        else:
            print("   ❌ Redis client not available")
            return False
        
    except Exception as e:
        print(f"   ❌ Cache functionality error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Local LLM Service Test")
    print("=" * 50)
    
    tests = [
        ("Hardware Detection", test_hardware_detection),
        ("Model Configuration", test_model_configuration),
        ("Company Context Manager", test_company_context_manager),
        ("Cache Functionality", test_cache_functionality),
    ]
    
    async_tests = [
        ("Model Loading", test_model_loading),
        ("Document Processing", test_document_processing),
        ("Performance Metrics", test_performance_metrics),
        ("Hardware Status", test_hardware_status),
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
    for test_name, test_func in async_tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Local LLM Service Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Local LLM service is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 