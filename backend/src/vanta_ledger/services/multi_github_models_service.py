#!/usr/bin/env python3
"""
Multi-GitHub Models Service
Provides access to multiple GitHub-hosted models for enhanced AI capabilities.
Supports various model types including language models, code models, and specialized models.
"""
import logging
import os
import re
import json
import asyncio
import aiohttp
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported model types"""
    LANGUAGE = "language"
    CODE = "code"
    FINANCIAL = "financial"
    DOCUMENT = "document"
    MULTIMODAL = "multimodal"


@dataclass
class GitHubModel:
    """GitHub model configuration"""
    name: str
    repository: str
    model_type: ModelType
    description: str
    capabilities: List[str]
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority


@dataclass
class MultiGitHubModelsService:
    """Multi-GitHub Models Service for enhanced AI capabilities"""
    
    token: Optional[str] = field(default=None)
    enabled: bool = field(init=False)
    models: Dict[str, GitHubModel] = field(default_factory=dict)
    active_models: Dict[str, bool] = field(default_factory=dict)
    session: Optional[aiohttp.ClientSession] = field(default=None)
    
    def __post_init__(self):
        # Read token from environment
        self.token = self.token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_MODELS_TOKEN")
        self.enabled = bool(self.token)
        
        # Initialize GitHub-hosted models
        self._initialize_github_models()
        
        # Set up active models
        self._setup_active_models()
        
        logger.info(f"Multi-GitHub Models Service initialized with {len(self.models)} models")
    
    def _initialize_github_models(self):
        """Initialize available GitHub-hosted models"""
        
        # Language Models
        self.models.update({
            "gpt-4o-mini": GitHubModel(
                name="gpt-4o-mini",
                repository="openai/gpt-4o-mini",
                model_type=ModelType.LANGUAGE,
                description="Fast and efficient language model for general tasks",
                capabilities=["text_generation", "analysis", "summarization", "translation"],
                max_tokens=4096,
                temperature=0.7,
                priority=1
            ),
            
            "gpt-4o": GitHubModel(
                name="gpt-4o",
                repository="openai/gpt-4o",
                model_type=ModelType.LANGUAGE,
                description="Advanced language model with multimodal capabilities",
                capabilities=["text_generation", "image_analysis", "code_generation", "reasoning"],
                max_tokens=8192,
                temperature=0.7,
                priority=2
            ),
            
            "claude-3-5-sonnet": GitHubModel(
                name="claude-3-5-sonnet",
                repository="anthropic/claude-3-5-sonnet",
                model_type=ModelType.LANGUAGE,
                description="Advanced reasoning and analysis model",
                capabilities=["reasoning", "analysis", "code_generation", "mathematics"],
                max_tokens=8192,
                temperature=0.7,
                priority=3
            ),
            
            "claude-3-haiku": GitHubModel(
                name="claude-3-haiku",
                repository="anthropic/claude-3-haiku",
                model_type=ModelType.LANGUAGE,
                description="Fast and efficient Claude model",
                capabilities=["text_generation", "analysis", "summarization"],
                max_tokens=4096,
                temperature=0.7,
                priority=4
            ),
            
            "gemini-1.5-pro": GitHubModel(
                name="gemini-1.5-pro",
                repository="google/gemini-1.5-pro",
                model_type=ModelType.MULTIMODAL,
                description="Google's advanced multimodal model",
                capabilities=["text_generation", "image_analysis", "code_generation", "reasoning"],
                max_tokens=8192,
                temperature=0.7,
                priority=5
            ),
            
            "gemini-1.5-flash": GitHubModel(
                name="gemini-1.5-flash",
                repository="google/gemini-1.5-flash",
                model_type=ModelType.LANGUAGE,
                description="Fast and efficient Gemini model",
                capabilities=["text_generation", "analysis", "summarization"],
                max_tokens=4096,
                temperature=0.7,
                priority=6
            ),
            
            "codellama-70b": GitHubModel(
                name="codellama-70b",
                repository="meta-llama/codellama-70b",
                model_type=ModelType.CODE,
                description="Large code generation model",
                capabilities=["code_generation", "code_analysis", "debugging", "documentation"],
                max_tokens=8192,
                temperature=0.7,
                priority=7
            ),
            
            "codellama-34b": GitHubModel(
                name="codellama-34b",
                repository="meta-llama/codellama-34b",
                model_type=ModelType.CODE,
                description="Medium code generation model",
                capabilities=["code_generation", "code_analysis", "debugging"],
                max_tokens=4096,
                temperature=0.7,
                priority=8
            ),
            
            "mistral-large": GitHubModel(
                name="mistral-large",
                repository="mistralai/mistral-large",
                model_type=ModelType.LANGUAGE,
                description="Mistral's large language model",
                capabilities=["text_generation", "analysis", "reasoning", "translation"],
                max_tokens=8192,
                temperature=0.7,
                priority=9
            ),
            
            "mistral-medium": GitHubModel(
                name="mistral-medium",
                repository="mistralai/mistral-medium",
                model_type=ModelType.LANGUAGE,
                description="Mistral's medium language model",
                capabilities=["text_generation", "analysis", "summarization"],
                max_tokens=4096,
                temperature=0.7,
                priority=10
            ),
            
            "llama-3.1-70b": GitHubModel(
                name="llama-3.1-70b",
                repository="meta-llama/llama-3.1-70b",
                model_type=ModelType.LANGUAGE,
                description="Meta's large language model",
                capabilities=["text_generation", "analysis", "reasoning", "translation"],
                max_tokens=8192,
                temperature=0.7,
                priority=11
            ),
            
            "llama-3.1-8b": GitHubModel(
                name="llama-3.1-8b",
                repository="meta-llama/llama-3.1-8b",
                model_type=ModelType.LANGUAGE,
                description="Meta's efficient language model",
                capabilities=["text_generation", "analysis", "summarization"],
                max_tokens=4096,
                temperature=0.7,
                priority=12
            ),
            
            "phi-3.5": GitHubModel(
                name="phi-3.5",
                repository="microsoft/phi-3.5",
                model_type=ModelType.LANGUAGE,
                description="Microsoft's efficient language model",
                capabilities=["text_generation", "analysis", "reasoning"],
                max_tokens=4096,
                temperature=0.7,
                priority=13
            ),
            
            "qwen2.5-72b": GitHubModel(
                name="qwen2.5-72b",
                repository="qwen/Qwen2.5-72B",
                model_type=ModelType.LANGUAGE,
                description="Alibaba's large language model",
                capabilities=["text_generation", "analysis", "reasoning", "multilingual"],
                max_tokens=8192,
                temperature=0.7,
                priority=14
            ),
            
            "qwen2.5-7b": GitHubModel(
                name="qwen2.5-7b",
                repository="qwen/Qwen2.5-7B",
                model_type=ModelType.LANGUAGE,
                description="Alibaba's efficient language model",
                capabilities=["text_generation", "analysis", "summarization"],
                max_tokens=4096,
                temperature=0.7,
                priority=15
            )
        })
    
    def _setup_active_models(self):
        """Set up which models are active based on configuration"""
        # Get active models from environment
        active_models_str = os.getenv("ACTIVE_GITHUB_MODELS", "gpt-4o-mini,claude-3-haiku,gemini-1.5-flash")
        active_model_list = [m.strip() for m in active_models_str.split(",")]
        
        # Set active status
        for model_name in self.models:
            self.active_models[model_name] = model_name in active_model_list
        
        logger.info(f"Active models: {[name for name, active in self.active_models.items() if active]}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def _call_model_api(self, model_name: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Call a specific model's API"""
        if not self.enabled:
            raise RuntimeError("Multi-GitHub Models Service is not enabled")
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        if not self.active_models.get(model_name, False):
            raise ValueError(f"Model {model_name} is not active")
        
        model = self.models[model_name]
        session = await self._get_session()
        
        # Prepare request payload
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", model.max_tokens),
            "temperature": kwargs.get("temperature", model.temperature)
        }
        
        try:
            # This is a simplified implementation - in practice, you'd need to
            # implement the actual API calls for each model provider
            async with session.post(
                f"https://api.github.com/models/{model_name}/generate",
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "model": model_name,
                        "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "usage": result.get("usage", {}),
                        "success": True
                    }
                else:
                    return {
                        "model": model_name,
                        "response": "",
                        "error": f"API call failed with status {response.status}",
                        "success": False
                    }
        except Exception as e:
            logger.error(f"Error calling model {model_name}: {e}")
            return {
                "model": model_name,
                "response": "",
                "error": str(e),
                "success": False
            }
    
    async def analyze_with_multiple_models(
        self, 
        text: str, 
        task_type: str = "analysis",
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze text with multiple models and combine results"""
        
        if not models:
            # Select models based on task type
            if task_type == "code":
                models = ["codellama-34b", "codellama-70b", "gpt-4o-mini"]
            elif task_type == "financial":
                models = ["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash"]
            elif task_type == "reasoning":
                models = ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"]
            else:
                models = ["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash"]
        
        # Filter to only active models
        active_models = [m for m in models if self.active_models.get(m, False)]
        
        if not active_models:
            raise ValueError("No active models available for the specified task")
        
        # Create tasks for parallel execution
        tasks = []
        for model_name in active_models:
            task = self._call_model_api(model_name, text)
            tasks.append(task)
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    "model": active_models[i],
                    "error": str(result)
                })
            elif result.get("success"):
                successful_results.append(result)
            else:
                failed_results.append(result)
        
        # Combine successful results
        combined_response = self._combine_model_responses(successful_results)
        
        return {
            "task_type": task_type,
            "models_used": active_models,
            "successful_models": len(successful_results),
            "failed_models": len(failed_results),
            "combined_response": combined_response,
            "individual_results": successful_results,
            "failed_results": failed_results
        }
    
    def _combine_model_responses(self, results: List[Dict[str, Any]]) -> str:
        """Combine responses from multiple models"""
        if not results:
            return ""
        
        if len(results) == 1:
            return results[0]["response"]
        
        # For multiple results, create a summary
        responses = [r["response"] for r in results if r["response"]]
        
        if not responses:
            return ""
        
        # Simple combination strategy - take the longest response as primary
        # In practice, you might want more sophisticated combination logic
        primary_response = max(responses, key=len)
        
        # Add a note about consensus
        if len(responses) > 1:
            primary_response += f"\n\n[Analysis based on {len(responses)} AI models]"
        
        return primary_response
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return {
            "service_enabled": self.enabled,
            "total_models": len(self.models),
            "active_models": len([m for m in self.active_models.values() if m]),
            "models": {
                name: {
                    "type": model.model_type.value,
                    "description": model.description,
                    "capabilities": model.capabilities,
                    "active": self.active_models.get(name, False),
                    "priority": model.priority
                }
                for name, model in self.models.items()
            }
        }
    
    async def set_active_models(self, model_names: List[str]) -> Dict[str, Any]:
        """Set which models are active"""
        # Validate model names
        invalid_models = [name for name in model_names if name not in self.models]
        if invalid_models:
            raise ValueError(f"Invalid model names: {invalid_models}")
        
        # Update active models
        for model_name in self.models:
            self.active_models[model_name] = model_name in model_names
        
        logger.info(f"Active models updated: {model_names}")
        
        return {
            "active_models": model_names,
            "total_models": len(self.models),
            "message": f"Successfully activated {len(model_names)} models"
        }
    
    async def close(self):
        """Close the service and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close())
