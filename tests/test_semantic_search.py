"""Tests for semantic search endpoints."""

import pytest
from fastapi import status

def test_semantic_search(client, auth_headers):
    """Test semantic search functionality."""
    search_data = {
        "query": "invoice over 1000",
        "company_id": "test-company-id"
    }
    
    response = client.post(
        "/semantic-search/search",
        json=search_data,
        headers=auth_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "results" in data
    assert "query" in data
