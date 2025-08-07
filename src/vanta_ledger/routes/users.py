from fastapi import APIRouter, Depends
from typing import List
from ..auth import AuthService

router = APIRouter(prefix='/users', tags=['Users'])

@router.get('/')
async def get_users(current_user: dict = Depends(AuthService.verify_token)):
    return [{'id': 1, 'username': 'admin', 'role': 'admin'}]
