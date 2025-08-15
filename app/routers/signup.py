from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Client, Contest
from app.themes import get_theme_by_name, get_theme_by_keywords, apply_theme_to_campaign
from datetime import datetime, timedelta
import hashlib
import secrets
from pathlib import Path

# Create templates instance
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

router = APIRouter()

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page for premium subscription"""
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """Pricing page for premium subscription"""
    return templates.TemplateResponse("pricing.html", {"request": request})

@router.post("/signup/process")
async def process_signup(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Process signup form and create user, client, and contest"""
    try:
        # Get form data
        form_data = await request.form()
        
        # Extract form fields
        first_name = form_data.get("firstName", "").strip()
        last_name = form_data.get("lastName", "").strip()
        email = form_data.get("email", "").strip().lower()
        password = form_data.get("password", "")
        creator_name = form_data.get("creatorName", "").strip()
        website = form_data.get("website", "").strip()
        social_media = form_data.get("socialMedia", "").strip()
        music_style = form_data.get("musicStyle", "")
        board1_name = form_data.get("board1Name", "").strip()
        board1_description = form_data.get("board1Description", "").strip()
        board1_tags = form_data.get("board1Tags", "").strip()
        theme_selection = form_data.get("themeSelection", "auto")
        selected_theme = form_data.get("selectedTheme", "chilled_vibe")
        
        # Validation
        if not all([first_name, last_name, email, password, creator_name, board1_name]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        # Check if email already exists
        existing_user = await db.execute(select(User).where(User.email == email))
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if creator name already exists
        existing_client = await db.execute(select(Client).where(Client.name == creator_name))
        if existing_client.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Creator name already taken")
        
        # Create user
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        username = f"{first_name.lower()}{last_name.lower()}{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Ensure username is unique
        counter = 1
        original_username = username
        while True:
            existing = await db.execute(select(User).where(User.username == username))
            if not existing.scalar_one_or_none():
                break
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            artist_name=creator_name,
            website=website if website else None,
            is_active=True,
            is_contestant=True
        )
        db.add(user)
        await db.flush()  # Get user ID
        
        # Create client
        client_slug = creator_name.lower().replace(" ", "-").replace("&", "and")
        # Ensure slug is unique
        counter = 1
        original_slug = client_slug
        while True:
            existing = await db.execute(select(Client).where(Client.slug == client_slug))
            if not existing.scalar_one_or_none():
                break
            client_slug = f"{original_slug}-{counter}"
            counter += 1
        
        client = Client(
            name=creator_name,
            slug=client_slug,
            website_url=website if website else None,
            description=f"AI music creator: {creator_name}",
            is_active=True
        )
        db.add(client)
        await db.flush()  # Get client ID
        
        # Create first contest/board
        contest_slug = board1_name.lower().replace(" ", "-").replace("&", "and")
        # Ensure contest slug is unique
        counter = 1
        original_contest_slug = contest_slug
        while True:
            existing = await db.execute(select(Contest).where(Contest.name == contest_slug))
            if not existing.scalar_one_or_none():
                break
            contest_slug = f"{original_contest_slug}-{counter}"
            counter += 1
        
        # Parse tags
        tags_list = [tag.strip() for tag in board1_tags.split(",") if tag.strip()]
        if not tags_list:
            tags_list = ["🤖 AI-Generated", "🎵 Music Contest", "🌍 Global Community"]
        
        contest = Contest(
            name=board1_name,
            description=board1_description or f"AI-generated music contest by {creator_name}",
            client_id=client.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365),  # 1 year from now
            is_active=True,
            voting_enabled=True
        )
        db.add(contest)
        
        # Commit all changes
        await db.commit()
        
        # Apply theme to the contest
        theme = None
        if theme_selection == "auto":
            # Auto-match theme based on description
            theme = get_theme_by_keywords(f"{board1_name} {board1_description}")
        else:
            # Use manually selected theme
            theme = get_theme_by_name(selected_theme)
        
        if theme:
            # Store theme information in contest metadata (you might want to add a theme field to Contest model)
            print(f"Applied theme '{theme.name}' to contest '{board1_name}'")
        
        # Prepare campaign data with theme
        campaign_data = {
            "client_name": client.name,
            "client_slug": client.slug,
            "contest_name": contest.name,
            "contest_id": contest.id,
            "description": contest.description,
            "song_count": 0,
            "vote_count": 0,
            "campaign_type": "custom",
            "colors": "from-blue-500 to-purple-600",  # Default fallback
            "features": ["🤖 AI-Generated", "🎵 Music Contest", "🗳️ Community Voting", "🎯 Custom Theme"],
            "action_text": "Enter Contest",
            "action_url": f"/campaigns/{client.slug}/{contest.id}",
            "website_url": client.website_url,
            "website_display": client.website_url,
            "end_date": contest.end_date,
            "is_always_open": False,
            "created_at": contest.created_at
        }
        
        if theme:
            campaign_data = apply_theme_to_campaign(campaign_data, theme)
        
        return {
            "success": True,
            "message": "Account created successfully!",
            "data": {
                "user_id": user.id,
                "client_slug": client.slug,
                "contest_slug": contest_slug,
                "redirect_url": f"/campaigns/{client.slug}/{contest_slug}",
                "theme_applied": theme.name if theme else "Default",
                "campaign_data": campaign_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/signup/success")
async def signup_success(
    request: Request,
    user_id: int = None,
    client_slug: str = None,
    contest_slug: str = None
):
    """Success page after signup"""
    return templates.TemplateResponse("signup_success.html", {
        "request": request,
        "user_id": user_id,
        "client_slug": client_slug,
        "contest_slug": contest_slug
    })
