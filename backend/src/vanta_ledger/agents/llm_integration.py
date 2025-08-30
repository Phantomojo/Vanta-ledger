"""
Local LLM Integration Module

Provides integration with local language models for AI agent operations.
Handles memory constraints and efficient model loading for agent testing.
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import torch
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for local LLM integration."""
    model_path: str = Field(..., description="Path to the local model")
    model_type: str = Field(default="auto", description="Model type (auto, llama, mistral, etc.)")
    max_memory_gb: float = Field(default=8.0, description="Maximum memory usage in GB")
    max_tokens: int = Field(default=512, description="Maximum tokens for generation")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    use_8bit: bool = Field(default=True, description="Use 8-bit quantization to save memory")
    use_4bit: bool = Field(default=False, description="Use 4-bit quantization for extreme memory savings")


class LLMResponse(BaseModel):
    """Response from local LLM."""
    text: str = Field(..., description="Generated text")
    tokens_used: int = Field(..., description="Number of tokens used")
    generation_time: float = Field(..., description="Generation time in seconds")
    memory_used_gb: Optional[float] = Field(None, description="Memory used during generation")


class LocalLLMIntegration:
    """
    Integration with local language models for AI agent operations.
    
    This class provides efficient access to local LLMs with memory constraint handling
    and optimization for agent testing scenarios.
    """

    def __init__(self, config: LLMConfig):
        """
        Initialize the local LLM integration.
        
        Args:
            config: Configuration for the LLM
        """
        self.config = config
        self._model = None
        self._tokenizer = None
        self._is_loaded = False
        self._last_used = None
        self._memory_monitor = MemoryMonitor(max_memory_gb=config.max_memory_gb)
        
        logger.info(f"Initialized Local LLM Integration with model: {config.model_path}")

    async def load_model(self) -> bool:
        """
        Load the local model with memory optimization.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            if self._is_loaded:
                logger.info("Model already loaded")
                return True

            # Check available memory
            available_memory = self._memory_monitor.get_available_memory()
            if available_memory < self.config.max_memory_gb:
                logger.warning(f"Available memory ({available_memory:.2f}GB) is less than required ({self.config.max_memory_gb}GB)")
                # Try to free some memory
                await self._free_memory()

            logger.info(f"Loading model from: {self.config.model_path}")
            
            # Try to load with different quantization levels based on memory
            if self.config.use_4bit and available_memory < 4.0:
                await self._load_model_4bit()
            elif self.config.use_8bit and available_memory < 8.0:
                await self._load_model_8bit()
            else:
                await self._load_model_full()

            self._is_loaded = True
            self._last_used = time.time()
            logger.info("Model loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    async def _load_model_4bit(self) -> None:
        """Load model with 4-bit quantization for extreme memory savings."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            
            # Configure 4-bit quantization
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype="float16",
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True
            )
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            self._model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            
            logger.info("Model loaded with 4-bit quantization")
            
        except ImportError:
            logger.error("BitsAndBytes not available for 4-bit quantization")
            raise

    async def _load_model_8bit(self) -> None:
        """Load model with 8-bit quantization for memory savings."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            
            # Configure 8-bit quantization
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            self._model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            
            logger.info("Model loaded with 8-bit quantization")
            
        except ImportError:
            logger.error("BitsAndBytes not available for 8-bit quantization")
            raise

    async def _load_model_full(self) -> None:
        """Load model with full precision."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            self._model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                device_map="auto",
                trust_remote_code=True
            )
            
            logger.info("Model loaded with full precision")
            
        except Exception as e:
            logger.error(f"Failed to load model with full precision: {e}")
            raise

    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> LLMResponse:
        """
        Generate text using the local model.
        
        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum tokens to generate (overrides config)
            temperature: Generation temperature (overrides config)
            
        Returns:
            LLMResponse containing generated text and metadata
        """
        if not self._is_loaded:
            success = await self.load_model()
            if not success:
                return LLMResponse(
                    text="Error: Model not loaded",
                    tokens_used=0,
                    generation_time=0.0
                )

        start_time = time.time()
        
        try:
            # Check memory before generation
            memory_before = self._memory_monitor.get_memory_usage()
            
            # Prepare inputs
            inputs = self._tokenizer(prompt, return_tensors="pt")
            input_tokens = inputs.input_ids.shape[1]
            
            # Generate
            with torch.no_grad():
                outputs = self._model.generate(
                    inputs.input_ids,
                    max_new_tokens=max_tokens or self.config.max_tokens,
                    temperature=temperature or self.config.temperature,
                    do_sample=True,
                    pad_token_id=self._tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = self._tokenizer.decode(outputs[0][input_tokens:], skip_special_tokens=True)
            total_tokens = outputs.shape[1]
            tokens_generated = total_tokens - input_tokens
            
            generation_time = time.time() - start_time
            memory_after = self._memory_monitor.get_memory_usage()
            memory_used = memory_after - memory_before if memory_after and memory_before else None
            
            self._last_used = time.time()
            
            return LLMResponse(
                text=generated_text,
                tokens_used=tokens_generated,
                generation_time=generation_time,
                memory_used_gb=memory_used
            )
            
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            return LLMResponse(
                text=f"Error: {str(e)}",
                tokens_used=0,
                generation_time=time.time() - start_time
            )

    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze text using the local model for agent operations.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (sentiment, compliance, fraud, etc.)
            
        Returns:
            Analysis results
        """
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
            "generation_time": response.generation_time
        }

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from generated text."""
        # Simple confidence extraction - can be enhanced
        confidence_indicators = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3,
            "certain": 0.95,
            "uncertain": 0.4
        }
        
        text_lower = text.lower()
        for indicator, score in confidence_indicators.items():
            if indicator in text_lower:
                return score
        
        return 0.7  # Default confidence

    async def _free_memory(self) -> None:
        """Attempt to free memory for model loading."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Clear any cached tensors
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Memory cleanup completed")

    async def unload_model(self) -> None:
        """Unload the model to free memory."""
        if self._is_loaded:
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None
            self._is_loaded = False
            
            await self._free_memory()
            logger.info("Model unloaded")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the LLM integration."""
        return {
            "model_loaded": self._is_loaded,
            "model_path": self.config.model_path,
            "last_used": self._last_used,
            "memory_usage": self._memory_monitor.get_memory_usage(),
            "available_memory": self._memory_monitor.get_available_memory(),
            "config": self.config.dict()
        }

    def __str__(self) -> str:
        """String representation of the LLM integration."""
        status = "loaded" if self._is_loaded else "not loaded"
        return f"LocalLLMIntegration(model={self.config.model_path}, status={status})"


