from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..auth import AuthService
from ..database import get_postgres_connection

router = APIRouter(prefix='/projects', tags=['Projects'])

@router.get('/')
async def get_projects(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve a list of up to 50 projects with their ID, name, status, and budget.
    
    Returns:
        List[dict]: A list of dictionaries, each containing the keys 'id', 'name', 'status', and 'budget' for a project.
    """
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT postgres_id, name, status, budget FROM projects LIMIT 50')
    projects = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{'id': p[0], 'name': p[1], 'status': p[2], 'budget': p[3]} for p in projects]

@router.get('/{project_id}')
async def get_project(project_id: int, current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve a project's details by its ID.
    
    Parameters:
        project_id (int): The unique identifier of the project to retrieve.
    
    Returns:
        dict: A dictionary containing the project's id, name, status, and budget.
    
    Raises:
        HTTPException: If the project with the specified ID is not found.
    """
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT postgres_id, name, status, budget FROM projects WHERE postgres_id = %s', (project_id,))
    project = cursor.fetchone()
    cursor.close()
    conn.close()
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    return {'id': project[0], 'name': project[1], 'status': project[2], 'budget': project[3]}
