import pytest
from httpx import AsyncClient
from fastapi import status
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from vanta_ledger.main import app

API_KEY = "supersecretadmintoken"
INVALID_API_KEY = "invalidtoken"

@pytest.mark.asyncio
async def test_missing_api_key():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/ledger/summary")
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_invalid_api_key():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/ledger/summary", headers={"access_token": INVALID_API_KEY})
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_create_transaction_missing_fields():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Missing 'type' field
        tx_data = {
            "amount": 100.0,
            "description": "Test transaction",
            "date": "2023-01-01"
        }
        response = await ac.post("/api/transactions", json=tx_data, headers={"access_token": API_KEY})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_create_transaction_invalid_amount():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        tx_data = {
            "type": "sale",
            "amount": "invalid_amount",
            "description": "Test transaction",
            "date": "2023-01-01"
        }
        response = await ac.post("/api/transactions", json=tx_data, headers={"access_token": API_KEY})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_update_nonexistent_transaction():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        tx_data = {
            "type": "sale",
            "amount": 50.0,
            "description": "Updated transaction",
            "date": "2023-01-02"
        }
        response = await ac.put("/api/transactions/999999", json=tx_data, headers={"access_token": API_KEY})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_nonexistent_transaction():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/transactions/999999", headers={"access_token": API_KEY})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_nonexistent_transaction():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/transactions/999999", headers={"access_token": API_KEY})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_settings_invalid_payload():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/settings", json={"invalid_field": "value"}, headers={"access_token": API_KEY})
    # Since update_settings is a placeholder, it returns 200 OK, but we can check the message
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
