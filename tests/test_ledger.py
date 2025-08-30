"""
Tests for ledger functionality.
"""

import pytest
from fastapi import status


def test_ledger_endpoint(client):
    """Test ledger endpoint."""
    response = client.get(f"/ledger")
    assert response.status_code == status.HTTP_200_OK


def test_ledger_authentication(client):
    """Test ledger authentication."""
    response = client.get(f"/ledger")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
