from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
import json
from urllib.parse import urlencode

from ..database import get_db
from ..models import User
from ..config import settings
from ..utils.main import generate_jwt_token

router = APIRouter(prefix="/auth", tags=["authentication"])

# Google OAuth configuration
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret
GOOGLE_REDIRECT_URI = settings.google_redirect_uri

# OAuth scopes
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile", 
    "openid"
]

def get_google_flow():
    """Create Google OAuth flow"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow

@router.get("/google")
async def google_login(request: Request, redirect_url: str = "/"):
    """Initiate Google OAuth login"""
    try:
        flow = get_google_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store state and redirect URL in session for security
        request.session["oauth_state"] = state
        request.session["redirect_after_login"] = redirect_url
        
        return RedirectResponse(authorization_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth setup failed: {str(e)}")

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from callback
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        
        # Verify state parameter
        if not state or state != request.session.get("oauth_state"):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for token
        flow = get_google_flow()
        flow.fetch_token(code=code)
        
        # Get user info from Google
        credentials = flow.credentials
        idinfo = id_token.verify_oauth2_token(
            credentials.id_token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        email = idinfo.get('email')
        name = idinfo.get('name')
        google_id = idinfo.get('sub')
        
        if not email:
            raise HTTPException(status_code=400, detail="No email provided by Google")
        
        # Check if user exists in database
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        # Create user if doesn't exist (for voters)
        if not user:
            user = User(
                email=email,
                username=email.split("@")[0],  # Use email prefix as username
                hashed_password="oauth_user",
                google_id=google_id,
                name=name,
                user_type="voter",
                is_voter=True
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = google_id
                await db.commit()
        
        # Generate JWT token
        token = generate_jwt_token(user.id, user.email, user.user_type)
        
        # Store token in session
        request.session["access_token"] = token
        request.session["user_id"] = user.id
        request.session["user_email"] = user.email
        request.session["user_type"] = user.user_type
        
        # Redirect to the page they were trying to access
        redirect_url = request.session.get("redirect_after_login", "/")
        # Clear the redirect URL from session
        if "redirect_after_login" in request.session:
            del request.session["redirect_after_login"]
        return RedirectResponse(redirect_url)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")

@router.get("/logout")
async def logout(request: Request):
    """Logout user and clear session"""
    request.session.clear()
    return RedirectResponse("/")

@router.get("/me")
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """Get current user information"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "user_type": user.user_type,
        "is_active": user.is_active
    }
