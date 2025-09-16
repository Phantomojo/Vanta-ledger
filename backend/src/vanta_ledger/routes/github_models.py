#!/usr/bin/env python3
"""
Enhanced GitHub Models API Routes
Provides comprehensive endpoints for AI-powered financial analysis using GitHub Models
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from ..auth import verify_token
from ..services.document_processor import DocumentProcessor
from ..services.github_models_service import github_models_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/github-models", tags=["GitHub Models AI"])


# Enhanced Pydantic models for request/response
class AnalyzeDocumentRequest(BaseModel):
    document_text: str = Field(
        ..., description="Text content of the document to analyze"
    )
    document_type: str = Field(
        default="invoice",
        description="Type of document (invoice, receipt, contract, etc.)",
    )


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
    financial_data: Dict[str, Any] = Field(
        ..., description="Financial data for the report"
    )
    report_type: str = Field(default="quarterly", description="Type of report")
    period: str = Field(default="Q1 2024", description="Reporting period")
    company_name: str = Field(default="Company", description="Company name")
    context: Optional[str] = Field(None, description="Additional context")


class NaturalLanguageQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query about financial data")
    context_data: Dict[str, Any] = Field(..., description="Context data for the query")


class FraudDetectionRequest(BaseModel):
    transactions: List[Dict[str, Any]] = Field(..., description="List of transactions to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of fraud analysis")


class ComplianceCheckRequest(BaseModel):
    financial_data: Dict[str, Any] = Field(..., description="Financial data to check")
    regulations: List[str] = Field(
        default=["basic_accounting", "tax_compliance", "audit_standards"],
        description="List of regulations to check against"
    )


# Enhanced health check endpoint
@router.get("/health")
async def github_models_health():
    """Check GitHub Models service health with enhanced capabilities"""
    return {
        "service": "Enhanced GitHub Models",
        "status": "available" if github_models_service.enabled else "unavailable",
        "token_configured": (
            bool(github_models_service.token)
            if github_models_service.enabled
            else False
        ),
        "available_prompts": (
            github_models_service.get_available_prompts()
            if github_models_service.enabled
            else []
        ),
        "expense_categories": (
            len(github_models_service.get_expense_categories())
            if github_models_service.enabled
            else 0
        ),
        "industry_patterns": (
            len(github_models_service.get_industry_patterns())
            if github_models_service.enabled
            else 0
        ),
        "default_model": (
            github_models_service.default_model
            if github_models_service.enabled
            else None
        ),
        "capabilities": [
            "document_analysis",
            "expense_categorization", 
            "insights_generation",
            "report_generation",
            "natural_language_query",
            "fraud_detection",
            "compliance_checking"
        ] if github_models_service.enabled else []
    }


# Enhanced document analysis endpoints
@router.post("/analyze-document")
async def analyze_document(
    request: AnalyzeDocumentRequest, current_user: dict = Depends(verify_token)
):
    """Analyze a financial document using enhanced GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        result = await github_models_service.analyze_financial_document(
            document_text=request.document_text, document_type=request.document_type
        )

        return {
            "success": True,
            "analysis": result,
            "processed_by": current_user.get("username", "unknown"),
            "analysis_quality": result.get("analysis_quality", "unknown"),
            "confidence": result.get("confidence", 0.0)
        }

    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-document-upload")
async def analyze_document_upload(
    file: UploadFile = File(...),
    document_type: str = Form(default="invoice"),
    current_user: dict = Depends(verify_token),
):
    """Upload and analyze a document using enhanced GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        # Initialize document processor
        doc_processor = DocumentProcessor()

        # Save uploaded file temporarily
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f"_{file.filename}"
        ) as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name

        try:
            # Process document with AI enhancement
            result = await doc_processor.process_document_async(
                file_path=temp_file_path, original_filename=file.filename
            )

            return {
                "success": True,
                "doc_id": result["doc_id"],
                "analysis": result["analysis"],
                "ai_enhanced": result["analysis"].get("enhanced_with_ai", False),
                "processed_by": current_user.get("username", "unknown"),
            }

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError as e:
                logger.debug(f"Failed to remove temporary file {temp_file_path}: {e}")
                pass

    except Exception as e:
        logger.error(f"Document upload analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Enhanced expense categorization endpoint
@router.post("/categorize-expense")
async def categorize_expense(
    request: CategorizeExpenseRequest, current_user: dict = Depends(verify_token)
):
    """Categorize an expense using enhanced GitHub Models AI with confidence scoring"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        result = await github_models_service.categorize_expense(
            description=request.description,
            amount=request.amount,
            vendor=request.vendor,
            date=request.date,
        )

        return {
            "success": True,
            "categorization": result,
            "processed_by": current_user.get("username", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "industry_context": result.get("industry_context", "general")
        }

    except Exception as e:
        logger.error(f"Expense categorization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")


# Enhanced financial insights endpoint
@router.post("/generate-insights")
async def generate_insights(
    request: GenerateInsightsRequest, current_user: dict = Depends(verify_token)
):
    """Generate comprehensive financial insights using enhanced GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        result = await github_models_service.generate_financial_insights(
            financial_data=request.financial_data,
            period=request.period,
            company_size=request.company_size,
            industry=request.industry,
        )

        return {
            "success": True,
            "insights": result,
            "processed_by": current_user.get("username", "unknown"),
            "analysis_quality": result.get("analysis_quality", "unknown"),
            "trends_detected": len(result.get("trends", []))
        }

    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Insights generation failed: {str(e)}"
        )


# Enhanced report generation endpoint
@router.post("/generate-report")
async def generate_report(
    request: GenerateReportRequest, current_user: dict = Depends(verify_token)
):
    """Generate comprehensive financial report using enhanced GitHub Models AI"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        result = await github_models_service.generate_financial_report(
            financial_data=request.financial_data,
            report_type=request.report_type,
            period=request.period,
            company_name=request.company_name,
            context=request.context,
        )

        return {
            "success": True,
            "report": result,
            "processed_by": current_user.get("username", "unknown"),
            "generated_at": result.get("generated_at"),
            "analysis_quality": result.get("report_metadata", {}).get("analysis_quality", "unknown")
        }

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Report generation failed: {str(e)}"
        )


