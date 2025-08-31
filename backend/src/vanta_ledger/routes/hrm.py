#!/usr/bin/env python3
"""
HRM (Hierarchical Reasoning Model) API Routes
Provides REST API endpoints for advanced hierarchical reasoning capabilities
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import verify_token
from ..services.hrm_service import hrm_service, HRMReasoningResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/hrm", tags=["HRM (Hierarchical Reasoning Model)"])


# Pydantic models for request/response
class DocumentAnalysisRequest(BaseModel):
    document_text: str = Field(..., description="Text content of the document to analyze")
    document_type: str = Field(default="invoice", description="Type of document (invoice, receipt, contract, etc.)")
    company_id: str = Field(..., description="Company identifier")
    business_context: Optional[Dict[str, Any]] = Field(default=None, description="Company-specific business context")


class BusinessRuleRequest(BaseModel):
    rule_name: str = Field(..., description="Name of the business rule")
    rule_conditions: Dict[str, Any] = Field(..., description="Conditions for the rule")
    rule_actions: List[str] = Field(..., description="Actions to take when rule is triggered")


class ComplianceCheckRequest(BaseModel):
    document_type: str = Field(..., description="Type of document to check")
    regulations: List[str] = Field(default=["basic_accounting", "tax_compliance"], description="Regulations to check")
    company_id: str = Field(..., description="Company identifier")


class RiskAssessmentRequest(BaseModel):
    document_text: str = Field(..., description="Document text for risk assessment")
    transaction_amount: Optional[float] = Field(None, description="Transaction amount")
    vendor_name: Optional[str] = Field(None, description="Vendor name")
    company_id: str = Field(..., description="Company identifier")


# Health check endpoint
@router.get("/health")
async def hrm_health():
    """Check HRM service health and capabilities"""
    try:
        status = await hrm_service.get_service_status()
        return {
            "service": "HRM (Hierarchical Reasoning Model)",
            "status": status['status'],
            "model_loaded": status['model_loaded'],
            "device": status['device'],
            "capabilities": status['capabilities'],
            "model_path": status['model_path'],
            "company_contexts": status['company_contexts']
        }
    except Exception as e:
        logger.error(f"HRM health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"HRM service unavailable: {str(e)}")


# Document analysis endpoint
@router.post("/analyze-document")
async def analyze_document(
    request: DocumentAnalysisRequest, 
    current_user: dict = Depends(verify_token)
):
    """Analyze financial document using HRM hierarchical reasoning"""
    try:
        result = await hrm_service.analyze_financial_document(
            document_text=request.document_text,
            document_type=request.document_type,
            company_id=request.company_id,
            business_context=request.business_context
        )
        
        return {
            "success": True,
            "analysis": {
                "decision": result.decision,
                "confidence": result.confidence,
                "reasoning_trail": result.reasoning_trail,
                "business_rules_applied": result.business_rules_applied,
                "compliance_checks": result.compliance_checks,
                "risk_assessment": result.risk_assessment,
                "recommendations": result.recommendations,
                "processing_time": result.processing_time
            },
            "processed_by": current_user.get("username", "unknown"),
            "hrm_model_used": True
        }
        
    except Exception as e:
        logger.error(f"HRM document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Business rule application endpoint
@router.post("/apply-business-rules")
async def apply_business_rules(
    request: BusinessRuleRequest,
    current_user: dict = Depends(verify_token)
):
    """Apply business rules using HRM reasoning"""
    try:
        # Create a mock document for rule application
        mock_document = f"Rule: {request.rule_name}, Conditions: {request.rule_conditions}"
        
        result = await hrm_service.analyze_financial_document(
            document_text=mock_document,
            document_type="business_rule",
            company_id="system",
            business_context={"business_rules": {request.rule_name: request.rule_conditions}}
        )
        
        return {
            "success": True,
            "rule_application": {
                "rule_name": request.rule_name,
                "decision": result.decision,
                "confidence": result.confidence,
                "business_rules_applied": result.business_rules_applied,
                "recommendations": result.recommendations
            },
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"HRM business rule application failed: {e}")
        raise HTTPException(status_code=500, detail=f"Rule application failed: {str(e)}")


# Compliance checking endpoint
@router.post("/check-compliance")
async def check_compliance(
    request: ComplianceCheckRequest,
    current_user: dict = Depends(verify_token)
):
    """Check compliance using HRM reasoning"""
    try:
        # Create a mock document for compliance checking
        mock_document = f"Document Type: {request.document_type}, Regulations: {request.regulations}"
        
        result = await hrm_service.analyze_financial_document(
            document_text=mock_document,
            document_type=request.document_type,
            company_id=request.company_id,
            business_context={"compliance_rules": request.regulations}
        )
        
        return {
            "success": True,
            "compliance_analysis": {
                "document_type": request.document_type,
                "regulations_checked": request.regulations,
                "compliance_checks": result.compliance_checks,
                "overall_compliance": all(check.get('status') == 'pass' for check in result.compliance_checks),
                "recommendations": result.recommendations
            },
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"HRM compliance check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")


# Risk assessment endpoint
@router.post("/assess-risk")
async def assess_risk(
    request: RiskAssessmentRequest,
    current_user: dict = Depends(verify_token)
):
    """Assess risk using HRM reasoning"""
    try:
        # Create document text with risk factors
        risk_document = f"Document: {request.document_text}"
        if request.transaction_amount:
            risk_document += f", Amount: {request.transaction_amount}"
        if request.vendor_name:
            risk_document += f", Vendor: {request.vendor_name}"
        
        result = await hrm_service.analyze_financial_document(
            document_text=risk_document,
            document_type="risk_assessment",
            company_id=request.company_id,
            business_context={"risk_factors": ["amount", "vendor", "content"]}
        )
        
        return {
            "success": True,
            "risk_assessment": {
                "risk_level": result.risk_assessment.get('level', 'unknown'),
                "risk_score": result.risk_assessment.get('score', 0.0),
                "risk_factors": result.risk_assessment.get('factors', []),
                "recommendations": result.risk_assessment.get('recommendations', []),
                "confidence": result.confidence
            },
            "processed_by": current_user.get("username", "unknown")
        }
        
    except Exception as e:
        logger.error(f"HRM risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


# Model loading endpoint
@router.post("/load-model")
async def load_model(current_user: dict = Depends(verify_token)):
    """Load the HRM model"""
    try:
        success = await hrm_service.load_model()
        
        if success:
            return {
                "success": True,
                "message": "HRM model loaded successfully",
                "model_loaded": True,
                "device": hrm_service.device
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to load HRM model")
            
    except Exception as e:
        logger.error(f"HRM model loading failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")


# Reasoning trail endpoint
@router.get("/reasoning-trail/{analysis_id}")
async def get_reasoning_trail(
    analysis_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get reasoning trail for a specific analysis"""
    try:
        # This would typically retrieve from database
        # For now, return a sample reasoning trail
        sample_trail = [
            {
                "level": "H",
                "step": 0,
                "reasoning": "High-level business context analysis",
                "confidence": 0.95
            },
            {
                "level": "L",
                "step": 0,
                "reasoning": "Document structure and content extraction",
                "confidence": 0.88
            },
            {
                "level": "H",
                "step": 1,
                "reasoning": "Business rule application and compliance checking",
                "confidence": 0.92
            }
        ]
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "reasoning_trail": sample_trail,
            "total_steps": len(sample_trail),
            "h_level_steps": len([step for step in sample_trail if step['level'] == 'H']),
            "l_level_steps": len([step for step in sample_trail if step['level'] == 'L'])
        }
        
    except Exception as e:
        logger.error(f"Failed to get reasoning trail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reasoning trail: {str(e)}")


