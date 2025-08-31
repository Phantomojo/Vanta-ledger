#!/usr/bin/env python3
"""
Test Ollama for AI Agents

This script tests the Ollama integration with your local models.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from vanta_ledger.agents.ollama_integration import OllamaConfig, initialize_global_ollama, get_global_ollama, cleanup_global_ollama


async def test_ollama_connection():
    """Test Ollama connection and list models."""
    print("🔍 Testing Ollama connection...")
    
    # Test with CodeLlama:7b
    config = OllamaConfig(
        model_name="codellama:7b",
        max_tokens=256,
        temperature=0.7
    )
    
    success = await initialize_global_ollama(config)
    if success:
        print("✅ Ollama connection successful!")
        return True
    else:
        print("❌ Failed to connect to Ollama")
        return False


async def test_text_generation():
    """Test text generation with Ollama."""
    print("\n📝 Testing text generation...")
    
    ollama = await get_global_ollama()
    if not ollama:
        print("❌ Ollama not initialized")
        return False
    
    # Test basic generation
    response = await ollama.generate_text(
        "Hello! This is a test of the AI agent system. Please respond briefly.",
        max_tokens=50,
        temperature=0.7
    )
    
    print(f"✅ Generation successful!")
    print(f"   Response: {response.text}")
    print(f"   Tokens used: {response.tokens_used}")
    print(f"   Generation time: {response.generation_time:.2f}s")
    
    return True


async def test_text_analysis():
    """Test text analysis with Ollama."""
    print("\n🔍 Testing text analysis...")
    
    ollama = await get_global_ollama()
    if not ollama:
        print("❌ Ollama not initialized")
        return False
    
    # Test fraud analysis
    analysis = await ollama.analyze_text(
        "This transaction shows unusual patterns that might indicate fraud.",
        "fraud"
    )
    
    print(f"✅ Analysis successful!")
    print(f"   Result: {analysis['result']}")
    print(f"   Confidence: {analysis['confidence']}")
    print(f"   Tokens used: {analysis['tokens_used']}")
    print(f"   Generation time: {analysis['generation_time']:.2f}s")
    
    return True


async def test_compliance_analysis():
    """Test compliance analysis with Ollama."""
    print("\n📋 Testing compliance analysis...")
    
    ollama = await get_global_ollama()
    if not ollama:
        print("❌ Ollama not initialized")
        return False
    
    # Test compliance analysis
    analysis = await ollama.analyze_text(
        "Company XYZ reported revenue of $1M but expenses were only $100K, which seems unusual.",
        "compliance"
    )
    
    print(f"✅ Compliance analysis successful!")
    print(f"   Result: {analysis['result']}")
    print(f"   Confidence: {analysis['confidence']}")
    
    return True


async def main():
    """Main test function."""
    print("🤖 Ollama Test for AI Agents")
    print("=" * 50)
    
    try:
        # Test connection
        if not await test_ollama_connection():
            print("\n❌ Cannot proceed without Ollama connection")
            print("💡 Make sure Ollama is running: ollama serve")
            return
        
        # Test text generation
        if not await test_text_generation():
            print("\n❌ Text generation failed")
            return
        
        # Test text analysis
        if not await test_text_analysis():
            print("\n❌ Text analysis failed")
            return
        
        # Test compliance analysis
        if not await test_compliance_analysis():
            print("\n❌ Compliance analysis failed")
            return
        
        print(f"\n🎉 All tests passed! Your CodeLlama:7b is ready for AI agents!")
        
        print(f"\n📋 Configuration for your agents:")
        print(f"```python")
        print(f"from vanta_ledger.agents.ollama_integration import OllamaConfig")
        print(f"")
        print(f"config = OllamaConfig(")
        print(f"    model_name='codellama:7b',")
        print(f"    max_tokens=512,")
        print(f"    temperature=0.7")
        print(f")")
        print(f"```")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    finally:
        # Cleanup
        await cleanup_global_ollama()


if __name__ == "__main__":
    asyncio.run(main())
