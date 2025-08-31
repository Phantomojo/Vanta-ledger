import os
"""
Users API Routes

Provides REST API endpoints for user management.
Includes authentication, validation, and error handling.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from ..auth import verify_token
from ..models.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/{user_id}")
async def update_user_partial(
    user_id: str,
    user_update: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """
    Partially update a user's information.
    
    Args:
        user_id: ID of the user to update
        user_update: Dictionary containing fields to update
        current_user: Authenticated user information

    Returns:
        Updated user information

    Raises:
        HTTPException: If user not found or update fails
    """
    user_service = UserService()
    existing_user = user_service.get_user_by_id(user_id)
    
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    for field, value in user_update.items():
        if hasattr(existing_user, field):
            setattr(existing_user, field, value)
    
    # Save changes with rollback on failure
    try:
        user_service.db.commit()
        user_service.db.refresh(existing_user)
    except Exception:
        user_service.db.rollback()
        raise
    
    return {
        "id": existing_user.id,
        "username": existing_user.username,
        "email": existing_user.email,
        "is_active": existing_user.is_active,
        "role": existing_user.role
    }
