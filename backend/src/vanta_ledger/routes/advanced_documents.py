import os
#!/usr/bin/env python3
"""
Advanced Documents API Routes
REST endpoints for advanced document processing with layout understanding
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status, UploadFile, File
from pydantic import BaseModel, Field

from ..auth import get_current_user
from ..models.user_models import User
from ..services.advanced_document_processor import advanced_document_processor
from ..services.enhanced_document_service import enhanced_document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced-documents", tags=["Advanced Document Processing"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class ProcessingOptions(BaseModel):
    """Advanced document processing options"""
    process_handwritten: bool = Field(False, description="Process handwritten text")
    enable_layout_analysis: bool = Field(True, description="Enable layout analysis")
    enable_advanced_ocr: bool = Field(True, description="Enable advanced OCR")
    confidence_threshold: float = Field(0.7, description="Minimum confidence threshold")


class AdvancedProcessingRequest(BaseModel):
    """Request model for advanced document processing"""
    document_id: str = Field(..., description="Document ID to process")
    processing_options: Optional[ProcessingOptions] = Field(None, description="Processing options")


class AdvancedProcessingResponse(BaseModel):
    """Response model for advanced document processing"""
    success: bool
    document_id: str
    processing_timestamp: str
    extracted_text: str
    layout_analysis: Dict[str, Any]
    confidence_scores: Dict[str, float]
    processing_errors: List[str]
    processing_methods: List[str]


class LayoutAnalysisResponse(BaseModel):
    """Response model for layout analysis"""
    layout_type: str
    regions: List[Dict[str, Any]]
    confidence: float
    processing_method: str


class ProcessingCapabilitiesResponse(BaseModel):
    """Response model for processing capabilities"""
    ml_available: bool
    ocr_available: bool
    layout_model_loaded: bool
    gpu_available: bool
    processing_features: List[str]


# ============================================================================
# ADVANCED DOCUMENT PROCESSING ENDPOINTS
# ============================================================================


@router.post("/process", response_model=AdvancedProcessingResponse)
async def process_document_advanced(
    request: AdvancedProcessingRequest = Body(...),
    current_user: User = Depends(get_current_user),
):
    """
    Process document with advanced layout understanding and OCR
    
    This endpoint provides enhanced document processing inspired by Docling + Documind,
    including layout analysis, advanced OCR, and handwritten text processing.
    """
    try:
        # Validate document access
        document = await enhanced_document_service.get_document(UUID(request.document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check user access to document
        if not current_user.has_company_access(document.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this document"
            )

        # Process document with advanced processor
        processing_options = request.processing_options.dict() if request.processing_options else {}
        results = await advanced_document_processor.process_complex_document(
            document, processing_options
        )

        # Extract processing methods used
        processing_methods = []
        if results.get("extracted_text"):
            processing_methods.append("advanced_ocr")
        if results.get("layout_analysis"):
            processing_methods.append("layout_analysis")
        if results.get("handwritten_text"):
            processing_methods.append("handwritten_processing")

        return AdvancedProcessingResponse(
            success=True,
            document_id=results["document_id"],
            processing_timestamp=results["processing_timestamp"],
            extracted_text=results.get("extracted_text", ""),
            layout_analysis=results.get("layout_analysis", {}),
            confidence_scores=results.get("confidence_scores", {}),
            processing_errors=results.get("processing_errors", []),
            processing_methods=processing_methods
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in advanced document processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/{document_id}/analysis", response_model=Dict[str, Any])
async def get_document_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get advanced analysis results for a document
    """
    try:
        # Validate document access
        document = await enhanced_document_service.get_document(UUID(document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check user access to document
        if not current_user.has_company_access(document.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this document"
            )

        # Get analysis results
        analysis = await advanced_document_processor.get_document_analysis(UUID(document_id))
        
        if "error" in analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analysis["error"]
            )

        return {
            "success": True,
            "document_id": document_id,
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document analysis: {str(e)}"
        )


@router.get("/{document_id}/layout", response_model=LayoutAnalysisResponse)
async def get_layout_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get layout analysis for a document
    """
    try:
        # Validate document access
        document = await enhanced_document_service.get_document(UUID(document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check user access to document
        if not current_user.has_company_access(document.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this document"
            )

        # Get layout analysis
        layout_analysis = await advanced_document_processor.get_layout_analysis(UUID(document_id))
        
        if "error" in layout_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=layout_analysis["error"]
            )

        return LayoutAnalysisResponse(**layout_analysis)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting layout analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get layout analysis: {str(e)}"
        )


@router.get("/capabilities", response_model=ProcessingCapabilitiesResponse)
async def get_processing_capabilities():
    """
    Get current processing capabilities and system status
    """
    try:
        capabilities = advanced_document_processor.get_processing_capabilities()
        
        return ProcessingCapabilitiesResponse(**capabilities)

    except Exception as e:
        logger.error(f"Error getting processing capabilities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing capabilities: {str(e)}"
        )


@router.post("/upload-and-process")
async def upload_and_process_advanced(
    file: UploadFile = File(...),
    process_handwritten: bool = Query(False, description="Process handwritten text"),
    enable_layout_analysis: bool = Query(True, description="Enable layout analysis"),
    current_user: User = Depends(get_current_user),
    company_id: str = Query(..., description="Company ID for the document"),
):
    """
    Upload and process document with advanced processing
    
    This endpoint combines document upload with advanced processing in a single operation.
    """
    try:
        # Validate company access
        if not current_user.has_company_access(company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to specified company"
            )

        # Upload document first
        document = await enhanced_document_service.upload_document(
            file, current_user.id, UUID(company_id)
        )

        # Process with advanced processor
        processing_options = {
            "process_handwritten": process_handwritten,
            "enable_layout_analysis": enable_layout_analysis,
            "enable_advanced_ocr": True
        }

        results = await advanced_document_processor.process_complex_document(
            document, processing_options
        )

        return {
            "success": True,
            "document": document.dict(),
            "processing_results": results,
            "message": "Document uploaded and processed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload and process: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload and process document: {str(e)}"
        )


@router.post("/batch-process")
async def batch_process_documents(
    document_ids: List[str] = Body(...),
    processing_options: Optional[ProcessingOptions] = Body(None),
    current_user: User = Depends(get_current_user),
):
    """
    Process multiple documents with advanced processing
    
    This endpoint allows batch processing of multiple documents with the same options.
    """
    try:
        if not document_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No document IDs provided"
            )

        if len(document_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 documents allowed per batch"
            )

        # Validate all documents and user access
        documents = []
        for doc_id in document_ids:
            document = await enhanced_document_service.get_document(UUID(doc_id))
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document {doc_id} not found"
                )
            
            if not current_user.has_company_access(document.company_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to document {doc_id}"
                )
            
            documents.append(document)

        # Process each document
        results = []
        processing_options_dict = processing_options.dict() if processing_options else {}
        
        for document in documents:
            try:
                result = await advanced_document_processor.process_complex_document(
                    document, processing_options_dict
                )
                results.append({
                    "document_id": str(document.id),
                    "success": True,
                    "results": result
                })
            except Exception as e:
                results.append({
                    "document_id": str(document.id),
                    "success": False,
                    "error": str(e)
                })

        return {
            "success": True,
            "batch_results": results,
            "total_documents": len(documents),
            "successful_processing": len([r for r in results if r["success"]]),
            "failed_processing": len([r for r in results if not r["success"]])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch process documents: {str(e)}"
        )


@router.get("/health")
async def advanced_document_health_check():
    """
    Health check for advanced document processing service
    """
    try:
        capabilities = advanced_document_processor.get_processing_capabilities()
        
        # Determine overall health
        health_status = "healthy"
        if not capabilities["ml_available"] and not capabilities["ocr_available"]:
            health_status = "degraded"
        
        return {
            "service": "advanced_document_processor",
            "status": health_status,
            "version": "1.0.0",
            "capabilities": capabilities,
            "features": [
                "advanced_ocr",
                "layout_analysis",
                "handwritten_text_processing",
                "complex_layout_understanding"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Advanced document processing service is unhealthy"
        )
