from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import verify_token
from ..services.user_service import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_users(current_user: dict = Depends(verify_token)):
    """
    Retrieve a list of users for authenticated clients.

    Requires a valid authentication token; returns actual users from the database.

    Returns:
        List[dict]: A list of user dictionaries with id, username, email, and role fields.
    """
    try:
        user_service = get_user_service()
        users = user_service.get_users()
        
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.get("/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(verify_token)):
    """
    Retrieve a specific user by ID.

    Parameters:
        user_id (str): The UUID of the user to retrieve.

    Returns:
        dict: User information if found.

    Raises:
        HTTPException: If user not found or access denied.
    """
    try:
        user_service = get_user_service()
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@router.patch("/{user_id}")
async def update_user_partial(
    user_id: str,
    user_update: dict,
    current_user: dict = Depends(verify_token)
):
    """
    Partially update a user's information.

    Parameters:
        user_id (str): The UUID of the user to update.
        user_update (dict): The user data to update (partial).

    Returns:
        dict: Updated user information.

    Raises:
        HTTPException: If user not found or update fails.
    """
    try:
        user_service = get_user_service()
        
        # Check if user exists
        existing_user = user_service.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user fields
        if "username" in user_update:
            existing_user.username = user_update["username"]
        if "email" in user_update:
            existing_user.email = user_update["email"]
        if "role" in user_update:
            existing_user.role = user_update["role"]
        if "is_active" in user_update:
            existing_user.is_active = user_update["is_active"]
        
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
            "role": existing_user.role,
            "is_active": existing_user.is_active,
            "created_at": existing_user.created_at.isoformat() if existing_user.created_at else None,
            "last_login": existing_user.last_login.isoformat() if existing_user.last_login else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )
