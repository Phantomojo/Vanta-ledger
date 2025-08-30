#!/usr/bin/env python3
"""
Semantic Search API Routes
REST endpoints for intelligent document search and AI-assisted tagging
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..auth import get_current_user
from ..models.user_models import User
from ..services.semantic_search_service import semantic_search_service
from ..services.enhanced_document_service import enhanced_document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/semantic-search", tags=["Semantic Search"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class SearchFilters(BaseModel):
    """Search filters for semantic search"""
    date_from: Optional[str] = Field(None, description="Start date for filtering")
    date_to: Optional[str] = Field(None, description="End date for filtering")
    document_type: Optional[str] = Field(None, description="Document type filter")
    status: Optional[str] = Field(None, description="Document status filter")
    tags: Optional[List[str]] = Field(None, description="Tag filters")


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., description="Search query", min_length=1)
    filters: Optional[SearchFilters] = Field(None, description="Search filters")
    limit: int = Field(20, description="Maximum number of results", ge=1, le=100)
    threshold: float = Field(0.3, description="Minimum similarity threshold", ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Model for search result"""
    document: Dict[str, Any]
    similarity: float
    relevance_score: float
    matches: Optional[int] = None


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search"""
    query: str
    results: List[SearchResult]
    total_found: int
    search_time: float
    filters_applied: Dict[str, Any]
    search_method: str


class AITaggingRequest(BaseModel):
    """Request model for AI tagging"""
    document_id: str = Field(..., description="Document ID to tag")


class AITag(BaseModel):
    """Model for AI-generated tag"""
    tag: str
    confidence: float
    tag_type: str


class AITaggingResponse(BaseModel):
    """Response model for AI tagging"""
    document_id: str
    tags: List[AITag]
    generation_method: str
    timestamp: str


class SearchSuggestionResponse(BaseModel):
    """Response model for search suggestions"""
    suggestions: List[str]
    partial_query: str


class PopularSearchResponse(BaseModel):
    """Response model for popular searches"""
    popular_searches: List[Dict[str, Any]]
    days: int


class SearchCapabilitiesResponse(BaseModel):
    """Response model for search capabilities"""
    semantic_available: bool
    tagging_available: bool
    embedding_model_loaded: bool
    tagging_pipeline_loaded: bool
    gpu_available: bool
    search_features: List[str]


# ============================================================================
# SEMANTIC SEARCH ENDPOINTS
# ============================================================================


@router.post("/search", response_model=SemanticSearchResponse)
async def search_documents(
    request: SemanticSearchRequest = Body(...),
    current_user: User = Depends(get_current_user),
    company_id: str = Query(..., description="Company ID for search scope"),
):
    """
    Perform semantic search on documents
    
    This endpoint provides intelligent document search inspired by Paperless-AI,
    including semantic understanding and relevance scoring.
    """
    try:
        # Validate company access
        if not current_user.has_company_access(company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to specified company"
            )

        # Convert filters to dict
        filters_dict = None
        if request.filters:
            filters_dict = request.filters.dict(exclude_none=True)

        # Perform semantic search
        results = await semantic_search_service.semantic_search(
            query=request.query,
            company_id=UUID(company_id),
            user_id=current_user.id,
            filters=filters_dict,
            limit=request.limit,
            threshold=request.threshold
        )

        # Convert results to response format
        search_results = []
        for result in results.get("results", []):
            search_results.append(SearchResult(
                document=result["document"],
                similarity=result["similarity"],
                relevance_score=result["relevance_score"],
                matches=result.get("matches")
            ))

        return SemanticSearchResponse(
            query=results["query"],
            results=search_results,
            total_found=results["total_found"],
            search_time=results["search_time"],
            filters_applied=results["filters_applied"],
            search_method=results["search_method"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform semantic search: {str(e)}"
        )


@router.post("/generate-tags", response_model=AITaggingResponse)
async def generate_ai_tags(
    request: AITaggingRequest = Body(...),
    current_user: User = Depends(get_current_user),
):
    """
    Generate AI-assisted tags for a document
    
    This endpoint uses AI to automatically generate relevant tags for documents,
    improving categorization and searchability.
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

        # Generate AI tags
        result = await semantic_search_service.generate_ai_tags(UUID(request.document_id))
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        # Convert tags to response format
        ai_tags = []
        for tag in result["tags"]:
            ai_tags.append(AITag(
                tag=tag["tag"],
                confidence=tag["confidence"],
                tag_type=tag["tag_type"]
            ))

        return AITaggingResponse(
            document_id=result["document_id"],
            tags=ai_tags,
            generation_method=result["generation_method"],
            timestamp=result["timestamp"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI tags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI tags: {str(e)}"
        )


@router.get("/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    partial_query: str = Query(..., description="Partial search query"),
    current_user: User = Depends(get_current_user),
    company_id: str = Query(..., description="Company ID for suggestions"),
):
    """
    Get search suggestions based on partial query
    
    This endpoint provides intelligent search suggestions based on
    previous searches and document content.
    """
    try:
        # Validate company access
        if not current_user.has_company_access(company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to specified company"
            )

        # Get search suggestions
        suggestions = await semantic_search_service.get_search_suggestions(
            partial_query=partial_query,
            company_id=UUID(company_id)
        )

        return SearchSuggestionResponse(
            suggestions=suggestions,
            partial_query=partial_query
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search suggestions: {str(e)}"
        )


@router.get("/popular", response_model=PopularSearchResponse)
async def get_popular_searches(
    current_user: User = Depends(get_current_user),
    company_id: str = Query(..., description="Company ID for popular searches"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
):
    """
    Get popular search queries for a company
    
    This endpoint provides analytics on popular search queries,
    helping users discover trending topics.
    """
    try:
        # Validate company access
        if not current_user.has_company_access(company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to specified company"
            )

        # Get popular searches
        popular_searches = await semantic_search_service.get_popular_searches(
            company_id=UUID(company_id),
            days=days
        )

        return PopularSearchResponse(
            popular_searches=popular_searches,
            days=days
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting popular searches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get popular searches: {str(e)}"
        )


@router.get("/capabilities", response_model=SearchCapabilitiesResponse)
async def get_search_capabilities():
    """
    Get current search capabilities and system status
    
    This endpoint provides information about available search features
    and system capabilities.
    """
    try:
        capabilities = semantic_search_service.get_search_capabilities()
        
        return SearchCapabilitiesResponse(**capabilities)

    except Exception as e:
        logger.error(f"Error getting search capabilities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search capabilities: {str(e)}"
        )


@router.post("/batch-tag")
async def batch_generate_tags(
    document_ids: List[str] = Body(...),
    current_user: User = Depends(get_current_user),
):
    """
    Generate AI tags for multiple documents
    
    This endpoint allows batch tagging of multiple documents,
    improving efficiency for large document sets.
    """
    try:
        if not document_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No document IDs provided"
            )

        if len(document_ids) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 documents allowed per batch"
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

        # Generate tags for each document
        results = []
        for document in documents:
            try:
                result = await semantic_search_service.generate_ai_tags(document.id)
                results.append({
                    "document_id": str(document.id),
                    "success": True,
                    "result": result
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
            "successful_tagging": len([r for r in results if r["success"]]),
            "failed_tagging": len([r for r in results if not r["success"]])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch tagging: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch generate tags: {str(e)}"
        )


@router.get("/health")
async def semantic_search_health_check():
    """
    Health check for semantic search service
    """
    try:
        capabilities = semantic_search_service.get_search_capabilities()
        
        # Determine overall health
        health_status = "healthy"
        if not capabilities["semantic_available"] and not capabilities["tagging_available"]:
            health_status = "degraded"
        
        return {
            "service": "semantic_search_service",
            "status": health_status,
            "version": "1.0.0",
            "capabilities": capabilities,
            "features": [
                "semantic_search",
                "ai_tagging",
                "search_suggestions",
                "popular_searches",
                "search_analytics"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Semantic search service is unhealthy"
        )
