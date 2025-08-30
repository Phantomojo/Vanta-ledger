from typing import List

from fastapi import APIRouter, Depends

from ..auth import AuthService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def get_notifications(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve the list of notifications for the authenticated user.

    Returns:
        list: An empty list of notifications.
    """
    return []


@router.get("/settings")
async def get_notification_settings(
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Retrieve the current user's notification settings.

    Returns:
        dict: A dictionary indicating whether email and push notifications are enabled.
    """
    return {"email": True, "push": False}
