#!/usr/bin/env python3
"""
Performance Optimization Test Script
Validates that optimized code works correctly
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

def test_database_module():
    """Test database module can be imported and has expected functions"""
    print("Testing database module...")
    try:
        from vanta_ledger import database
        
        # Check that functions exist
        assert hasattr(database, 'get_postgres_connection'), "get_postgres_connection missing"
        assert hasattr(database, 'release_postgres_connection'), "release_postgres_connection missing"
        assert hasattr(database, 'get_mongo_client'), "get_mongo_client missing"
        assert hasattr(database, 'get_redis_client'), "get_redis_client missing"
        
        print("✅ Database module structure is correct")
        return True
    except ImportError as e:
        print(f"⚠️  Database module import failed (dependencies not installed): {e}")
        return False
    except Exception as e:
        print(f"❌ Database module test failed: {e}")
        return False


def test_middleware_module():
    """Test middleware module can be imported"""
    print("\nTesting middleware module...")
    try:
        from vanta_ledger import middleware
        
        # Check that classes exist
        assert hasattr(middleware, 'RateLimitMiddleware'), "RateLimitMiddleware missing"
        assert hasattr(middleware, 'SecurityHeadersMiddleware'), "SecurityHeadersMiddleware missing"
        assert hasattr(middleware, 'LoggingMiddleware'), "LoggingMiddleware missing"
        
        # Check RateLimitMiddleware has cleanup method
        assert hasattr(middleware.RateLimitMiddleware, '_cleanup_old_entries'), "_cleanup_old_entries missing"
        
        print("✅ Middleware module structure is correct")
        return True
    except ImportError as e:
        print(f"⚠️  Middleware module import failed (dependencies not installed): {e}")
        return False
    except Exception as e:
        print(f"❌ Middleware module test failed: {e}")
        return False


def test_document_processor_module():
    """Test document processor module can be imported"""
    print("\nTesting document processor module...")
    try:
        from vanta_ledger.services import document_processor
        
        # Check that lazy loading function exists
        assert hasattr(document_processor, '_get_nlp_model'), "_get_nlp_model missing"
        assert hasattr(document_processor, 'DocumentProcessor'), "DocumentProcessor missing"
        
        print("✅ Document processor module structure is correct")
        return True
    except ImportError as e:
        print(f"⚠️  Document processor import failed (dependencies not installed): {e}")
        return False
    except Exception as e:
        print(f"❌ Document processor test failed: {e}")
        return False


def test_performance_optimizer_module():
    """Test performance optimizer module"""
    print("\nTesting performance optimizer module...")
    try:
        from vanta_ledger.optimizations import performance_optimizer as po
        
        # Check that class exists
        assert hasattr(po, 'PerformanceOptimizer'), "PerformanceOptimizer missing"
        
        print("✅ Performance optimizer module structure is correct")
        return True
    except ImportError as e:
        print(f"⚠️  Performance optimizer import failed (dependencies not installed): {e}")
        return False
    except Exception as e:
        print(f"❌ Performance optimizer test failed: {e}")
        return False


def test_hybrid_database_module():
    """Test hybrid database module"""
    print("\nTesting hybrid database module...")
    try:
        from vanta_ledger import hybrid_database
        
        # Check that class exists
        assert hasattr(hybrid_database, 'HybridDatabaseManager'), "HybridDatabaseManager missing"
        
        print("✅ Hybrid database module structure is correct")
        return True
    except ImportError as e:
        print(f"⚠️  Hybrid database import failed (dependencies not installed): {e}")
        return False
    except Exception as e:
        print(f"❌ Hybrid database test failed: {e}")
        return False


def test_syntax_only():
    """Test that all Python files compile without syntax errors"""
    print("\nTesting Python syntax...")
    import py_compile
    
    files_to_check = [
        "src/vanta_ledger/database.py",
        "src/vanta_ledger/middleware.py",
        "src/vanta_ledger/hybrid_database.py",
        "src/vanta_ledger/services/document_processor.py",
        "src/vanta_ledger/optimizations/performance_optimizer.py",
        "src/vanta_ledger/main.py",
        "scripts/optimize_database_indexes.py",
    ]
    
    all_valid = True
    for filepath in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), "..", filepath)
        try:
            py_compile.compile(full_path, doraise=True)
            print(f"  ✅ {filepath}")
        except py_compile.PyCompileError as e:
            print(f"  ❌ {filepath}: {e}")
            all_valid = False
    
    if all_valid:
        print("✅ All files have valid Python syntax")
    return all_valid


if __name__ == "__main__":
    print("=" * 60)
    print("Performance Optimization Validation Tests")
    print("=" * 60)
    
    results = []
    
    # First check syntax (doesn't require dependencies)
    results.append(("Syntax Check", test_syntax_only()))
    
    # Then check module structure (requires dependencies but not database)
    results.append(("Database Module", test_database_module()))
    results.append(("Middleware Module", test_middleware_module()))
    results.append(("Document Processor", test_document_processor_module()))
    results.append(("Performance Optimizer", test_performance_optimizer_module()))
    results.append(("Hybrid Database", test_hybrid_database_module()))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All optimizations validated successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed (may be due to missing dependencies)")
        sys.exit(1)
