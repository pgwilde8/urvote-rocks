from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.config import settings
from datetime import datetime
import secrets

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    # Create new user
    verification_token = secrets.token_urlsafe(32)
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        verification_token=verification_token
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    # TODO: Send verification email
    # For now, just return success
    return {
        "message": "User registered successfully. Please check your email for verification.",
        "user_id": new_user.id
    }

@router.post("/login", response_model=dict)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and return access token"""
    # Find user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.post("/verify-email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify user email with token"""
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    user.email_verified = True
    user.verification_token = None
    await db.commit()
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(email: str, db: AsyncSession = Depends(get_db)):
    """Resend verification email"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    # Generate new verification token
    user.verification_token = secrets.token_urlsafe(32)
    await db.commit()
    # TODO: Send verification email
    return {"message": "Verification email sent"}

    
