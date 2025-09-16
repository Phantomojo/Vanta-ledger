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
import logging
logger = logging.getLogger(__name__)


async def main():
    """Simple test function."""
    logger.info("🤖 Simple Ollama Test")
    logger.info("=")
    
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
    logger.info("🔍 Testing connection...")
    connected = await ollama.check_connection()
    if connected:
        logger.info("✅ Connected to Ollama!")
    else:
        logger.error("❌ Failed to connect")
        return
    
    # Test simple generation
    logger.info("\n📝 Testing generation...")
    response = await ollama.generate_text(
        "Say hello in one sentence.",
        max_tokens=20,
        temperature=0.7
    )
    
    logger.info(f"✅ Response: {response.text}")
    logger.info(f"   Tokens: {response.tokens_used}")
    logger.info(f"   Time: {response.generation_time:.2f}s")
    
    # Cleanup
    await ollama.close()
    logger.info("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
