"""
Companies API Routes

Provides REST API endpoints for company management.
Includes authentication, validation, and error handling.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ..auth import AuthService
from ..utils.validation import input_validator
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(prefix="/companies", tags=["companies"])
executor = ThreadPoolExecutor(max_workers=4)


def _get_companies_sync(page: int, limit: int) -> Dict[str, Any]:
    """Synchronous function to get companies from database."""
    # This would normally query the database
    # For now, return sample data
    companies = [
        {
            "id": "1",
            "name": "Acme Corp",
            "industry": "Technology",
            "status": "active"
        },
        {
            "id": "2", 
            "name": "Global Industries",
            "industry": "Manufacturing",
            "status": "active"
        }
    ]
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_companies = companies[start_idx:end_idx]
    
    return {
        "companies": paginated_companies,
        "total": len(companies),
        "page": page,
        "limit": limit,
        "pages": (len(companies) + limit - 1) // limit
    }


@router.get("")
async def get_companies(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    limit: int = Query(20, ge=1, le=100, description="Number of companies per page, max 100"),
    current_user: Dict[str, Any] = Depends(AuthService.verify_token),
):
    """
    Retrieve a paginated list of companies with their details.
    
    Args:
        page: Page number (1-based)
        limit: Number of companies per page (max 100)
        current_user: Authenticated user information
        
    Returns:
        Dictionary containing companies, pagination info, and metadata
        
    Raises:
        HTTPException: If validation fails or database error occurs
    """
    page = input_validator.validate_integer(page, min_value=1, field_name="page")
    limit = input_validator.validate_integer(limit, min_value=1, max_value=100, field_name="limit")
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_companies_sync, page, limit)
