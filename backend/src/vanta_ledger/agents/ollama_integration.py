"""
Ollama Integration Module

Provides integration with Ollama for AI agent operations.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OllamaConfig(BaseModel):
    """Configuration for Ollama integration."""
    model_name: str = Field(..., description="Name of the Ollama model")
    base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    max_tokens: int = Field(default=512, description="Maximum tokens for generation")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")


class OllamaResponse(BaseModel):
    """Response from Ollama API."""
    text: str = Field(..., description="Generated text")
    tokens_used: int = Field(..., description="Number of tokens used")
    generation_time: float = Field(..., description="Generation time in seconds")
    model_name: str = Field(..., description="Model used for generation")


class OllamaIntegration:
    """Integration with Ollama for AI agent operations."""

    def __init__(self, config: OllamaConfig):
        """Initialize the Ollama integration."""
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._is_connected = False
        logger.info(f"Initialized Ollama Integration with model: {config.model_name}")

    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.config.base_url}/api/tags") as response:
                if response.status == 200:
                    self._is_connected = True
                    logger.info("Ollama connection established")
                    return True
                else:
                    logger.error(f"Ollama API returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            self._is_connected = False
            return False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> OllamaResponse:
        """Generate text using Ollama."""
        if not self._is_connected:
            connected = await self.check_connection()
            if not connected:
                return OllamaResponse(
                    text="Error: Ollama not accessible",
                    tokens_used=0,
                    generation_time=0.0,
                    model_name=self.config.model_name
                )

        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens or self.config.max_tokens,
                    "temperature": temperature or self.config.temperature
                }
            }
            
            async with session.post(
                f"{self.config.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    generated_text = data.get("response", "")
                    tokens_used = data.get("eval_count", 0)
                    generation_time = time.time() - start_time
                    
                    return OllamaResponse(
                        text=generated_text,
                        tokens_used=tokens_used,
                        generation_time=generation_time,
                        model_name=self.config.model_name
                    )
                else:
                    error_text = f"Ollama API error: {response.status}"
                    logger.error(error_text)
                    return OllamaResponse(
                        text=error_text,
                        tokens_used=0,
                        generation_time=time.time() - start_time,
                        model_name=self.config.model_name
                    )
                    
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            return OllamaResponse(
                text=f"Error: {str(e)}",
                tokens_used=0,
                generation_time=time.time() - start_time,
                model_name=self.config.model_name
            )

    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze text using Ollama for agent operations."""
        prompts = {
            "sentiment": f"Analyze the sentiment of this text and provide a score from -1 (negative) to 1 (positive): {text}",
            "compliance": f"Check this text for compliance issues and list any violations: {text}",
            "fraud": f"Analyze this text for potential fraud indicators: {text}",
            "summary": f"Provide a concise summary of this text: {text}",
            "risk": f"Assess the risk level (low/medium/high) of this text: {text}"
        }
        
        prompt = prompts.get(analysis_type, f"Analyze this text: {text}")
        
        response = await self.generate_text(prompt, max_tokens=256, temperature=0.3)
        
        return {
            "analysis_type": analysis_type,
            "input_text": text,
            "result": response.text,
            "confidence": self._extract_confidence(response.text),
            "tokens_used": response.tokens_used,
            "generation_time": response.generation_time,
            "model_name": response.model_name
        }

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from generated text."""
        confidence_indicators = {
            "high": 0.9, "medium": 0.6, "low": 0.3,
            "certain": 0.95, "uncertain": 0.4
        }
        
        text_lower = text.lower()
        for indicator, score in confidence_indicators.items():
            if indicator in text_lower:
                return score
        return 0.7

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Ollama session closed")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Ollama integration."""
        return {
            "connected": self._is_connected,
            "model_name": self.config.model_name,
            "base_url": self.config.base_url,
            "config": self.config.dict()
        }


# Global Ollama instance
_global_ollama: Optional[OllamaIntegration] = None


async def get_global_ollama() -> Optional[OllamaIntegration]:
    """Get the global Ollama instance."""
    return _global_ollama


async def initialize_global_ollama(config: OllamaConfig) -> bool:
    """Initialize the global Ollama instance."""
    global _global_ollama
    
    try:
        _global_ollama = OllamaIntegration(config)
        connected = await _global_ollama.check_connection()
        if connected:
            logger.info("Global Ollama initialized successfully")
        return connected
    except Exception as e:
        logger.error(f"Failed to initialize global Ollama: {e}")
        return False


async def cleanup_global_ollama() -> None:
    """Clean up the global Ollama instance."""
    global _global_ollama
    
    if _global_ollama:
        await _global_ollama.close()
        _global_ollama = None
        logger.info("Global Ollama cleaned up")
