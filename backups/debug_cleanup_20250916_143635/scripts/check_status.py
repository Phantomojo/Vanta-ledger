#!/usr/bin/env python3
"""
Status check for Local LLM setup
"""

import os
import json

def check_status():
    status = {
        "models": {},
        "dependencies": {},
        "hardware": {},
        "overall": "unknown"
    }
    
    # Check models
    print("📁 Checking models...")
    
    # TinyLlama
    tinyllama_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    if os.path.exists(tinyllama_path):
        size_mb = os.path.getsize(tinyllama_path) / (1024**2)
        status["models"]["tinyllama"] = {
            "status": "ready",
            "size_mb": round(size_mb, 1)
        }
        print(f"   ✅ TinyLlama: {size_mb:.1f}MB")
    else:
        status["models"]["tinyllama"] = {"status": "missing"}
        print("   ❌ TinyLlama: missing")
    
    # Mistral
    mistral_path = "models/mistral"
    if os.path.exists(mistral_path):
        files = os.listdir(mistral_path)
        if files:
            total_size = sum(os.path.getsize(os.path.join(mistral_path, f)) for f in files)
            size_mb = total_size / (1024**2)
            status["models"]["mistral"] = {
                "status": "partial",
                "files": len(files),
                "size_mb": round(size_mb, 1)
            }
            print(f"   ⚠️  Mistral: {len(files)} files, {size_mb:.1f}MB")
        else:
            status["models"]["mistral"] = {"status": "empty"}
            print("   ❌ Mistral: empty directory")
    else:
        status["models"]["mistral"] = {"status": "missing"}
        print("   ❌ Mistral: missing")
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    
    deps = ["torch", "transformers", "llama_cpp", "redis", "pymongo"]
    for dep in deps:
        try:
            if dep == "llama_cpp":
                from llama_cpp import Llama
            else:
                __import__(dep)
            status["dependencies"][dep] = "installed"
            print(f"   ✅ {dep}")
        except ImportError:
            status["dependencies"][dep] = "missing"
            print(f"   ❌ {dep}")
    
    # Check hardware
    print("\n🖥️  Checking hardware...")
    
    try:
        import psutil
        cpu_cores = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        status["hardware"]["cpu_cores"] = cpu_cores
        status["hardware"]["memory_gb"] = round(memory_gb, 1)
        print(f"   ✅ CPU: {cpu_cores} cores")
        print(f"   ✅ Memory: {memory_gb:.1f}GB")
    except:
        status["hardware"]["cpu_cores"] = "unknown"
        status["hardware"]["memory_gb"] = "unknown"
        print("   ❌ Hardware info unavailable")
    
    # GPU check
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(', ')
            status["hardware"]["gpu"] = {
                "name": gpu_info[0],
                "memory_mb": int(gpu_info[1])
            }
            print(f"   ✅ GPU: {gpu_info[0]} ({gpu_info[1]}MB)")
        else:
            status["hardware"]["gpu"] = "none"
            print("   ❌ GPU: not detected")
    except:
        status["hardware"]["gpu"] = "unknown"
        print("   ❌ GPU: check failed")
    
    # Overall status
    ready_models = sum(1 for m in status["models"].values() if m.get("status") == "ready")
    installed_deps = sum(1 for d in status["dependencies"].values() if d == "installed")
    
    if ready_models >= 1 and installed_deps >= 4:
        status["overall"] = "ready"
        print("\n🎉 System is ready for local LLM processing!")
    elif ready_models >= 1:
        status["overall"] = "partial"
        print("\n⚠️  System partially ready - missing some dependencies")
    else:
        status["overall"] = "not_ready"
        print("\n❌ System not ready - missing models and/or dependencies")
    
    return status

if __name__ == "__main__":
    status = check_status()
    
    # Save status to file
    with open("llm_status.json", "w") as f:
        json.dump(status, f, indent=2)
    
    print(f"\n📄 Status saved to llm_status.json")
    print(f"Overall status: {status['overall']}") 