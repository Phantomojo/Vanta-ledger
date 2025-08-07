from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from datetime import datetime

from ..auth import AuthService
from ..utils.file_utils import secure_file_handler
from ..services.document_processor import DocumentProcessor
from ..config import settings

router = APIRouter(prefix="/upload/documents", tags=["Documents"])
document_processor = DocumentProcessor()

@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(AuthService.verify_token)
):
    """Upload and process a new document securely"""
    temp_file_path = None
    try:
        user_id = current_user.get("user_id", "unknown")

        temp_file_path, secure_filename = secure_file_handler.save_file_securely(
            file, user_id, settings.UPLOAD_DIR
        )

        result = document_processor.process_document(str(temp_file_path), file.filename)

        result["security"] = {
            "uploaded_by": user_id,
            "secure_filename": secure_filename,
            "original_filename": file.filename,
            "file_size": file.size,
            "upload_timestamp": datetime.now().isoformat()
        }

        return {
            "message": "Document uploaded and processed successfully",
            "doc_id": result['doc_id'],
            "original_filename": result['original_filename'],
            "type": result['analysis']['type'],
            "summary": result['analysis']['summary'],
            "security": result["security"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")
    finally:
        if temp_file_path:
            secure_file_handler.cleanup_temp_file(temp_file_path)

@router.get("")
async def list_documents(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(AuthService.verify_token)
):
    """List all processed documents with pagination"""
    documents = document_processor.list_documents()

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_docs = documents[start_idx:end_idx]

    return {
        "documents": paginated_docs,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(documents),
            "pages": (len(documents) + limit - 1) // limit
        }
    }

@router.get("/{document_id}")
async def get_document_details(
    document_id: str,
    current_user: dict = Depends(AuthService.verify_token)
):
    """Get detailed information about a specific document"""
    analysis = document_processor.get_document_analysis(document_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Document not found")

    content = document_processor.get_document_content(document_id)
    if not content:
        content = "Document content not available"

    return {
        "doc_id": document_id,
        "content": content,
        "analysis": analysis,
        "metadata": {
            "type": analysis.get('type'),
            "word_count": analysis.get('metadata', {}).get('word_count', 0),
            "processed_at": analysis.get('processed_at')
        }
    }

@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    current_user: dict = Depends(AuthService.verify_token)
):
    """Get raw text content of a document"""
    content = document_processor.get_document_content(document_id)
    if not content:
        raise HTTPException(status_code=404, detail="Document content not found")

    return {"content": content}

@router.post("/{document_id}/analyze")
async def reanalyze_document(
    document_id: str,
    current_user: dict = Depends(AuthService.verify_token)
):
    """Re-analyze a document with updated AI processing"""
    content = document_processor.get_document_content(document_id)
    if not content:
        raise HTTPException(status_code=404, detail="Document content not found")

    analysis = document_processor._analyze_document(content, document_id)
    document_processor._store_analysis(document_id, analysis)

    return {
        "message": "Document re-analyzed successfully",
        "doc_id": document_id,
        "analysis": analysis
    }