# Enhanced natural language query endpoint
@router.post("/query")
async def natural_language_query(
    request: NaturalLanguageQueryRequest, current_user: dict = Depends(verify_token)
):
    """Process natural language queries about financial data with enhanced understanding"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        result = await github_models_service.natural_language_query(
            query=request.query, context_data=request.context_data
        )

        return {
            "success": True,
            "response": result,
            "processed_by": current_user.get("username", "unknown"),
            "query_type": result.get("query_type", "general"),
            "confidence": result.get("confidence", 0.0)
        }

    except Exception as e:
        logger.error(f"Natural language query failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Query processing failed: {str(e)}"
        )


# New fraud detection endpoint
@router.post("/detect-fraud")
async def detect_fraud(
    request: FraudDetectionRequest, current_user: dict = Depends(verify_token)
):
    """Detect potential fraud patterns in financial transactions"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        result = await github_models_service.detect_fraud_patterns(
            transactions=request.transactions
        )

        return {
            "success": True,
            "fraud_analysis": result,
            "processed_by": current_user.get("username", "unknown"),
            "risk_level": result.get("risk_level", "unknown"),
            "confidence": result.get("confidence", 0.0)
        }

    except Exception as e:
        logger.error(f"Fraud detection failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Fraud detection failed: {str(e)}"
        )


# New compliance checking endpoint
@router.post("/check-compliance")
async def check_compliance(
    request: ComplianceCheckRequest, current_user: dict = Depends(verify_token)
):
    """Check financial data for regulatory compliance"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    try:
        result = await github_models_service.check_compliance(
            financial_data=request.financial_data,
            regulations=request.regulations
        )

        return {
            "success": True,
            "compliance_analysis": result,
            "processed_by": current_user.get("username", "unknown"),
            "overall_compliance": result.get("overall_compliance", False),
            "compliance_score": result.get("compliance_score", 0.0)
        }

    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Compliance check failed: {str(e)}"
        )


# Enhanced prompt template management endpoints
@router.get("/prompts")
async def list_prompts(current_user: dict = Depends(verify_token)):
    """List available prompt templates with enhanced capabilities"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    prompts = github_models_service.get_available_prompts()
    prompt_info = {}

    for prompt_name in prompts:
        prompt_info[prompt_name] = github_models_service.get_prompt_info(prompt_name)

    return {
        "success": True,
        "available_prompts": prompts,
        "prompt_details": prompt_info,
        "total_prompts": len(prompts),
        "enhanced_capabilities": True
    }


@router.get("/prompts/{prompt_name}")
async def get_prompt_info(prompt_name: str, current_user: dict = Depends(verify_token)):
    """Get detailed information about a specific prompt template"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    prompt_info = github_models_service.get_prompt_info(prompt_name)

    if not prompt_info:
        raise HTTPException(
            status_code=404, detail=f"Prompt template '{prompt_name}' not found"
        )

    return {"success": True, "prompt_name": prompt_name, "prompt_info": prompt_info}


# New endpoint to get expense categories
@router.get("/expense-categories")
async def get_expense_categories(current_user: dict = Depends(verify_token)):
    """Get available expense categories and their keywords"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    categories = github_models_service.get_expense_categories()
    
    return {
        "success": True,
        "expense_categories": categories,
        "total_categories": len(categories),
        "enhanced_categorization": True
    }


# New endpoint to get industry patterns
@router.get("/industry-patterns")
async def get_industry_patterns(current_user: dict = Depends(verify_token)):
    """Get industry-specific patterns for analysis"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    patterns = github_models_service.get_industry_patterns()
    
    return {
        "success": True,
        "industry_patterns": patterns,
        "total_industries": len(patterns),
        "enhanced_analysis": True
    }


# Enhanced batch processing endpoint
@router.post("/batch-analyze")
async def batch_analyze_documents(
    requests: List[AnalyzeDocumentRequest], current_user: dict = Depends(verify_token)
):
    """Batch analyze multiple documents with enhanced capabilities"""
    if not github_models_service.enabled:
        raise HTTPException(
            status_code=503, detail="GitHub Models service not available"
        )

    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 documents per batch")

    results = []

    for i, request in enumerate(requests):
        try:
            result = await github_models_service.analyze_financial_document(
                document_text=request.document_text, document_type=request.document_type
            )

            results.append({
                "index": i, 
                "success": True, 
                "analysis": result,
                "confidence": result.get("confidence", 0.0),
                "analysis_quality": result.get("analysis_quality", "unknown")
            })

        except Exception as e:
            logger.exception(f"Batch analysis failed for document {i}")
            results.append(
                {
                    "index": i,
                    "success": False,
                    "error": "Internal error during analysis",
                }
            )

    return {
        "success": True,
        "batch_results": results,
        "total_processed": len(results),
        "successful": len([r for r in results if r["success"]]),
        "failed": len([r for r in results if not r["success"]]),
        "processed_by": current_user.get("username", "unknown"),
        "enhanced_analysis": True
    }
