"""
AI Agents Package

This package contains intelligent AI agents for financial automation,
compliance monitoring, fraud detection, forecasting, and reporting.
"""

from .base_agent import BaseAgent, AgentResult, AnalysisResult
from .agent_manager import AgentManager
from .communication import AgentCommunication
from .llm_integration import LLMConfig, LocalLLMIntegration, initialize_global_llm, get_global_llm
from .ollama_integration import OllamaConfig, OllamaIntegration, initialize_global_ollama, get_global_ollama

__all__ = [
    "BaseAgent",
    "AgentResult", 
    "AnalysisResult",
    "AgentManager",
    "AgentCommunication",
    "LLMConfig",
    "LocalLLMIntegration",
    "initialize_global_llm",
    "get_global_llm",
    "OllamaConfig",
    "OllamaIntegration",
    "initialize_global_ollama",
    "get_global_ollama"
]
