from fastapi import APIRouter, Depends
from typing import List
from ..auth import AuthService

router = APIRouter(prefix='/users', tags=['Users'])

@router.get('/')
async def get_users(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve a list of users for authenticated clients.
    
    Requires a valid authentication token; returns a static list containing a single user with admin privileges.
    
    Returns:
        List[dict]: A list of user dictionaries with id, username, and role fields.
    """
    return [{'id': 1, 'username': 'admin', 'role': 'admin'}]
