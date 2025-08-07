#!/usr/bin/env python3
"""
Simple test script for Local LLM Service
Tests basic imports and functionality without Qt conflicts
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
        print(f"   Version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
    
    try:
        import transformers
        print("✅ Transformers imported successfully")
        print(f"   Version: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers import failed: {e}")
    
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python imported successfully")
    except ImportError as e:
        print(f"❌ llama-cpp-python import failed: {e}")
    
    try:
        import redis
        print("✅ Redis imported successfully")
    except ImportError as e:
        print(f"❌ Redis import failed: {e}")
    
    try:
        import pymongo
        print("✅ PyMongo imported successfully")
    except ImportError as e:
        print(f"❌ PyMongo import failed: {e}")

def test_hardware_detection():
    """Test hardware detection without Qt conflicts"""
    print("\nTesting hardware detection...")
    
    try:
        # Use subprocess to avoid Qt conflicts
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(', ')
            print(f"✅ GPU detected: {gpu_info[0]}")
            print(f"   Memory: {gpu_info[1]}MB")
        else:
            print("⚠️  No GPU detected or nvidia-smi not available")
    except Exception as e:
        print(f"❌ GPU detection failed: {e}")
    
    try:
        import psutil
        print(f"✅ CPU cores: {psutil.cpu_count()}")
        print(f"   Memory: {psutil.virtual_memory().total / (1024**3):.1f}GB")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")

def test_model_files():
    """Test if model files exist"""
    print("\nTesting model files...")
    
    models_dir = "models"
    if os.path.exists(models_dir):
        print(f"✅ Models directory exists: {models_dir}")
        
        # Check TinyLlama
        tinyllama_path = os.path.join(models_dir, "tinyllama", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
        if os.path.exists(tinyllama_path):
            size_mb = os.path.getsize(tinyllama_path) / (1024**2)
            print(f"✅ TinyLlama model found: {size_mb:.1f}MB")
        else:
            print("❌ TinyLlama model not found")
        
        # Check Mistral
        mistral_path = os.path.join(models_dir, "mistral")
        if os.path.exists(mistral_path):
            mistral_files = os.listdir(mistral_path)
            if mistral_files:
                print(f"✅ Mistral directory has files: {len(mistral_files)} files")
                for file in mistral_files:
                    file_path = os.path.join(mistral_path, file)
                    size_mb = os.path.getsize(file_path) / (1024**2)
                    print(f"   - {file}: {size_mb:.1f}MB")
            else:
                print("❌ Mistral directory is empty")
        else:
            print("❌ Mistral directory not found")
    else:
        print("❌ Models directory not found")

def test_simple_llm_load():
    """Test simple LLM loading without Qt conflicts"""
    print("\nTesting simple LLM loading...")
    
    try:
        from llama_cpp import Llama
        
        # Test with TinyLlama
        model_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        if os.path.exists(model_path):
            print("Loading TinyLlama model...")
            llm = Llama(
                model_path=model_path,
                n_ctx=1024,
                n_threads=4,
                verbose=False
            )
            
            # Simple test
            response = llm("Hello, how are you?", max_tokens=20, temperature=0.7)
            print("✅ TinyLlama loaded and tested successfully!")
            print(f"   Response: {response['choices'][0]['text'].strip()}")
        else:
            print("❌ TinyLlama model file not found")
            
    except Exception as e:
        print(f"❌ LLM loading failed: {e}")

if __name__ == "__main__":
    print("🔍 Local LLM Service - Basic Test")
    print("=" * 50)
    
    test_basic_imports()
    test_hardware_detection()
    test_model_files()
    test_simple_llm_load()
    
    print("\n" + "=" * 50)
    print("Test completed!") 