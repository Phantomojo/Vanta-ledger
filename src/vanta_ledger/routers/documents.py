from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models
from ..schemas.document import DocumentCreate, DocumentRead
import os
from datetime import datetime
from ..force_scan import ForceScanner
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/documents", tags=["documents"])
force_scanner = ForceScanner()

# Directory for storing uploaded files
BASE_DOCS_DIR = "docs"  # Change as needed for your deployment

@router.post("/upload", response_model=DocumentRead)
def upload_document(
    project_id: Optional[int] = Form(None),
    company_id: Optional[int] = Form(None),
    doc_type: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    version_number: int = Form(1),
    uploader_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new document or version for a project/company.
    Stores the file in a structured folder, and records metadata for easy retrieval during tenders or audits.
    """
    # Build file path: docs/<company_id>/<project_id>/<filename>_v<version>_<timestamp>
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{os.path.splitext(file.filename)[0]}_v{version_number}_{timestamp}{os.path.splitext(file.filename)[1]}"
    company_folder = str(company_id) if company_id else "general"
    project_folder = str(project_id) if project_id else "general"
    dir_path = os.path.join(BASE_DOCS_DIR, company_folder, project_folder)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, safe_filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    # Parse expiry_date if provided
    expiry = None
    if expiry_date:
        try:
            expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except Exception:
            pass
    db_doc = models.Document(
        project_id=project_id,
        company_id=company_id,
        filename=file.filename,
        file_path=file_path,
        version_number=version_number,
        uploader_id=uploader_id,
        uploaded_at=datetime.now(),
        notes=notes,
        doc_type=doc_type,
        expiry_date=expiry
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@router.get("/", response_model=List[DocumentRead])
def list_documents(db: Session = Depends(get_db)):
    """
    List all documents in the system.
    Lets the family see every document available for tenders, audits, or compliance.
    """
    return db.query(models.Document).all()

@router.get("/{doc_id}", response_model=DocumentRead)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Get details for a single document, including version and metadata.
    Useful for preparing tender submissions or compliance checks.
    """
    doc = db.query(models.Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/project/{project_id}", response_model=List[DocumentRead])
def list_project_documents(project_id: int, db: Session = Depends(get_db)):
    """
    List all documents for a specific project.
    Helps the family quickly gather all docs needed for a project tender or audit.
    """
    return db.query(models.Document).filter(models.Document.project_id == project_id).all()

@router.get("/company/{company_id}", response_model=List[DocumentRead])
def list_company_documents(company_id: int, db: Session = Depends(get_db)):
    """
    List all documents for a specific company.
    Useful for compliance, audits, or preparing company-wide reports.
    """
    return db.query(models.Document).filter(models.Document.company_id == company_id).all()

@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Delete a document (if uploaded in error or no longer needed).
    Keeps the records room tidy and up to date.
    """
    doc = db.query(models.Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Optionally, delete the file from disk
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    db.commit()
    return {"ok": True}

@router.get("/history/{project_id}", response_model=List[DocumentRead])
def document_version_history(project_id: int, db: Session = Depends(get_db)):
    """
    List all versions of documents for a project, ordered by filename and version.
    Lets the family see the full history of each document for compliance and audits.
    """
    docs = db.query(models.Document).filter(models.Document.project_id == project_id).order_by(models.Document.filename, models.Document.version_number.desc()).all()
    return docs

@router.post('/force_scan')
def force_scan_document(doc_id: int = None, file_path: str = None, db: Session = Depends(get_db)):
    """
    Manually trigger a force scan on a document by ID or file path.
    """
    if not doc_id and not file_path:
        raise HTTPException(status_code=400, detail='Must provide doc_id or file_path')
    if doc_id:
        doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail='Document not found')
        file_path = doc.file_path
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail='File not found')
    result = force_scanner.scan_file(file_path)
    # Optionally update document OCR text/status in DB
    if doc_id and result.text:
        doc.ocr_text = result.text
        db.commit()
    return {
        'text': result.text,
        'confidence': result.confidence,
        'pages': result.pages,
        'error': result.error
    } 