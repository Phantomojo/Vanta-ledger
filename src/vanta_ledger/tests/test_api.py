import pytest
from httpx import AsyncClient
from vanta_ledger.main import app
from vanta_ledger.core.config import settings
import os

API_KEY = os.getenv("VANTALEDGER_API_KEY", settings.API_KEY)
HEADERS = {"access_token": API_KEY}

@pytest.mark.asyncio
async def test_verify_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/verify", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == {"message": "Token is valid"}

@pytest.mark.asyncio
async def test_crud_transactions():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create transaction
        tx_data = {
            "amount": 100.0,
            "type": "income",
            "description": "Test transaction",
            "date": "2025-01-01"
        }
        response = await ac.post("/api/transactions", json=tx_data, headers=HEADERS)
        assert response.status_code == 200
        tx = response.json()
        tx_id = tx["id"]

        # Get transaction
        response = await ac.get(f"/api/transactions/{tx_id}", headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["id"] == tx_id

        # List transactions
        response = await ac.get("/api/transactions", headers=HEADERS)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Delete transaction
        response = await ac.delete(f"/api/transactions/{tx_id}", headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["message"] == "Transaction deleted"
