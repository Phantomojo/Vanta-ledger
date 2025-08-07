#!/usr/bin/env python3
"""
Simple LLM Test - No GUI dependencies
"""

import os
import sys
import time

# Disable any GUI-related imports
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ''

def main():
    print("🧪 Simple LLM Test")
    print("=" * 30)
    
    # Test 1: Check model file
    model_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        print("❌ Model not found!")
        return
    
    print(f"✅ Model found: {model_path}")
    
    # Test 2: Import llama-cpp-python
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python imported")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test 3: Load model
    try:
        print("🔄 Loading model...")
        start = time.time()
        
        llm = Llama(
            model_path=model_path,
            n_ctx=256,  # Very small context
            n_threads=2,  # Few threads
            verbose=False
        )
        
        load_time = time.time() - start
        print(f"✅ Model loaded in {load_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return
    
    # Test 4: Generate text
    try:
        print("🔄 Testing generation...")
        start = time.time()
        
        response = llm("Hi", max_tokens=5, temperature=0.7)
        result = response['choices'][0]['text'].strip()
        
        gen_time = time.time() - start
        print(f"✅ Generated in {gen_time:.2f}s: '{result}'")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return
    
    print("\n🎉 LLM test successful!")
    print("Your local LLM system is working!")

if __name__ == "__main__":
    main() 