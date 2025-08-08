from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..auth import AuthService
from ..utils.validation import input_validator
from ..config import settings
from ..database import get_postgres_connection

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/")
async def get_companies(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(AuthService.verify_token)
):
    """Get all companies with secure pagination"""
    page, limit = input_validator.validate_pagination_params(page, limit, max_limit=100)

    conn = get_postgres_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM companies")
    total_count = cursor.fetchone()[0]

    offset = (page - 1) * limit

    cursor.execute(
        "SELECT postgres_id, name, industry, revenue FROM companies ORDER BY name LIMIT %s OFFSET %s",
        (limit, offset)
    )
    companies = cursor.fetchall()
    cursor.close()
    conn.close()

    return {
        "companies": [
            {
                "id": company[0],
                "name": company[1],
                "industry": company[2],
                "revenue": company[3]
            }
            for company in companies
        ],
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }

@router.get("/{company_id}")
async def get_company(company_id: int, current_user: dict = Depends(AuthService.verify_token)):
    """Get company by ID with input validation"""
    company_id = input_validator.validate_integer(company_id, min_value=1, field_name="company_id")

    conn = get_postgres_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT postgres_id, name, industry, revenue FROM companies WHERE postgres_id = %s",
        (company_id,)
    )
    company = cursor.fetchone()
    cursor.close()
    conn.close()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "id": company[0],
        "name": company[1],
        "industry": company[2],
        "revenue": company[3]
    }
