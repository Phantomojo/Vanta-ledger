#!/usr/bin/env python3
"""
System Health Checker
Comprehensive validation of the Vanta Ledger system with Local LLM
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

def check_environment():
    """Check environment setup"""
    print("🔍 Checking Environment Setup...")
    
    health = {
        "environment": {},
        "dependencies": {},
        "models": {},
        "hardware": {},
        "databases": {},
        "overall": "unknown"
    }
    
    # Check Python version
    python_version = sys.version_info
    health["environment"]["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    # Check working directory
    health["environment"]["working_directory"] = str(Path.cwd())
    
    # Check if we're in the right directory
    if Path("backend").exists() and Path("models").exists():
        health["environment"]["project_structure"] = "correct"
    else:
        health["environment"]["project_structure"] = "incorrect"
    
    print(f"   ✅ Python: {health['environment']['python_version']}")
    print(f"   ✅ Working Directory: {health['environment']['working_directory']}")
    print(f"   ✅ Project Structure: {health['environment']['project_structure']}")
    
    return health

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n📦 Checking Dependencies...")
    
    dependencies = {
        "torch": "PyTorch for ML",
        "transformers": "Hugging Face Transformers",
        "llama_cpp": "llama-cpp-python",
        "redis": "Redis client",
        "pymongo": "MongoDB client",
        "fastapi": "FastAPI framework",
        "uvicorn": "ASGI server",
        "psutil": "System monitoring",
        "GPUtil": "GPU monitoring"
    }
    
    health = {}
    
    for dep, description in dependencies.items():
        try:
            if dep == "llama_cpp":
                from llama_cpp import Llama
            else:
                __import__(dep)
            health[dep] = "installed"
            print(f"   ✅ {dep}: {description}")
        except ImportError:
            health[dep] = "missing"
            print(f"   ❌ {dep}: {description} - MISSING")
    
    return health

def check_models():
    """Check model files"""
    print("\n🤖 Checking Model Files...")
    
    health = {}
    
    # Check models directory
    models_dir = Path("models")
    if models_dir.exists():
        health["models_directory"] = "exists"
        print(f"   ✅ Models directory: {models_dir}")
        
        # Check TinyLlama
        tinyllama_path = models_dir / "tinyllama" / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        if tinyllama_path.exists():
            size_mb = tinyllama_path.stat().st_size / (1024**2)
            health["tinyllama"] = {
                "status": "ready",
                "size_mb": round(size_mb, 1)
            }
            print(f"   ✅ TinyLlama: {size_mb:.1f}MB")
        else:
            health["tinyllama"] = {"status": "missing"}
            print("   ❌ TinyLlama: missing")
        
        # Check Mistral
        mistral_dir = models_dir / "mistral"
        if mistral_dir.exists():
            files = list(mistral_dir.glob("*"))
            if files:
                total_size = sum(f.stat().st_size for f in files) / (1024**2)
                health["mistral"] = {
                    "status": "partial",
                    "files": len(files),
                    "size_mb": round(total_size, 1)
                }
                print(f"   ⚠️  Mistral: {len(files)} files, {total_size:.1f}MB")
            else:
                health["mistral"] = {"status": "empty"}
                print("   ❌ Mistral: empty directory")
        else:
            health["mistral"] = {"status": "missing"}
            print("   ❌ Mistral: missing")
    else:
        health["models_directory"] = "missing"
        print("   ❌ Models directory: missing")
    
    return health

def check_hardware():
    """Check hardware configuration"""
    print("\n🖥️  Checking Hardware...")
    
    health = {}
    
    # Check CPU
    try:
        import psutil
        cpu_cores = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        health["cpu"] = {
            "cores": cpu_cores,
            "usage_percent": cpu_percent,
            "memory_gb": round(memory.total / (1024**3), 1)
        }
        
        print(f"   ✅ CPU: {cpu_cores} cores, {cpu_percent}% usage")
        print(f"   ✅ Memory: {health['cpu']['memory_gb']}GB total")
        
    except Exception as e:
        health["cpu"] = {"error": str(e)}
        print(f"   ❌ CPU check failed: {e}")
    
    # Check GPU
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(', ')
            gpu_name = gpu_info[0]
            gpu_memory_total = int(gpu_info[1])
            gpu_memory_used = int(gpu_info[2])
            gpu_memory_percent = round((gpu_memory_used / gpu_memory_total) * 100, 1)
            
            health["gpu"] = {
                "name": gpu_name,
                "memory_total_mb": gpu_memory_total,
                "memory_used_mb": gpu_memory_used,
                "memory_usage_percent": gpu_memory_percent
            }
            
            print(f"   ✅ GPU: {gpu_name}")
            print(f"   ✅ GPU Memory: {gpu_memory_used}MB / {gpu_memory_total}MB ({gpu_memory_percent}%)")
        else:
            health["gpu"] = {"status": "not_detected"}
            print("   ❌ GPU: not detected")
            
    except Exception as e:
        health["gpu"] = {"error": str(e)}
        print(f"   ❌ GPU check failed: {e}")
    
    return health

def check_databases():
    """Check database connections"""
    print("\n🗄️  Checking Database Connections...")
    
    health = {}
    
    # Check MongoDB
    try:
        from backend.app.config import settings
        import pymongo
        
        mongo_client = pymongo.MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
        health["mongodb"] = "connected"
        print("   ✅ MongoDB: connected")
        mongo_client.close()
        
    except Exception as e:
        health["mongodb"] = f"error: {str(e)}"
        print(f"   ❌ MongoDB: {e}")
    
    # Check Redis
    try:
        from backend.app.config import settings
        import redis
        
        redis_client = redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)
        redis_client.ping()
        health["redis"] = "connected"
        print("   ✅ Redis: connected")
        redis_client.close()
        
    except Exception as e:
        health["redis"] = f"error: {str(e)}"
        print(f"   ❌ Redis: {e}")
    
    return health

def check_services():
    """Check service initialization"""
    print("\n⚙️  Checking Services...")
    
    health = {}
    
    # Check Local LLM Service
    try:
        from backend.app.services.local_llm_service import local_llm_service
        
        if hasattr(local_llm_service, 'hardware_detector'):
            health["local_llm_service"] = "initialized"
            print("   ✅ Local LLM Service: initialized")
        else:
            health["local_llm_service"] = "not_initialized"
            print("   ❌ Local LLM Service: not initialized")
            
    except Exception as e:
        health["local_llm_service"] = f"error: {str(e)}"
        print(f"   ❌ Local LLM Service: {e}")
    
    # Check Enhanced Document Service
    try:
        from backend.app.services.enhanced_document_service import enhanced_document_service
        
        if hasattr(enhanced_document_service, 'documents'):
            health["enhanced_document_service"] = "initialized"
            print("   ✅ Enhanced Document Service: initialized")
        else:
            health["enhanced_document_service"] = "not_initialized"
            print("   ❌ Enhanced Document Service: not initialized")
            
    except Exception as e:
        health["enhanced_document_service"] = f"error: {str(e)}"
        print(f"   ❌ Enhanced Document Service: {e}")
    
    return health

def generate_report(health_data):
    """Generate health report"""
    print("\n📊 Generating Health Report...")
    
    # Calculate overall health
    all_checks = []
    
    # Check environment
    if health_data["environment"]["project_structure"] == "correct":
        all_checks.append(True)
    else:
        all_checks.append(False)
    
    # Check dependencies
    deps_ok = all(health_data["dependencies"].get(dep) == "installed" 
                  for dep in ["torch", "transformers", "llama_cpp", "redis", "pymongo"])
    all_checks.append(deps_ok)
    
    # Check models
    models_ok = health_data["models"].get("tinyllama", {}).get("status") == "ready"
    all_checks.append(models_ok)
    
    # Check hardware
    hardware_ok = "error" not in health_data["hardware"].get("cpu", {})
    all_checks.append(hardware_ok)
    
    # Check databases
    db_ok = (health_data["databases"].get("mongodb") == "connected" and 
             health_data["databases"].get("redis") == "connected")
    all_checks.append(db_ok)
    
    # Check services
    services_ok = (health_data["services"].get("local_llm_service") == "initialized" and
                   health_data["services"].get("enhanced_document_service") == "initialized")
    all_checks.append(services_ok)
    
    # Overall health
    if all(all_checks):
        health_data["overall"] = "healthy"
        print("🎉 Overall Health: HEALTHY - All systems operational!")
    else:
        health_data["overall"] = "unhealthy"
        print("⚠️  Overall Health: UNHEALTHY - Some issues detected")
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"health_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(health_data, f, indent=2, default=str)
    
    print(f"📄 Health report saved to: {report_file}")
    
    return health_data

def main():
    """Main health check function"""
    print("🏥 Vanta Ledger System Health Check")
    print("=" * 50)
    
    # Run all health checks
    health_data = {
        "environment": check_environment(),
        "dependencies": check_dependencies(),
        "models": check_models(),
        "hardware": check_hardware(),
        "databases": check_databases(),
        "services": check_services(),
        "overall": "unknown"
    }
    
    # Generate report
    final_report = generate_report(health_data)
    
    print("\n" + "=" * 50)
    print("🏥 Health Check Complete!")
    
    if final_report["overall"] == "healthy":
        print("✅ System is ready for testing and operation!")
        return True
    else:
        print("⚠️  System has issues that need to be addressed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 