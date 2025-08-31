#!/usr/bin/env python3
"""
Multi-GitHub Models API Routes
Provides REST API endpoints for accessing multiple GitHub-hosted models.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ..services.multi_github_models_service import MultiGitHubModelsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multi-github-models", tags=["Multi-GitHub Models"])

# Initialize service
multi_github_service = MultiGitHubModelsService()


class AnalysisRequest(BaseModel):
    """Request for multi-model analysis"""
    text: str = Field(..., description="Text to analyze")
    task_type: str = Field(default="analysis", description="Type of task (analysis, code, financial, reasoning)")
    models: Optional[List[str]] = Field(default=None, description="Specific models to use")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens for generation")
    temperature: Optional[float] = Field(default=None, description="Generation temperature")


class ModelActivationRequest(BaseModel):
    """Request to activate specific models"""
    model_names: List[str] = Field(..., description="List of model names to activate")


class ModelResponse(BaseModel):
    """Response from a single model"""
    model: str
    response: str
    usage: Optional[Dict[str, Any]] = None
    success: bool
    error: Optional[str] = None


class MultiModelAnalysisResponse(BaseModel):
    """Response from multi-model analysis"""
    task_type: str
    models_used: List[str]
    successful_models: int
    failed_models: int
    combined_response: str
    individual_results: List[ModelResponse]
    failed_results: List[Dict[str, Any]]


class ModelStatusResponse(BaseModel):
    """Response for model status"""
    service_enabled: bool
    total_models: int
    active_models: int
    models: Dict[str, Dict[str, Any]]


class ActivationResponse(BaseModel):
    """Response for model activation"""
    active_models: List[str]
    total_models: int
    message: str


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check for multi-GitHub models service"""
    try:
        status = await multi_github_service.get_model_status()
        return {
            "status": "healthy",
            "service": "multi-github-models",
            "enabled": status["service_enabled"],
            "total_models": status["total_models"],
            "active_models": status["active_models"],
            "capabilities": [
                "multi_model_analysis",
                "model_activation",
                "parallel_processing",
                "task_specific_routing"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service health check failed: {str(e)}")


@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status():
    """Get detailed status of all models"""
    try:
        return await multi_github_service.get_model_status()
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")


@router.post("/analyze", response_model=MultiModelAnalysisResponse)
async def analyze_with_multiple_models(request: AnalysisRequest):
    """Analyze text with multiple models"""
    try:
        result = await multi_github_service.analyze_with_multiple_models(
            text=request.text,
            task_type=request.task_type,
            models=request.models
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/activate", response_model=ActivationResponse)
async def activate_models(request: ModelActivationRequest):
    """Activate specific models"""
    try:
        result = await multi_github_service.set_active_models(request.model_names)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Model activation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model activation failed: {str(e)}")


@router.get("/models", response_model=Dict[str, Any])
async def list_models():
    """List all available models with their details"""
    try:
        status = await multi_github_service.get_model_status()
        return {
            "available_models": status["models"],
            "active_models": [name for name, details in status["models"].items() if details["active"]],
            "model_types": {
                "language": [name for name, details in status["models"].items() if details["type"] == "language"],
                "code": [name for name, details in status["models"].items() if details["type"] == "code"],
                "multimodal": [name for name, details in status["models"].items() if details["type"] == "multimodal"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/models/{model_name}", response_model=Dict[str, Any])
async def get_model_details(model_name: str):
    """Get details for a specific model"""
    try:
        status = await multi_github_service.get_model_status()
        if model_name not in status["models"]:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        
        return {
            "model_name": model_name,
            "details": status["models"][model_name]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model details: {str(e)}")


@router.post("/analyze/financial")
async def analyze_financial_document(request: AnalysisRequest):
    """Specialized endpoint for financial document analysis"""
    try:
        result = await multi_github_service.analyze_with_multiple_models(
            text=request.text,
            task_type="financial",
            models=request.models or ["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Financial analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Financial analysis failed: {str(e)}")


@router.post("/analyze/code")
async def analyze_code(request: AnalysisRequest):
    """Specialized endpoint for code analysis"""
    try:
        result = await multi_github_service.analyze_with_multiple_models(
            text=request.text,
            task_type="code",
            models=request.models or ["codellama-34b", "codellama-70b", "gpt-4o-mini"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")


@router.post("/analyze/reasoning")
async def analyze_reasoning(request: AnalysisRequest):
    """Specialized endpoint for reasoning tasks"""
    try:
        result = await multi_github_service.analyze_with_multiple_models(
            text=request.text,
            task_type="reasoning",
            models=request.models or ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Reasoning analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reasoning analysis failed: {str(e)}")


@router.get("/capabilities", response_model=Dict[str, Any])
async def get_capabilities():
    """Get service capabilities"""
    return {
        "service": "multi-github-models",
        "capabilities": {
            "multi_model_analysis": "Analyze text with multiple models simultaneously",
            "task_specific_routing": "Route tasks to appropriate models based on type",
            "parallel_processing": "Process multiple models in parallel",
            "model_activation": "Dynamically activate/deactivate models",
            "response_combination": "Combine responses from multiple models",
            "financial_analysis": "Specialized financial document analysis",
            "code_analysis": "Specialized code analysis and generation",
            "reasoning_tasks": "Advanced reasoning and problem solving"
        },
        "supported_task_types": [
            "analysis",
            "financial",
            "code",
            "reasoning"
        ],
        "model_types": [
            "language",
            "code",
            "multimodal"
        ]
    }


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await multi_github_service.close()
