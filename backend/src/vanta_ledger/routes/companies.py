import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..auth import AuthService
from ..config import settings
from ..database import get_postgres_connection
from ..utils.validation import input_validator

# Thread pool for database operations
executor = ThreadPoolExecutor(max_workers=10)

router = APIRouter(prefix="/companies", tags=["Companies"])





def _get_companies_sync(page: int, limit: int):
    """Synchronous database operation for getting companies"""
    conn = get_postgres_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_count = cursor.fetchone()[0]

        offset = (page - 1) * limit

        cursor.execute(
            "SELECT postgres_id, name, industry, revenue FROM companies ORDER BY name LIMIT %s OFFSET %s",
            (limit, offset),
        )
        companies = cursor.fetchall()

        return {
            "companies": [
                {
                    "id": company[0],
                    "name": company[1],
                    "industry": company[2],
                    "revenue": company[3],
                }
                for company in companies
            ],
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit,
        }
    finally:
        cursor.close()
        conn.close()


@router.get("")
async def get_companies(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    limit: int = Query(20, ge=1, le=100, description="Number of companies per page, max 100"),
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Retrieve a paginated list of companies with their details.

    Parameters:
        page (int): The page number to retrieve, starting from 1.
        limit (int): The maximum number of companies per page, up to 100.

    Returns:
        dict: Contains a list of companies (each with id, name, industry, revenue), total count, current page, limit, and total pages.
    """
    # Validate pagination parameters
    page = input_validator.validate_integer(page, min_value=1, field_name="page")
    limit = input_validator.validate_integer(limit, min_value=1, max_value=100, field_name="limit")

    # Run database operation in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_companies_sync, page, limit)


def _get_company_sync(company_id: int):
    """Synchronous database operation for getting a single company"""
    conn = get_postgres_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT postgres_id, name, industry, revenue FROM companies WHERE postgres_id = %s",
            (company_id,),
        )
        company = cursor.fetchone()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        return {
            "id": company[0],
            "name": company[1],
            "industry": company[2],
            "revenue": company[3],
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/{company_id}")
async def get_company(
    company_id: int, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Retrieve a company's details by its unique ID.

    Validates the provided company ID and returns the company's id, name, industry, and revenue. Raises a 404 error if the company does not exist.

    Parameters:
        company_id (int): The unique identifier of the company to retrieve.

    Returns:
        dict: A dictionary containing the company's id, name, industry, and revenue.
    """
    company_id = input_validator.validate_integer(
        company_id, min_value=1, field_name="company_id"
    )

    # Run database operation in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_company_sync, company_id)
