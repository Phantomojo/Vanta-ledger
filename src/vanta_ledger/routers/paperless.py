from fastapi import APIRouter, HTTPException
from typing import List, Dict
import httpx

router = APIRouter(prefix="/paperless", tags=["paperless"])

PAPERLESS_API_URL = "http://localhost:8000/api/documents/"

@router.get("/documents", response_model=List[Dict])
async def list_documents():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(PAPERLESS_API_URL)
            resp.raise_for_status()
            data = resp.json()
            # Paperless-ngx returns results in 'results' key
            docs = data.get('results', [])
            return [
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "tags": [t["name"] for t in doc.get("tags", [])],
                    "path": f"/media/documents/originals/{doc['id']}"
                }
                for doc in docs
            ]
    except Exception as e:
        # Fallback to placeholder data
        return [
            {"id": 1, "title": "Sample Document.pdf", "tags": ["invoice"], "path": "/media/documents/originals/1.pdf"},
            {"id": 2, "title": "Another Doc.pdf", "tags": ["contract"], "path": "/media/documents/originals/2.pdf"},
        ]

@router.get("/documents/{doc_id}", response_model=Dict)
async def get_document(doc_id: int):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{PAPERLESS_API_URL}{doc_id}/")
            resp.raise_for_status()
            doc = resp.json()
            return {
                "id": doc["id"],
                "title": doc["title"],
                "tags": [t["name"] for t in doc.get("tags", [])],
                "path": f"/media/documents/originals/{doc['id']}"
            }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

# TODO: Add sync, search, and linking endpoints as needed 