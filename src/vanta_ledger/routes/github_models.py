#!/usr/bin/env python3
"""
GitHub Models API Routes
Provides endpoints for AI-powered financial analysis using GitHub Models
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field

from ..auth import verify_token
from ..services.github_models_service import github_models_service
from ..services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/github-models", tags=["GitHub Models AI"])

# Pydantic models for request/response
class AnalyzeDocumentRequest(BaseModel):
    document_text: str = Field(..., description="Text content of the document to analyze")
    document_type: str = Field(default="invoice", description="Type of document (invoice, receipt, contract, etc.)")

class CategorizeExpenseRequest(BaseModel):
    description: str = Field(..., description="Description of the expense")
    amount: Optional[float] = Field(None, description="Amount of the expense")
    vendor: Optional[str] = Field(None, description="Vendor/merchant name")
    date: Optional[str] = Field(None, description="Date of the expense")

class GenerateInsightsRequest(BaseModel):
    financial_data: Dict[str, Any] = Field(..., description="Financial data to analyze")
    period: str = Field(default="recent", description="Time period for analysis")
    company_size: str = Field(default="unknown", description="Size of the company")
    industry: str = Field(default="general", description="Industry type")

class GenerateReportRequest(BaseModel):
    financial_data: Dict[str, Any] = Field(..., description="Financial data for the report")
    report_type: str = Field(default="quarterly", description="Type of report")
    period: str = Field(default="Q1 2024", description="Reporting period")
    company_name: str = Field(default="Company", description="Company name")
    context: Optional[str] = Field(None, description="Additional context")

class NaturalLanguageQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query about financial data")
    context_data: Dict[str, Any] = Field(..., description="Context data for the query")

# Health check endpoint
@router.get("/health")
async def github_models_health():
    """Check GitHub Models service health"""
    return {
        "service": "GitHub Models",
        "status": "available" if github_models_service.enabled else "unavailable",
        "token_configured": bool(github_models_service.token) if github_models_service.enabled else False,
        "available_prompts": github_models_service.get_available_prompts() if github_models_service.enabled else [],
        "default_model": github_models_service.default_model if github_models_service.enabled else None
    }

# Document analysis endpoints
@router.post("/analyze-document")
async def analyze_document(
    request: AnalyzeDocumentRequest,
    current_user: dict = Depends(verify_token)
):
    """Analyze a financial document using GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    try:
        result = await github_models_service.analyze_financial_document(
            document_text=request.document_text,
            document_type=request.document_type
        )
        
        return {
            "success": True,
            "analysis": result,
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-document-upload")
async def analyze_document_upload(
    file: UploadFile = File(...),
    document_type: str = Form(default="invoice"),
    current_user: dict = Depends(verify_token)
):
    """Upload and analyze a document using GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    try:
        # Initialize document processor
        doc_processor = DocumentProcessor()
        
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        try:
            # Process document with AI enhancement
            result = await doc_processor.process_document_async(
                file_path=temp_file_path,
                original_filename=file.filename
            )
            
            return {
                "success": True,
                "doc_id": result["doc_id"],
                "analysis": result["analysis"],
                "ai_enhanced": result["analysis"].get("enhanced_with_ai", False),
                "processed_by": current_user.get("username", "unknown")
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Document upload analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Expense categorization endpoint
@router.post("/categorize-expense")
async def categorize_expense(
    request: CategorizeExpenseRequest,
    current_user: dict = Depends(verify_token)
):
    """Categorize an expense using GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    try:
        result = await github_models_service.categorize_expense(
            description=request.description,
            amount=request.amount,
            vendor=request.vendor,
            date=request.date
        )
        
        return {
            "success": True,
            "categorization": result,
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Expense categorization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")

# Financial insights endpoint
@router.post("/generate-insights")
async def generate_insights(
    request: GenerateInsightsRequest,
    current_user: dict = Depends(verify_token)
):
    """Generate financial insights using GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    try:
        result = await github_models_service.generate_financial_insights(
            financial_data=request.financial_data,
            period=request.period,
            company_size=request.company_size,
            industry=request.industry
        )
        
        return {
            "success": True,
            "insights": result,
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

# Report generation endpoint
@router.post("/generate-report")
async def generate_report(
    request: GenerateReportRequest,
    current_user: dict = Depends(verify_token)
):
    """Generate comprehensive financial report using GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    try:
        result = await github_models_service.generate_financial_report(
            financial_data=request.financial_data,
            report_type=request.report_type,
            period=request.period,
            company_name=request.company_name,
            context=request.context
        )
        
        return {
            "success": True,
            "report": result,
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

# Natural language query endpoint
@router.post("/query")
async def natural_language_query(
    request: NaturalLanguageQueryRequest,
    current_user: dict = Depends(verify_token)
):
    """Process natural language queries about financial data"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    try:
        result = await github_models_service.natural_language_query(
            query=request.query,
            context_data=request.context_data
        )
        
        return {
            "success": True,
            "response": result,
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Natural language query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

# Prompt template management endpoints
@router.get("/prompts")
async def list_prompts(current_user: dict = Depends(verify_token)):
    """List available prompt templates"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    prompts = github_models_service.get_available_prompts()
    prompt_info = {}
    
    for prompt_name in prompts:
        prompt_info[prompt_name] = github_models_service.get_prompt_info(prompt_name)
    
    return {
        "success": True,
        "available_prompts": prompts,
        "prompt_details": prompt_info,
        "total_prompts": len(prompts)
    }

@router.get("/prompts/{prompt_name}")
async def get_prompt_info(
    prompt_name: str,
    current_user: dict = Depends(verify_token)
):
    """Get detailed information about a specific prompt template"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    prompt_info = github_models_service.get_prompt_info(prompt_name)
    
    if not prompt_info:
        raise HTTPException(status_code=404, detail=f"Prompt template '{prompt_name}' not found")
    
    return {
        "success": True,
        "prompt_name": prompt_name,
        "prompt_info": prompt_info
    }

# Batch processing endpoint
@router.post("/batch-analyze")
async def batch_analyze_documents(
    requests: List[AnalyzeDocumentRequest],
    current_user: dict = Depends(verify_token)
):
    """Batch analyze multiple documents"""
    if not github_models_service.enabled:
        raise HTTPException(status_code=503, detail="GitHub Models service not available")
    
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 documents per batch")
    
    results = []
    
    for i, request in enumerate(requests):
        try:
            result = await github_models_service.analyze_financial_document(
                document_text=request.document_text,
                document_type=request.document_type
            )
            
            results.append({
                "index": i,
                "success": True,
                "analysis": result
            })
            
        except Exception as e:
            logger.exception(f"Batch analysis failed for document {i}")
            results.append({
                "index": i,
                "success": False,
                "error": "Internal error during analysis"
            })
    
    return {
        "success": True,
        "batch_results": results,
        "total_processed": len(results),
        "successful": len([r for r in results if r["success"]]),
        "failed": len([r for r in results if not r["success"]]),
        "processed_by": current_user.get("username", "unknown")
    }





