#!/usr/bin/env python3
"""
Local LLM API Routes
Multi-company document processing with local LLM integration
"""

import tempfile
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Body
from fastapi.responses import JSONResponse

from ..auth import get_current_user, User
from ..services.local_llm_service import local_llm_service
from ..services.enhanced_document_service import enhanced_document_service
from ..utils.validation import input_validator

router = APIRouter(prefix="/api/v2/llm", tags=["Local LLM"])

# ============================================================================
# DOCUMENT PROCESSING ENDPOINTS
# ============================================================================

@router.post("/process-document")
async def process_document_with_llm(
    file: UploadFile = File(...),
    company_id: str = Query(..., description="Company ID for context"),
    current_user: User = Depends(get_current_user)
):
    """Process document with local LLM for specific company"""
    try:
        # Validate company ID
        company_uuid = input_validator.validate_uuid(company_id, "company_id")
        
        # Create secure temporary file
        temp_fd, temp_path = tempfile.mkstemp(
            suffix=f"_{file.filename}",
            prefix=f"user_{current_user.id}_"
        )
        os.close(temp_fd)  # Close the file descriptor, we'll use the path
        
        # Create document data
        document_data = {
            "original_filename": file.filename,
            "secure_filename": f"user_{current_user.id}_{file.filename}",
            "file_path": temp_path,
            "file_size": 0,  # Will be set after file save
            "file_extension": file.filename.split(".")[-1] if "." in file.filename else "",
            "mime_type": file.content_type,
            "checksum": "temp_checksum",
            "company_id": str(company_uuid)
        }
        
        # Create document with LLM enhancement
        document = await enhanced_document_service.create_document_with_llm(
            document_data, current_user.id, company_uuid
        )
        
        return {
            "success": True,
            "document": document.dict(),
            "message": "Document processed with local LLM successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

@router.post("/analyze-text")
async def analyze_text_with_llm(
    text: str = Body(..., embed=True),
    company_id: str = Query(..., description="Company ID for context"),
    analysis_type: str = Query("general", description="Type of analysis: general, financial, entities"),
    current_user: User = Depends(get_current_user)
):
    """Analyze text with local LLM for specific company"""
    try:
        # Validate company ID
        company_uuid = input_validator.validate_uuid(company_id, "company_id")
        
        # Get company context
        company_context = await local_llm_service.company_context_manager.get_company_context(company_uuid)
        
        # Perform analysis based on type
        if analysis_type == "financial":
            result = await local_llm_service._extract_financial_data_with_context(text, company_context)
        elif analysis_type == "entities":
            result = await local_llm_service._extract_entities_with_context(text, company_context)
        else:
            result = {
                "classification": await local_llm_service._classify_document_with_context(text, company_context),
                "summary": await local_llm_service._generate_summary_with_context(text, company_context)
            }
        
        return {
            "success": True,
            "analysis": result,
            "analysis_type": analysis_type,
            "company_context": company_context["company_name"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze text: {str(e)}"
        )

# ============================================================================
# COMPANY MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/companies/{company_id}/context")
async def get_company_context(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get company-specific context for LLM processing"""
    try:
        company_uuid = input_validator.validate_uuid(company_id, "company_id")
        
        context = await local_llm_service.company_context_manager.get_company_context(company_uuid)
        
        return {
            "success": True,
            "company_context": context
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company context: {str(e)}"
        )

@router.get("/companies/{company_id}/statistics")
async def get_company_statistics(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get company processing statistics"""
    try:
        company_uuid = input_validator.validate_uuid(company_id, "company_id")
        
        stats = local_llm_service.company_context_manager.get_company_statistics(company_uuid)
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company statistics: {str(e)}"
        )

# ============================================================================
# HARDWARE & PERFORMANCE ENDPOINTS
# ============================================================================

@router.get("/hardware/status")
async def get_hardware_status(
    current_user: User = Depends(get_current_user)
):
    """Get current hardware status and utilization"""
    try:
        status = await local_llm_service.get_hardware_status()
        
        return {
            "success": True,
            "hardware_status": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hardware status: {str(e)}"
        )

@router.get("/performance/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get LLM performance metrics"""
    try:
        metrics = await local_llm_service.get_performance_metrics()
        
        return {
            "success": True,
            "performance_metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/hardware/summary")
async def get_hardware_summary(
    current_user: User = Depends(get_current_user)
):
    """Get human-readable hardware summary"""
    try:
        summary = local_llm_service.hardware_detector.get_hardware_summary()
        
        return {
            "success": True,
            "hardware_summary": summary,
            "detected_hardware": local_llm_service.hardware_config
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hardware summary: {str(e)}"
        )

# ============================================================================
# MODEL MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/models/status")
async def get_model_status(
    current_user: User = Depends(get_current_user)
):
    """Get status of loaded models"""
    try:
        models_loaded = list(local_llm_service.models.keys())
        recommended_models = local_llm_service.hardware_config.get("recommended_models", {})
        
        return {
            "success": True,
            "models_loaded": models_loaded,
            "recommended_models": recommended_models,
            "hardware_profile": local_llm_service.hardware_config["performance_profile"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model status: {str(e)}"
        )

@router.post("/models/reload")
async def reload_models(
    current_user: User = Depends(get_current_user)
):
    """Reload all models"""
    try:
        await local_llm_service.initialize_models()
        
        return {
            "success": True,
            "message": "Models reloaded successfully",
            "models_loaded": list(local_llm_service.models.keys())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload models: {str(e)}"
        )

# ============================================================================
# CACHE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/cache/clear")
async def clear_llm_cache(
    current_user: User = Depends(get_current_user)
):
    """Clear LLM cache"""
    try:
        # Clear Redis cache for LLM
        cache_keys = local_llm_service.redis_client.keys("llm_company_cache:*")
        if cache_keys:
            local_llm_service.redis_client.delete(*cache_keys)
        
        # Clear company context cache
        local_llm_service.company_context_manager.clear_cache()
        
        return {
            "success": True,
            "message": "LLM cache cleared successfully",
            "cleared_keys": len(cache_keys)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.get("/cache/status")
async def get_cache_status(
    current_user: User = Depends(get_current_user)
):
    """Get cache status and statistics"""
    try:
        # Get cache statistics
        cache_keys = local_llm_service.redis_client.keys("llm_company_cache:*")
        cache_size = len(cache_keys)
        
        # Get Redis info
        redis_info = local_llm_service.redis_client.info()
        
        return {
            "success": True,
            "cache_status": {
                "llm_cache_keys": cache_size,
                "redis_memory_used": redis_info.get("used_memory_human", "Unknown"),
                "redis_keyspace_hits": redis_info.get("keyspace_hits", 0),
                "redis_keyspace_misses": redis_info.get("keyspace_misses", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache status: {str(e)}"
        )

# ============================================================================
# HEALTH & DIAGNOSTICS ENDPOINTS
# ============================================================================

@router.get("/health")
async def llm_health_check():
    """Check LLM service health"""
    try:
        # Check if models are loaded
        models_loaded = len(local_llm_service.models) > 0
        
        # Check hardware status
        hardware_status = await local_llm_service.get_hardware_status()
        
        # Check Redis connection
        redis_connected = local_llm_service.redis_client.ping()
        
        health_status = {
            "service": "local_llm",
            "status": "healthy" if models_loaded and redis_connected else "degraded",
            "models_loaded": models_loaded,
            "redis_connected": redis_connected,
            "hardware_status": hardware_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "health": {
                "service": "local_llm",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        }

@router.get("/diagnostics")
async def get_llm_diagnostics(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive LLM diagnostics"""
    try:
        diagnostics = {
            "hardware": {
                "detection": local_llm_service.hardware_config,
                "current_status": await local_llm_service.get_hardware_status()
            },
            "models": {
                "loaded": list(local_llm_service.models.keys()),
                "recommended": local_llm_service.hardware_config.get("recommended_models", {}),
                "configs": local_llm_service.model_configs
            },
            "performance": {
                "metrics": await local_llm_service.get_performance_metrics()
            },
            "cache": {
                "keys": len(local_llm_service.redis_client.keys("llm_company_cache:*")),
                "redis_info": local_llm_service.redis_client.info()
            },
            "company_contexts": {
                "cached": len(local_llm_service.company_context_manager.company_configs)
            }
        }
        
        return {
            "success": True,
            "diagnostics": diagnostics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get diagnostics: {str(e)}"
        )
