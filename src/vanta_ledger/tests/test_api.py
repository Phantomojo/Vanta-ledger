import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vanta_ledger.core.config import settings
import pytest
import asyncio

# Example test - replace with your actual tests
@pytest.mark.asyncio
async def test_dummy():
    assert True
