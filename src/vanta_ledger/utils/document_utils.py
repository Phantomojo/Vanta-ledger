import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def get_document_hash(file_path: str) -> str:
    import hashlib

    BUF_SIZE = 65536
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except Exception:
        return ""


def load_document_metadata(file_path: str) -> Optional[Dict[str, any]]:
    """Load and parse document metadata from analysis file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        txt_file_path = file_path.replace("_analysis.json", ".txt")
        try:
            file_stat = os.stat(txt_file_path)
            file_size = file_stat.st_size
        except FileNotFoundError:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
        return {
            "id": str(data.get("doc_id", data.get("id", ""))),
            "filename": data.get(
                "filename", f"document_{data.get('doc_id', data.get('id', ''))}.json"
            ),
            "title": data.get(
                "title", f"Document {data.get('doc_id', data.get('id', ''))}"
            ),
            "file_type": data.get("file_type", "application/json"),
            "upload_date": data.get("upload_date", datetime.now().isoformat()),
            "size": file_size,
            "status": "analyzed",
            "category": data.get("category", "unknown"),
            "type": data.get("type", "unknown"),
            "companies": data.get("companies", []),
            "projects": data.get("projects", []),
            "financial_data": data.get("financial_data", []),
            "dates": data.get("dates", []),
            "keywords": data.get("keywords", []),
            "file_hash": get_document_hash(file_path),
        }
    except Exception as e:
        print(f"Error loading metadata from {file_path}: {e}")
        return None


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text from PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content or error message
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        return f"[PDF file: {file_path.name} - text extraction failed]"


def extract_text_from_docx(file_path: Path) -> str:
    """
    Extract text from DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text content or error message
    """
    try:
        import docx
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        return f"[DOCX file: {file_path.name} - processing failed]"


def extract_text_from_image(file_path: Path) -> str:
    """
    Extract text from image using OCR.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Extracted text content or error message
    """
    try:
        from PIL import Image
        import pytesseract
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from image {file_path}: {e}")
        return f"[Image file: {file_path.name} - OCR failed]"


def classify_document_type(text: str) -> str:
    """
    Classify document type based on text content.
    
    Args:
        text: Document text content
        
    Returns:
        Document type classification
    """
    text_lower = text.lower()
    
    # Check for different document types
    if any(word in text_lower for word in ['invoice', 'bill', 'receipt']):
        return 'invoice'
    elif any(word in text_lower for word in ['contract', 'agreement']):
        return 'contract'
    elif any(word in text_lower for word in ['report', 'summary']):
        return 'report'
    else:
        return 'general'


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of document text.
    
    Args:
        text: Document text content
        
    Returns:
        Dictionary with sentiment analysis results
    """
    # Simple keyword-based sentiment analysis
    positive_words = ['good', 'excellent', 'great', 'positive', 'approved', 'success']
    negative_words = ['bad', 'poor', 'negative', 'rejected', 'failed', 'issue', 'problem']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = 'positive'
    elif negative_count > positive_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'sentiment': sentiment,
        'positive_indicators': positive_count,
        'negative_indicators': negative_count
    }
