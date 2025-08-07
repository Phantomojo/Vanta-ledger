from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta

from ..auth import AuthService, get_current_user, get_user_by_username, User, verify_password, blacklist_token
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return AuthService.verify_token(credentials.credentials)

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Secure login endpoint with password hashing"""
    user = await get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
async def logout(current_user: dict = Depends(verify_token)):
    """Logout endpoint - add token to blacklist"""
    await blacklist_token(current_user.get("jti"))
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(verify_token)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": current_user.get("sub"), "user_id": current_user.get("user_id")},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
