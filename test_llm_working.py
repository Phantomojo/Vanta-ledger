#!/usr/bin/env python3
"""
Test Local LLM with TinyLlama
Simple test to verify the system is working
"""

import os
import sys
import time

def test_tinyllama():
    """Test TinyLlama model"""
    print("🧪 Testing TinyLlama Local LLM")
    print("=" * 40)
    
    # Check model file
    model_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        print("❌ TinyLlama model not found!")
        return False
    
    print(f"✅ Model found: {model_path}")
    
    try:
        from llama_cpp import Llama
        
        print("🔄 Loading model...")
        start_time = time.time()
        
        # Load model with conservative settings
        llm = Llama(
            model_path=model_path,
            n_ctx=512,  # Small context for testing
            n_threads=4,  # Use 4 threads
            n_gpu_layers=0,  # CPU only for testing
            verbose=False
        )
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Test simple generation
        print("🔄 Testing generation...")
        start_time = time.time()
        
        response = llm(
            "Hello! How are you today?",
            max_tokens=20,
            temperature=0.7,
            stop=["\n"]
        )
        
        gen_time = time.time() - start_time
        result = response['choices'][0]['text'].strip()
        
        print(f"✅ Generation completed in {gen_time:.2f} seconds")
        print(f"📝 Response: '{result}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_document_processing():
    """Test basic document processing"""
    print("\n📄 Testing Document Processing")
    print("=" * 40)
    
    try:
        # Test with a simple text
        test_text = """
        Invoice #12345
        Date: 2024-01-15
        Amount: $150.00
        Customer: John Doe
        """
        
        from llama_cpp import Llama
        
        model_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        llm = Llama(
            model_path=model_path,
            n_ctx=512,
            n_threads=4,
            verbose=False
        )
        
        # Test document classification
        prompt = f"""
        Classify this document:
        {test_text}
        
        Options: invoice, receipt, contract, other
        Answer with just the category:
        """
        
        response = llm(prompt, max_tokens=10, temperature=0.3)
        classification = response['choices'][0]['text'].strip()
        
        print(f"✅ Document classified as: {classification}")
        
        # Test entity extraction
        prompt = f"""
        Extract key information from this document:
        {test_text}
        
        Format: Invoice Number, Date, Amount, Customer
        """
        
        response = llm(prompt, max_tokens=50, temperature=0.3)
        extraction = response['choices'][0]['text'].strip()
        
        print(f"✅ Entity extraction: {extraction}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document processing error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Local LLM System Test")
    print("=" * 50)
    
    # Test 1: Basic model loading and generation
    test1_success = test_tinyllama()
    
    # Test 2: Document processing
    test2_success = test_document_processing()
    
    print("\n" + "=" * 50)
    if test1_success and test2_success:
        print("🎉 All tests passed! Your local LLM system is working!")
        print("💡 You can now use it for document processing and analysis.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    print("=" * 50) 