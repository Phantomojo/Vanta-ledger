import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..auth import verify_token
from ..database import get_postgres_connection

# Thread pool for database operations
executor = ThreadPoolExecutor(max_workers=10)

router = APIRouter(prefix="/projects", tags=["Projects"])


def _get_projects_sync():
    """Synchronous database operation for getting projects"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT postgres_id, name, status, budget FROM projects LIMIT 50"
        )
        projects = cursor.fetchall()
        return [
            {"id": p[0], "name": p[1], "status": p[2], "budget": p[3]} for p in projects
        ]
    finally:
        cursor.close()
        conn.close()


@router.get("/")
async def get_projects(current_user: dict = Depends(verify_token)):
    """
    Retrieve a list of up to 50 projects with their ID, name, status, and budget.

    Returns:
        List[dict]: A list of dictionaries, each containing the keys 'id', 'name', 'status', and 'budget' for a project.
    """
    # Run database operation in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_projects_sync)


def _get_project_sync(project_id: int):
    """Synchronous database operation for getting a single project"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT postgres_id, name, status, budget FROM projects WHERE postgres_id = %s",
            (project_id,),
        )
        project = cursor.fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return {
            "id": project[0],
            "name": project[1],
            "status": project[2],
            "budget": project[3],
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/{project_id}")
async def get_project(project_id: int, current_user: dict = Depends(verify_token)):
    """
    Retrieve a project's details by its ID.

    Parameters:
        project_id (int): The unique identifier of the project to retrieve.

    Returns:
        dict: A dictionary containing the project's id, name, status, and budget.

    Raises:
        HTTPException: If the project with the specified ID is not found.
    """
    # Run database operation in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_project_sync, project_id)