# Batch analysis endpoint
@router.post("/batch-analyze")
async def batch_analyze_documents(
    requests: List[DocumentAnalysisRequest],
    current_user: dict = Depends(verify_token)
):
    """Batch analyze multiple documents using HRM"""
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 documents per batch")
    
    results = []
    
    for i, request in enumerate(requests):
        try:
            result = await hrm_service.analyze_financial_document(
                document_text=request.document_text,
                document_type=request.document_type,
                company_id=request.company_id,
                business_context=request.business_context
            )
            
            results.append({
                "index": i,
                "success": True,
                "analysis": {
                    "decision": result.decision,
                    "confidence": result.confidence,
                    "risk_level": result.risk_assessment.get('level', 'unknown'),
                    "processing_time": result.processing_time
                }
            })
            
        except Exception as e:
            logger.exception(f"Batch analysis failed for document {i}")
            results.append({
                "index": i,
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": True,
        "batch_results": results,
        "total_processed": len(results),
        "successful": len([r for r in results if r["success"]]),
        "failed": len([r for r in results if not r["success"]]),
        "processed_by": current_user.get("username", "unknown")
    }


# Model capabilities endpoint
@router.get("/capabilities")
async def get_capabilities(current_user: dict = Depends(verify_token)):
    """Get HRM model capabilities"""
    try:
        status = await hrm_service.get_service_status()
        
        return {
            "success": True,
            "capabilities": status['capabilities'],
            "model_info": {
                "model_loaded": status['model_loaded'],
                "device": status['device'],
                "model_path": status['model_path']
            },
            "hierarchical_reasoning": {
                "h_level": "High-level business reasoning and decision making",
                "l_level": "Low-level document processing and pattern recognition",
                "cycles": "Multi-cycle reasoning for complex financial tasks",
                "adaptability": "Company-specific learning and rule application"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")
