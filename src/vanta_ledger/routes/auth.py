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
    try:
        from ..services.user_service import get_user_service
        
        user_service = get_user_service()
        db_user = user_service.verify_user_credentials(username, password)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": db_user.username, "user_id": db_user.id, "role": db_user.role},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "role": db_user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

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
        data={"sub": current_user.get("sub"), "user_id": current_user.get("user_id"), "role": current_user.get("role")},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(default="user")
):
    """Register a new user"""
    try:
        from ..services.user_service import get_user_service
        from ..models.user_models import UserCreate
        
        user_service = get_user_service()
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            role=role
        )
        
        db_user = user_service.create_user(user_data)
        
        return {
            "message": "User created successfully",
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "role": db_user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )
