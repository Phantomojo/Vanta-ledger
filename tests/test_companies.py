"""
Tests for companies functionality.
"""

import pytest
from fastapi import status


def test_companies_endpoint(client):
    """Test companies endpoint."""
    response = client.get(f"/companies")
    assert response.status_code == status.HTTP_200_OK


def test_companies_authentication(client):
    """Test companies authentication."""
    response = client.get(f"/companies")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
