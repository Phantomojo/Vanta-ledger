import pytest
from httpx import AsyncClient
from fastapi import status
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from vanta_ledger.main import app
import asyncio

@pytest.mark.asyncio
async def test_get_ledger_summary():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/ledger/summary")
    assert response.status_code == status.HTTP_200_OK
    assert "total_sales" in response.json()

@pytest.mark.asyncio
async def test_get_settings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/settings")
    assert response.status_code == status.HTTP_200_OK
    assert "currency" in response.json()

@pytest.mark.asyncio
async def test_update_settings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/settings", json={"currency": "EUR"})
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

@pytest.mark.asyncio
async def test_transactions_crud():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create transaction
        tx_data = {
            "type": "sale",
            "amount": 100.0,
            "description": "Test transaction",
            "date": "2023-01-01"
        }
        response = await ac.post("/api/transactions", json=tx_data)
        assert response.status_code == status.HTTP_200_OK
        tx = response.json()
        tx_id = tx["id"]

        # Get transaction
        response = await ac.get(f"/api/transactions/{tx_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Test transaction"

        # Update transaction
        tx_data_update = {
            "type": "expenditure",
            "amount": 50.0,
            "description": "Updated transaction",
            "date": "2023-01-02"
        }
        response = await ac.put(f"/api/transactions/{tx_id}", json=tx_data_update)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["type"] == "expenditure"

        # Delete transaction
        response = await ac.delete(f"/api/transactions/{tx_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Transaction deleted"

        # Get deleted transaction should 404
        response = await ac.get(f"/api/transactions/{tx_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_export_endpoints():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        for endpoint in ["/api/export/csv", "/api/export/excel", "/api/export/pdf"]:
            response = await ac.get(endpoint)
            assert response.status_code == status.HTTP_200_OK
            assert response.headers.get("content-disposition") is not None
