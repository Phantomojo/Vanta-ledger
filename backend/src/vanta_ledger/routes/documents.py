from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ..auth import AuthService
from ..config import settings
from ..services.document_processor import DocumentProcessor
from ..utils.file_utils import secure_file_handler

router = APIRouter(prefix="/upload/documents", tags=["Documents"])

def get_document_processor():
    """Get a document processor instance"""
    return DocumentProcessor()


@router.post("")
async def upload_document(
    file: UploadFile = File(...), current_user: dict = Depends(AuthService.verify_token)
):
    """
    Handles secure upload and processing of a document file.

    Accepts a file upload, saves it securely, processes the document, and returns metadata including analysis results and security information. Raises an HTTP 500 error if processing fails.
    """
    temp_file_path = None
    try:
        user_id = current_user.get("user_id", "unknown")

        temp_file_path, secure_filename = secure_file_handler.save_file_securely(
            file, user_id, settings.UPLOAD_DIR
        )

        document_processor = get_document_processor()
        result = document_processor.process_document(str(temp_file_path), file.filename)

        result["security"] = {
            "uploaded_by": user_id,
            "secure_filename": secure_filename,
            "original_filename": file.filename,
            "file_size": file.size,
            "upload_timestamp": datetime.now().isoformat(),
        }

        return {
            "message": "Document uploaded and processed successfully",
            "doc_id": result["doc_id"],
            "original_filename": result["original_filename"],
            "type": result["analysis"]["type"],
            "summary": result["analysis"]["summary"],
            "security": result["security"],
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Document processing failed") from e
    finally:
        if temp_file_path:
            secure_file_handler.cleanup_temp_file(temp_file_path)


@router.get("")
async def list_documents(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Retrieve a paginated list of all processed documents.

    Parameters:
        page (int): The page number to retrieve.
        limit (int): The maximum number of documents per page.

    Returns:
        dict: A dictionary containing the list of documents for the requested page and pagination metadata.
    """
    document_processor = get_document_processor()
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
            "pages": (len(documents) + limit - 1) // limit,
        },
    }


@router.get("/{document_id}")
async def get_document_details(
    document_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Retrieve detailed analysis and metadata for a specific document by its ID.

    Returns:
        dict: A dictionary containing the document ID, content (or a placeholder if unavailable), analysis results, and metadata such as type, word count, and processing timestamp.

    Raises:
        HTTPException: If the document is not found.
    """
    document_processor = get_document_processor()
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
            "type": analysis.get("type"),
            "word_count": analysis.get("metadata", {}).get("word_count", 0),
            "processed_at": analysis.get("processed_at"),
        },
    }


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Retrieve the raw text content of a document by its ID.

    Raises:
        HTTPException: If the document content is not found.

    Returns:
        dict: A dictionary containing the document's raw content under the "content" key.
    """
    document_processor = get_document_processor()
    content = document_processor.get_document_content(document_id)
    if not content:
        raise HTTPException(status_code=404, detail="Document content not found")

    return {"content": content}


@router.post("/{document_id}/analyze")
async def reanalyze_document(
    document_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Re-analyzes an existing document using updated AI processing and stores the new analysis.

    Parameters:
        document_id (str): The unique identifier of the document to re-analyze.

    Returns:
        dict: A message indicating success, the document ID, and the updated analysis results.

    Raises:
        HTTPException: If the document content is not found.
    """
    document_processor = get_document_processor()
    content = document_processor.get_document_content(document_id)
    if not content:
        raise HTTPException(status_code=404, detail="Document content not found")

    analysis = document_processor._analyze_document(content, document_id)
    document_processor._store_analysis(document_id, analysis)

    return {
        "message": "Document re-analyzed successfully",
        "doc_id": document_id,
        "analysis": analysis,
    }
