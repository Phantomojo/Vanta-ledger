#!/usr/bin/env python3
"""
Enhanced Document Management API Routes
Advanced document management endpoints with tagging, categorization, search, and analytics
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..auth import User, get_current_user
from ..models.document_models import (
    DocumentCategory,
    DocumentPriority,
    DocumentSearchCriteria,
    DocumentStatus,
    DocumentTag,
    DocumentType,
)
from ..services.enhanced_document_service import enhanced_document_service
from ..utils.validation import input_validator

router = APIRouter(prefix="/api/v2/documents", tags=["Enhanced Document Management"])

# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================================


@router.post("/")
async def create_enhanced_document(
    document_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Create a new enhanced document with metadata"""
    try:
        document = enhanced_document_service.create_document(
            document_data, current_user.id
        )
        return {
            "success": True,
            "document": document.dict(),
            "message": "Document created successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}",
        )


@router.get("/{document_id}")
async def get_enhanced_document(
    document_id: str, current_user: User = Depends(get_current_user)
):
    """Get enhanced document by ID with access tracking"""
    try:
        doc_id = input_validator.validate_uuid(document_id, "document_id")
        document = enhanced_document_service.get_document(doc_id, current_user.id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        return {"success": True, "document": document.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}",
        )


@router.get("/")
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: User = Depends(get_current_user),
):
    """List documents with advanced filtering and pagination"""
    try:
        # Build search criteria
        criteria = DocumentSearchCriteria(
            page=page, limit=limit, sort_by=sort_by, sort_order=sort_order
        )

        # Add filters
        if document_type:
            try:
                doc_type = DocumentType(document_type)
                criteria.document_types = [doc_type]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid document type: {document_type}",
                )

        if status:
            try:
                doc_status = DocumentStatus(status)
                criteria.status = [doc_status]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}",
                )

        if category_id:
            criteria.category_id = input_validator.validate_uuid(
                category_id, "category_id"
            )

        if created_by:
            criteria.created_by = input_validator.validate_uuid(
                created_by, "created_by"
            )

        # Execute search
        documents, total_count = enhanced_document_service.search_documents(
            criteria, current_user.id
        )

        return {
            "success": True,
            "documents": [doc.dict() for doc in documents],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )


