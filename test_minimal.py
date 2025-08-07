#!/usr/bin/python3
"""
Minimal test script - no GUI dependencies
"""

import os
import sys

def main():
    print("🔍 Minimal Local LLM Test")
    print("=" * 30)
    
    # Test 1: Check model files
    print("1. Checking model files...")
    tinyllama_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    if os.path.exists(tinyllama_path):
        size_mb = os.path.getsize(tinyllama_path) / (1024**2)
        print(f"   ✅ TinyLlama: {size_mb:.1f}MB")
    else:
        print("   ❌ TinyLlama not found")
    
    # Test 2: Check basic imports
    print("2. Testing imports...")
    
    try:
        import torch
        print(f"   ✅ PyTorch: {torch.__version__}")
    except:
        print("   ❌ PyTorch failed")
    
    try:
        import transformers
        print(f"   ✅ Transformers: {transformers.__version__}")
    except:
        print("   ❌ Transformers failed")
    
    try:
        from llama_cpp import Llama
        print("   ✅ llama-cpp-python")
    except:
        print("   ❌ llama-cpp-python failed")
    
    # Test 3: Simple LLM test
    print("3. Testing LLM loading...")
    try:
        from llama_cpp import Llama
        llm = Llama(
            model_path=tinyllama_path,
            n_ctx=512,
            n_threads=2,
            verbose=False
        )
        response = llm("Hi", max_tokens=10)
        print("   ✅ LLM loaded and working!")
    except Exception as e:
        print(f"   ❌ LLM test failed: {e}")
    
    print("=" * 30)
    print("Test completed!")

if __name__ == "__main__":
    main() 