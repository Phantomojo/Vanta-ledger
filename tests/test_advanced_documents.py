"""Tests for advanced document processing endpoints."""

import pytest
from fastapi import status

def test_process_document_advanced(client, auth_headers):
    """Test advanced document processing."""
    processing_data = {
        "document_id": "test-doc-id",
        "processing_options": {
            "process_handwritten": True,
            "enable_layout_analysis": True
        }
    }
    
    response = client.post(
        "/advanced-documents/process",
        json=processing_data,
        headers=auth_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "completed"
