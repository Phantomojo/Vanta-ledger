#!/usr/bin/env python3
"""
Backend Startup Script
Initializes services and performs startup checks
"""

import asyncio
import logging
from typing import Optional

from .services.local_llm_service import local_llm_service
from .config import settings

logger = logging.getLogger(__name__)

async def initialize_services():
    """Initialize all backend services"""
    try:
        logger.info("Initializing backend services...")
        
        # Initialize local LLM service
        await initialize_local_llm()
        
        logger.info("All services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        return False

async def initialize_local_llm():
    """Initialize local LLM service"""
    try:
        logger.info("Initializing local LLM service...")
        
        # Check if LLM service should be enabled
        if not getattr(settings, 'ENABLE_LOCAL_LLM', True):
            logger.info("Local LLM service disabled in settings")
            return
        
        # Initialize models
        await local_llm_service.initialize_models()
        
        # Get hardware status
        hardware_status = await local_llm_service.get_hardware_status()
        logger.info(f"Hardware status: {hardware_status}")
        
        # Get performance metrics
        metrics = await local_llm_service.get_performance_metrics()
        logger.info(f"Performance profile: {metrics.get('hardware', {}).get('performance_profile', 'unknown')}")
        
        logger.info("Local LLM service initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize local LLM service: {str(e)}")
        # Don't fail startup if LLM service fails - it's optional
        logger.info("Continuing startup without local LLM service")

async def health_check():
    """Perform health check on all services"""
    try:
        health_status = {
            "status": "healthy",
            "services": {}
        }
        
        # Check local LLM service
        try:
            if hasattr(settings, 'ENABLE_LOCAL_LLM') and settings.ENABLE_LOCAL_LLM:
                hardware_status = await local_llm_service.get_hardware_status()
                health_status["services"]["local_llm"] = {
                    "status": "healthy",
                    "models_loaded": len(local_llm_service.models),
                    "hardware": hardware_status
                }
            else:
                health_status["services"]["local_llm"] = {
                    "status": "disabled"
                }
        except Exception as e:
            health_status["services"]["local_llm"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 