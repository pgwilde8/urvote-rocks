from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
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
    # Create new user with appropriate permissions based on user_type
    verification_token = secrets.token_urlsafe(32)
    hashed_password = get_password_hash(user_data.password)
    
    # Set permissions based on user type
    if user_data.user_type == "board_owner":
        is_contestant = False
        is_voter = True
    elif user_data.user_type == "creator":
        is_contestant = True
        is_voter = True
    else:  # voter or default
        is_contestant = False
        is_voter = True
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        verification_token=verification_token,
        user_type=user_data.user_type,
        is_contestant=is_contestant,
        is_voter=is_voter
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

@router.post("/register-form", response_class=HTMLResponse)
async def register_form(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    user_type: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Handle form-based registration for board_owners and creators"""
    try:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            return HTMLResponse(
                content=f"""
                <div class="text-red-600 text-center text-sm">
                    Email already registered. 
                    <a href="/login" class="text-blue-600 hover:underline">Login here</a>
                </div>
                """,
                status_code=400
            )
        
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            return HTMLResponse(
                content="""
                <div class="text-red-600 text-center text-sm">
                    Username already taken. Please choose a different username.
                </div>
                """,
                status_code=400
            )
        
        # Validate user_type
        if user_type not in ["board_owner", "creator"]:
            return HTMLResponse(
                content="""
                <div class="text-red-600 text-center text-sm">
                    Invalid user type. Please select Board Owner or Content Creator.
                </div>
                """,
                status_code=400
            )
        
        # Create new user with appropriate permissions
        verification_token = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(password)
        
        # Set permissions based on user type
        if user_type == "board_owner":
            is_contestant = False
            is_voter = True
        elif user_type == "creator":
            is_contestant = True
            is_voter = True
        else:  # This shouldn't happen due to validation above
            is_contestant = False
            is_voter = True
        
        new_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            verification_token=verification_token,
            user_type=user_type,
            is_contestant=is_contestant,
            is_voter=is_voter
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Redirect based on user type
        if user_type == "board_owner":
            return RedirectResponse(url="/make-media-board", status_code=302)
        elif user_type == "creator":
            return RedirectResponse(url="/contests", status_code=302)
        else:
            return RedirectResponse(url="/login?message=Registration successful! Please login.", status_code=302)
        
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <div class="text-red-600 text-center text-sm">
                Registration failed: {str(e)}
            </div>
            """,
            status_code=500
        )

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

@router.post("/session")
async def set_session(request: Request, user_data: dict):
    """Store user info in session for server-side access"""
    request.session["user_id"] = user_data.get("user_id")
    request.session["user_email"] = user_data.get("email")
    request.session["user_type"] = user_data.get("user_type")
    return {"message": "Session set successfully"}

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

    
