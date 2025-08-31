#!/usr/bin/env python3
"""
Test Local Model for AI Agents

This script helps you test your local model with the AI agent system.
It will detect your model, test memory constraints, and validate the setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from vanta_ledger.agents.llm_integration import LLMConfig, initialize_global_llm, get_global_llm, cleanup_global_llm


def find_local_models() -> list:
    """Find local models on your system."""
    common_paths = [
        "/home/*/models",
        "/home/*/.cache/huggingface/hub",
        "/usr/local/models",
        "/opt/models",
        "~/models",
        "~/.cache/huggingface/hub"
    ]
    
    models = []
    
    for pattern in common_paths:
        expanded_pattern = os.path.expanduser(pattern)
        if "*" in expanded_pattern:
            # Handle glob patterns
            import glob
            for path in glob.glob(expanded_pattern):
                if os.path.isdir(path):
                    models.extend(find_models_in_directory(path))
        else:
            if os.path.isdir(expanded_pattern):
                models.extend(find_models_in_directory(expanded_pattern))
    
    return models


def find_models_in_directory(directory: str) -> list:
    """Find model directories within a given directory."""
    models = []
    
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                # Check if it looks like a model directory
                if has_model_files(item_path):
                    models.append(item_path)
    except PermissionError:
        pass  # Skip directories we can't access
    
    return models


def has_model_files(directory: str) -> bool:
    """Check if a directory contains model files."""
    model_files = ["config.json", "tokenizer.json", "pytorch_model.bin", "model.safetensors"]
    
    for file in model_files:
        if os.path.exists(os.path.join(directory, file)):
            return True
    
    return False


def get_system_memory() -> float:
    """Get available system memory in GB."""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return memory.available / (1024 ** 3)  # Convert to GB
    except ImportError:
        print("⚠️  psutil not available, assuming 8GB memory")
        return 8.0


async def test_model_loading(model_path: str, max_memory_gb: float) -> bool:
    """Test loading a specific model."""
    print(f"\n🧪 Testing model: {model_path}")
    
    config = LLMConfig(
        model_path=model_path,
        max_memory_gb=max_memory_gb,
        use_8bit=True,
        use_4bit=max_memory_gb < 4.0
    )
    
    try:
        success = await initialize_global_llm(config)
        if success:
            llm = await get_global_llm()
            if llm:
                status = llm.get_status()
                print(f"✅ Model loaded successfully!")
                print(f"   Memory usage: {status.get('memory_usage', 'Unknown')} GB")
                print(f"   Available memory: {status.get('available_memory', 'Unknown')} GB")
                
                # Test text generation
                print("\n📝 Testing text generation...")
                response = await llm.generate_text(
                    "Hello! This is a test of the AI agent system. Please respond briefly.",
                    max_tokens=50,
                    temperature=0.7
                )
                
                print(f"✅ Generation successful!")
                print(f"   Response: {response.text}")
                print(f"   Tokens used: {response.tokens_used}")
                print(f"   Generation time: {response.generation_time:.2f}s")
                
                # Test analysis
                print("\n🔍 Testing text analysis...")
                analysis = await llm.analyze_text(
                    "This transaction shows unusual patterns that might indicate fraud.",
                    "fraud"
                )
                
                print(f"✅ Analysis successful!")
                print(f"   Result: {analysis['result']}")
                print(f"   Confidence: {analysis['confidence']}")
                
                await cleanup_global_llm()
                return True
        else:
            print(f"❌ Failed to load model")
            return False
            
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        await cleanup_global_llm()
        return False


async def main():
    """Main test function."""
    print("🤖 Local Model Test for AI Agents")
    print("=" * 50)
    
    # Check system memory
    available_memory = get_system_memory()
    print(f"💾 Available system memory: {available_memory:.2f} GB")
    
    # Find local models
    print("\n🔍 Searching for local models...")
    models = find_local_models()
    
    if not models:
        print("❌ No local models found!")
        print("\n💡 To use your local model:")
        print("1. Make sure your model is in a common location like:")
        print("   - ~/models/")
        print("   - ~/.cache/huggingface/hub/")
        print("   - /home/username/models/")
        print("2. The model directory should contain files like:")
        print("   - config.json")
        print("   - tokenizer.json")
        print("   - pytorch_model.bin or model.safetensors")
        
        # Ask for manual path
        manual_path = input("\n🔧 Enter the path to your model manually (or press Enter to skip): ").strip()
        if manual_path and os.path.exists(manual_path):
            models = [manual_path]
        else:
            return
    else:
        print(f"✅ Found {len(models)} potential models:")
        for i, model in enumerate(models, 1):
            print(f"   {i}. {model}")
    
    # Test each model
    working_models = []
    
    for model_path in models:
        if await test_model_loading(model_path, available_memory):
            working_models.append(model_path)
            break  # Stop after first working model
    
    if working_models:
        print(f"\n🎉 Success! Found {len(working_models)} working model(s):")
        for model in working_models:
            print(f"   ✅ {model}")
        
        print(f"\n📋 Configuration for your model:")
        print(f"```python")
        print(f"from vanta_ledger.agents.llm_integration import LLMConfig")
        print(f"")
        print(f"config = LLMConfig(")
        print(f"    model_path='{working_models[0]}',")
        print(f"    max_memory_gb={available_memory:.1f},")
        print(f"    use_8bit=True,")
        print(f"    use_4bit={available_memory < 4.0},")
        print(f"    max_tokens=512,")
        print(f"    temperature=0.7")
        print(f")")
        print(f"```")
        
        print(f"\n🚀 Your model is ready for AI agent testing!")
        
    else:
        print(f"\n❌ No working models found.")
        print(f"💡 Try:")
        print(f"   1. Check if your model is compatible with transformers")
        print(f"   2. Ensure you have enough memory")
        print(f"   3. Install required dependencies: pip install transformers torch")


if __name__ == "__main__":
    asyncio.run(main())