@router.post("/search")
async def advanced_search(
    search_criteria: DocumentSearchCriteria = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Advanced document search with full criteria"""
    try:
        documents, total_count = enhanced_document_service.search_documents(
            search_criteria, current_user.id
        )

        return {
            "success": True,
            "documents": [doc.dict() for doc in documents],
            "pagination": {
                "page": search_criteria.page,
                "limit": search_criteria.limit,
                "total": total_count,
                "total_pages": (total_count + search_criteria.limit - 1)
                // search_criteria.limit,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


# ============================================================================
# TAGGING ENDPOINTS
# ============================================================================


@router.post("/tags")
async def create_tag(
    tag_data: Dict[str, Any] = Body(...), current_user: User = Depends(get_current_user)
):
    """Create a new document tag"""
    try:
        tag = enhanced_document_service.create_tag(tag_data, current_user.id)
        return {
            "success": True,
            "tag": tag.dict(),
            "message": "Tag created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tag: {str(e)}",
        )


@router.get("/tags")
async def list_tags(
    include_system: bool = Query(True, description="Include system-generated tags"),
    current_user: User = Depends(get_current_user),
):
    """List all document tags"""
    try:
        tags = enhanced_document_service.get_tags(include_system=include_system)
        return {"success": True, "tags": [tag.dict() for tag in tags]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tags: {str(e)}",
        )


@router.post("/{document_id}/tags/{tag_id}")
async def add_tag_to_document(
    document_id: str, tag_id: str, current_user: User = Depends(get_current_user)
):
    """Add a tag to a document"""
    try:
        doc_id = input_validator.validate_uuid(document_id, "document_id")
        tag_uuid = input_validator.validate_uuid(tag_id, "tag_id")

        # Get document and add tag
        document = enhanced_document_service.get_document(doc_id, current_user.id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        document.add_tag(tag_uuid)

        # Update in database
        enhanced_document_service.documents.update_one(
            {"_id": str(doc_id)},
            {
                "$set": {
                    "metadata.tags": document.metadata.tags,
                    "modified_at": document.modified_at,
                }
            },
        )

        return {"success": True, "message": "Tag added to document successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add tag: {str(e)}",
        )


@router.delete("/{document_id}/tags/{tag_id}")
async def remove_tag_from_document(
    document_id: str, tag_id: str, current_user: User = Depends(get_current_user)
):
    """Remove a tag from a document"""
    try:
        doc_id = input_validator.validate_uuid(document_id, "document_id")
        tag_uuid = input_validator.validate_uuid(tag_id, "tag_id")

        # Get document and remove tag
        document = enhanced_document_service.get_document(doc_id, current_user.id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        document.remove_tag(tag_uuid)

        # Update in database
        enhanced_document_service.documents.update_one(
            {"_id": str(doc_id)},
            {
                "$set": {
                    "metadata.tags": document.metadata.tags,
                    "modified_at": document.modified_at,
                }
            },
        )

        return {"success": True, "message": "Tag removed from document successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove tag: {str(e)}",
        )


# ============================================================================
# CATEGORY ENDPOINTS
# ============================================================================


@router.post("/categories")
async def create_category(
    category_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Create a new document category"""
    try:
        category = enhanced_document_service.create_category(
            category_data, current_user.id
        )
        return {
            "success": True,
            "category": category.dict(),
            "message": "Category created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}",
        )


@router.get("/categories")
async def list_categories(
    include_system: bool = Query(
        True, description="Include system-generated categories"
    ),
    current_user: User = Depends(get_current_user),
):
    """List all document categories"""
    try:
        categories = enhanced_document_service.get_categories(
            include_system=include_system
        )
        return {"success": True, "categories": [cat.dict() for cat in categories]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list categories: {str(e)}",
        )


@router.put("/{document_id}/category")
async def set_document_category(
    document_id: str,
    category_id: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Set the category for a document"""
    try:
        doc_id = input_validator.validate_uuid(document_id, "document_id")
        cat_uuid = input_validator.validate_uuid(category_id, "category_id")

        # Get document and set category
        document = enhanced_document_service.get_document(doc_id, current_user.id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        document.set_category(cat_uuid)

        # Update in database
        enhanced_document_service.documents.update_one(
            {"_id": str(doc_id)},
            {
                "$set": {
                    "metadata.category_id": str(cat_uuid),
                    "modified_at": document.modified_at,
                }
            },
        )

        return {"success": True, "message": "Document category updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update category: {str(e)}",
        )


# ============================================================================
# ANALYTICS AND STATISTICS ENDPOINTS
# ============================================================================


@router.get("/statistics/overview")
async def get_document_statistics(current_user: User = Depends(get_current_user)):
    """Get comprehensive document statistics"""
    try:
        stats = enhanced_document_service.get_document_statistics(current_user.id)

        # Format storage size
        total_bytes = stats.get("total_storage_bytes", 0)
        if total_bytes > 1024**3:
            storage_size = f"{total_bytes / (1024**3):.2f} GB"
        elif total_bytes > 1024**2:
            storage_size = f"{total_bytes / (1024**2):.2f} MB"
        elif total_bytes > 1024:
            storage_size = f"{total_bytes / 1024:.2f} KB"
        else:
            storage_size = f"{total_bytes} bytes"

        stats["storage_size_formatted"] = storage_size

        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        )


@router.get("/statistics/by-type")
async def get_documents_by_type(current_user: User = Depends(get_current_user)):
    """Get document count by type"""
    try:
        stats = enhanced_document_service.get_document_statistics(current_user.id)
        return {"success": True, "by_type": stats.get("by_type", {})}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get type statistics: {str(e)}",
        )


@router.get("/statistics/by-status")
async def get_documents_by_status(current_user: User = Depends(get_current_user)):
    """Get document count by status"""
    try:
        stats = enhanced_document_service.get_document_statistics(current_user.id)
        return {"success": True, "by_status": stats.get("by_status", {})}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status statistics: {str(e)}",
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@router.get("/types")
async def get_document_types():
    """Get all available document types"""
    return {"success": True, "document_types": [dt.value for dt in DocumentType]}


@router.get("/statuses")
async def get_document_statuses():
    """Get all available document statuses"""
    return {"success": True, "statuses": [ds.value for ds in DocumentStatus]}


@router.get("/priorities")
async def get_document_priorities():
    """Get all available document priorities"""
    return {"success": True, "priorities": [dp.value for dp in DocumentPriority]}


@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Search query"),
    current_user: User = Depends(get_current_user),
):
    """Get search suggestions based on query"""
    try:
        # Simple implementation - can be enhanced with more sophisticated suggestions
        suggestions = {
            "document_types": [
                dt.value for dt in DocumentType if query.lower() in dt.value.lower()
            ],
            "tags": [],
            "categories": [],
        }

        # Get matching tags
        tags = enhanced_document_service.get_tags()
        suggestions["tags"] = [
            tag.name for tag in tags if query.lower() in tag.name.lower()
        ]

        # Get matching categories
        categories = enhanced_document_service.get_categories()
        suggestions["categories"] = [
            cat.name for cat in categories if query.lower() in cat.name.lower()
        ]

        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}",
        )
