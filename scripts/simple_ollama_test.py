#!/usr/bin/env python3
"""
Simple Ollama Test

Quick test to verify Ollama integration works.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from vanta_ledger.agents.ollama_integration import OllamaConfig, OllamaIntegration


async def main():
    """Simple test function."""
    print("🤖 Simple Ollama Test")
    print("=" * 30)
    
    # Create config
    config = OllamaConfig(
        model_name="codellama:7b",
        max_tokens=100,
        temperature=0.7,
        timeout=60
    )
    
    # Create integration
    ollama = OllamaIntegration(config)
    
    # Test connection
    print("🔍 Testing connection...")
    connected = await ollama.check_connection()
    if connected:
        print("✅ Connected to Ollama!")
    else:
        print("❌ Failed to connect")
        return
    
    # Test simple generation
    print("\n📝 Testing generation...")
    response = await ollama.generate_text(
        "Say hello in one sentence.",
        max_tokens=20,
        temperature=0.7
    )
    
    print(f"✅ Response: {response.text}")
    print(f"   Tokens: {response.tokens_used}")
    print(f"   Time: {response.generation_time:.2f}s")
    
    # Cleanup
    await ollama.close()
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
