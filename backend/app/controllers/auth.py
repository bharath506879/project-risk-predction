from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import logging

from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    **Request:**
    ```json
    {
        "email": "user@example.com",
        "username": "john_doe",
        "password": "secure_password",
        "full_name": "John Doe"
    }
    ```
    """
    try:
        user = await AuthService.register_user(db, user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login user and get access token
    
    **Request:**
    ```json
    {
        "email": "user@example.com",
        "password": "secure_password"
    }
    ```
    
    **Response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "john_doe",
            "full_name": "John Doe"
        }
    }
    ```
    """
    user = await AuthService.authenticate_user(db, credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = None, db: AsyncSession = Depends(get_db)):
    """Get current authenticated user (requires token in Authorization header)"""
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    token_data = AuthService.verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await AuthService.get_user_by_id(db, token_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)