class MemoryMonitor:
    """Monitor system memory usage."""
    
    def __init__(self, max_memory_gb: float = 8.0):
        self.max_memory_gb = max_memory_gb
    
    def get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in GB."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.used / (1024 ** 3)  # Convert to GB
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            return None
    
    def get_available_memory(self) -> float:
        """Get available memory in GB."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.available / (1024 ** 3)  # Convert to GB
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            return self.max_memory_gb  # Assume we have the max memory


# Global LLM instance for agent use
_global_llm: Optional[LocalLLMIntegration] = None


async def get_global_llm() -> Optional[LocalLLMIntegration]:
    """Get the global LLM instance."""
    return _global_llm


async def initialize_global_llm(config: LLMConfig) -> bool:
    """Initialize the global LLM instance."""
    global _global_llm
    
    try:
        _global_llm = LocalLLMIntegration(config)
        success = await _global_llm.load_model()
        if success:
            logger.info("Global LLM initialized successfully")
        return success
    except Exception as e:
        logger.error(f"Failed to initialize global LLM: {e}")
        return False


async def cleanup_global_llm() -> None:
    """Clean up the global LLM instance."""
    global _global_llm
    
    if _global_llm:
        await _global_llm.unload_model()
        _global_llm = None
        logger.info("Global LLM cleaned up")
