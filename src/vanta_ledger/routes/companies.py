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
    """
    Retrieve a paginated list of companies with their details.
    
    Parameters:
        page (int): The page number to retrieve, starting from 1.
        limit (int): The maximum number of companies per page, up to 100.
    
    Returns:
        dict: Contains a list of companies (each with id, name, industry, revenue), total count, current page, limit, and total pages.
    """
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
    """
    Retrieve a company's details by its unique ID.
    
    Validates the provided company ID and returns the company's id, name, industry, and revenue. Raises a 404 error if the company does not exist.
    
    Parameters:
    	company_id (int): The unique identifier of the company to retrieve.
    
    Returns:
    	dict: A dictionary containing the company's id, name, industry, and revenue.
    """
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
