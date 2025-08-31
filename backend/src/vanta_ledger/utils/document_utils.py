import json
import os
from datetime import datetime
from typing import Dict, Optional


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
