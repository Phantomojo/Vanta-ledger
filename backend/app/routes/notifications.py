from fastapi import APIRouter, Depends
from typing import List
from ..auth import AuthService

router = APIRouter(prefix='/notifications', tags=['Notifications'])

@router.get('/')
async def get_notifications(current_user: dict = Depends(AuthService.verify_token)):
    return []

@router.get('/settings')
async def get_notification_settings(current_user: dict = Depends(AuthService.verify_token)):
    return {'email': True, 'push': False}
