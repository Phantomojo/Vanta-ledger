#!/usr/bin/env python3
"""
Simple Authentication Route
Legacy compatibility endpoint for frontend integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..auth import AuthService

router = APIRouter(tags=["Simple Auth"])


@router.post("/simple-auth")
async def simple_auth(username: str = Query(...), password: str = Query(...)):
    """
    Simple authentication endpoint for legacy frontend compatibility
    Returns access token if authentication is successful
    """
    try:
        # Use the existing AuthService to authenticate
        user_data = AuthService.authenticate_user(username, password)

        if user_data:
            # Generate access token
            access_token = AuthService.create_access_token(
                data={
                    "sub": user_data["username"],
                    "user_id": user_data.get("user_id"),
                    "role": user_data.get("role", "user"),
                }
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "username": user_data["username"],
                    "user_id": user_data.get("user_id"),
                    "email": user_data.get("email"),
                    "role": user_data.get("role", "user"),
                },
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except HTTPException:
        raise
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"Authentication failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """Dependency for token verification"""
    return AuthService.verify_token(credentials.credentials)


# Add this to the router for external access
router.verify_token_dependency = verify_token_dependency


@router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(verify_token_dependency)):
    """
    Get current user information from token
    """
    return {
        "username": current_user.get("sub") or current_user.get("username"),
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email", "admin@vantaledger.com"),
        "role": current_user.get("role", "user"),
        "profile": {
            "name": current_user.get("sub") or current_user.get("username", "Admin"),
            "avatar": "",
            "bio": "System Administrator",
        },
    }
