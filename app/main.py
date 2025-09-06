# app/main.py
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------- App / Config ----------------
from .config import settings
from .database import get_db
from .models import Contest, Client, Song, Vote

# Routers (updated: campaigns -> songboards, add sales)
from .routers import auth, songs, voting, songboards, signup, static_pages, brevo_test
#from . import admin
from .routers import admin
from app.routers import submitter, board_owner, boards
# Routers (updated: campaigns -> songboards, add sales)

# ------------------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------------------
app = FastAPI(
    title="UrVote.Rocks",
    description="Contest Platform for Brands, Events, and Creators",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
# Production: restrict to your domains; Dev: allow localhost
allow_origins = [
    "https://urvote.rocks",
    "https://www.urvote.rocks",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware for uploads
from fastapi.responses import Response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add security headers for uploaded files
    if request.url.path.startswith("/uploads/"):
        response.headers["Content-Disposition"] = "inline"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "public, max-age=3600"
    
    return response

# ------------------------------------------------------------------------------
# Static & Templates
# ------------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")  # Re-enable static mount
templates = Jinja2Templates(directory="app/templates")

# Remove the custom file serving route since it conflicts with board routes
# The static mount will handle file serving, and we'll add security through other means

# ------------------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("lander.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Media Boards landing page
@app.get("/media-boards", response_class=HTMLResponse)
async def media_boards_page(request: Request):
    """Media Boards landing page explaining what Media Boards are"""
    return templates.TemplateResponse("media-boards.html", {"request": request})

# Business setup page
@app.get("/business-setup", response_class=HTMLResponse)
async def business_setup_page(request: Request):
    """Business setup page where users input business information before creating their Media Board"""
    return templates.TemplateResponse("business-setup.html", {"request": request})

# Board page route - moved here to ensure it takes precedence
@app.get("/board/{slug}", response_class=HTMLResponse)
async def board_page(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Import Board model here to avoid circular imports
    from .models import Board
    
    # Find board by slug
    board_res = await db.execute(select(Board).where(Board.slug == slug))
    board = board_res.scalar_one_or_none()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    return templates.TemplateResponse("board.html", {
        "request": request,
        "board": board
    })

# Smart Voting Link Page - Dynamic for each piece of content
@app.get("/vote/{content_id}/{slug}", response_class=HTMLResponse)
async def smart_vote_page(
    content_id: int,
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Dynamic voting page that loads specific content and shows leaderboard"""
    try:
        # Import models here to avoid circular imports
        from .models import Board, Song, Video, Visual, Vote
        from sqlalchemy import select, func
        
        # Find the board by slug
        board_res = await db.execute(select(Board).where(Board.slug == slug))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Find the specific content being voted on
        content = None
        content_type = None
        
        # Check songs
        song_res = await db.execute(select(Song).where(Song.id == content_id, Song.board_id == board.id))
        song = song_res.scalar_one_or_none()
        if song:
            content = song
            content_type = "music"
        
        # Check videos
        if not content:
            video_res = await db.execute(select(Video).where(Video.id == content_id, Video.board_id == board.id))
            video = video_res.scalar_one_or_none()
            if video:
                content = video
                content_type = "video"
        
        # Check visuals
        if not content:
            visual_res = await db.execute(select(Visual).where(Visual.id == content_id, Visual.board_id == board.id))
            visual = visual_res.scalar_one_or_none()
            if visual:
                content = visual
                content_type = "visuals"
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Get top voted content for leaderboard
        leaderboard = []
        
        # Get top music
        if board.allow_music:
            music_query = select(Song, func.count(Vote.id).label('vote_count')).join(
                Vote, (Vote.media_type == "music") & (Vote.media_id == Song.id) & (Vote.vote_type == "like")
            ).where(Song.board_id == board.id).group_by(Song.id).order_by(func.count(Vote.id).desc()).limit(10)
            music_res = await db.execute(music_query)
            music_items = music_res.all()
            for song, vote_count in music_items:
                leaderboard.append({
                    "id": song.id,
                    "title": song.title,
                    "artist_name": song.artist_name,
                    "content_type": "music",
                    "vote_count": vote_count,
                    "rank": len(leaderboard) + 1
                })
        
        # Get top videos
        if board.allow_video:
            video_query = select(Video, func.count(Vote.id).label('vote_count')).join(
                Vote, (Vote.media_type == "video") & (Vote.media_id == Video.id) & (Vote.vote_type == "like")
            ).where(Video.board_id == board.id).group_by(Video.id).order_by(func.count(Vote.id).desc()).limit(10)
            video_res = await db.execute(video_query)
            video_items = video_res.all()
            for video, vote_count in video_items:
                leaderboard.append({
                    "id": video.id,
                    "title": video.title,
                    "artist_name": video.artist_name,
                    "content_type": "video",
                    "vote_count": vote_count,
                    "rank": len(leaderboard) + 1
                })
        
        # Get top visuals
        if board.allow_visuals:
            visual_query = select(Visual, func.count(Vote.id).label('vote_count')).join(
                Vote, (Vote.media_type == "visuals") & (Vote.media_id == Visual.id) & (Vote.vote_type == "like")
            ).where(Visual.board_id == board.id).group_by(Visual.id).order_by(func.count(Vote.id).desc()).limit(10)
            visual_res = await db.execute(visual_query)
            visual_items = visual_res.all()
            for visual, vote_count in visual_items:
                leaderboard.append({
                    "id": visual.id,
                    "title": visual.title,
                    "artist_name": visual.artist_name,
                    "content_type": "visuals",
                    "vote_count": vote_count,
                    "rank": len(leaderboard) + 1
                })
        
        # Sort leaderboard by vote count and assign final ranks
        leaderboard.sort(key=lambda x: x['vote_count'], reverse=True)
        for i, item in enumerate(leaderboard):
            item['rank'] = i + 1
        
        return templates.TemplateResponse("smart-vote.html", {
            "request": request,
            "board": board,
            "content": content,
            "content_type": content_type,
            "leaderboard": leaderboard[:10]  # Top 10
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading voting page: {str(e)}")

# Create checkout session with theme
@app.get("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    theme: str = Query("default", description="Selected theme name")
):
    """Create Stripe checkout session for Media Board subscription or redirect to free creation"""
    from app.config import settings
    
    # Check if free boards are enabled
    if settings.free_boards_enabled:
        # Redirect to free board creation page
        return RedirectResponse(url=f"/media-boards/create?theme={theme}&free=true", status_code=303)
    
    # If Stripe is not configured, redirect to free creation
    if not settings.stripe_secret_key:
        return RedirectResponse(url=f"/media-boards/create?theme={theme}&free=true", status_code=303)
    
    try:
        # Import stripe here to avoid circular imports
        import stripe
        
        stripe.api_key = settings.stripe_secret_key
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": settings.stripe_price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{request.base_url}success?session_id={{CHECKOUT_SESSION_ID}}&theme={theme}",
            cancel_url=f"{request.base_url}media-boards",
            metadata={
                "theme": theme,
                "product": "media_board"
            }
        )
        
        # Redirect to Stripe checkout
        return RedirectResponse(url=session.url, status_code=303)
        
    except Exception as e:
        # If Stripe fails, redirect to free creation
        return RedirectResponse(url=f"/media-boards/create?theme={theme}&free=true", status_code=303)

# Free Board Creation Page
@app.get("/media-boards/create", response_class=HTMLResponse)
async def free_board_creation_page(request: Request):
    """Show free board creation page"""
    return templates.TemplateResponse("get-media-board.html", {"request": request})

# Alternative route for easier access
@app.get("/get-media-board", response_class=HTMLResponse)
async def free_board_creation_alt(request: Request):
    """Alternative route for free board creation page"""
    return templates.TemplateResponse("get-media-board.html", {"request": request})

# Upload form (UI)
@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Upload success (UI)
@app.get("/upload/success", response_class=HTMLResponse)
async def upload_success_page(request: Request, song_id: Optional[int] = None):
    song_data = None
    if song_id:
        db = await anext(get_db())
        try:
            result = await db.execute(select(Song).where(Song.id == song_id))
            song_data = result.scalar_one_or_none()
        except Exception:
            song_data = None

    return templates.TemplateResponse("upload-success.html", {
        "request": request,
        "song": song_data,
    })

# ------------------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------------------
# API namespace
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(songs.router, prefix="/api", tags=["songs"])
app.include_router(voting.router, prefix="/api", tags=["voting"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(brevo_test.router, prefix="/api", tags=["brevo"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
# Site features
app.include_router(songboards.router, tags=["songboards"])   # replaces campaigns
app.include_router(signup.router, tags=["signup"])
app.include_router(submitter.router, tags=["submitter"])
app.include_router(board_owner.router, tags=["board_owner"])
app.include_router(boards.router, tags=["boards"])  # Media Board Content API
app.include_router(static_pages.router, tags=["static_pages"])  # Sales, pricing, contact pages

# app.include_router(sales.router, tags=["sales"])  # Removed because 'sales' is not defined

# Handle form submission (UI -> calls upload logic, then redirects)
@app.post("/upload", response_class=HTMLResponse)
async def handle_upload_form(
    request: Request,
    title: str = Form(...),
    artist_name: str = Form(...),
    email: str = Form(...),
    genre: Optional[str] = Form(None),
    ai_tools_used: str = Form(...),
    description: Optional[str] = Form(None),
    license_type: str = Form("stream_only"),
    external_link: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    from app.routers.songs import upload_song_logic
    try:
        song = await upload_song_logic(
            title=title,
            artist_name=artist_name,
            email=email,
            genre=genre,
            ai_tools_used=ai_tools_used,
            description=description,
            license_type=license_type,
            external_link=external_link,
            file=file,
            request=request,
            db=db,
        )
        return RedirectResponse(url=f"/upload/success?song_id={song.id}", status_code=303)
    except HTTPException as e:
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "error": e.detail,
        })

# Legacy leaderboard -> redirect to new songboards landing
@app.get("/leaderboard", response_class=HTMLResponse)
async def legacy_leaderboard_redirect():
    return RedirectResponse(url="/songboards", status_code=307)

# Public pricing: redirect to sales module (commented out due to conflict)
# @app.get("/pricing")
# async def redirect_to_sales_pricing():
#     return RedirectResponse(url="/sales/pricing", status_code=307)

# Client contest page
@app.get("/contest/{client_slug}/{contest_slug}", response_class=HTMLResponse)
async def client_contest_page(
    client_slug: str,
    contest_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    contest_res = await db.execute(
        select(Contest).where(
            Contest.client_slug == client_slug,
            Contest.contest_slug == contest_slug,
        )
    )
    contest = contest_res.scalar_one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    return templates.TemplateResponse("client_contest.html", {
        "request": request,
        "contest": contest,
        "client_slug": client_slug,
        "contest_slug": contest_slug,
    })

# Client homepage
@app.get("/client/{client_slug}", response_class=HTMLResponse)
async def client_homepage(
    client_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    client_res = await db.execute(select(Client).where(Client.slug == client_slug))
    client = client_res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Fetch active contest (optional)
    contest = None
    contest_res = await db.execute(
        select(Contest).where(Contest.client_id == client.id, Contest.is_active == True)
    )
    contest = contest_res.scalar_one_or_none()

    # Recent songs for this client's active contest (guard for None)
    recent_songs = []
    if contest:
        songs_res = await db.execute(
            select(Song)
            .where(Song.contest_id == contest.id)
            .order_by(Song.created_at.desc())
            .limit(4)
        )
        recent_songs = songs_res.scalars().all()

    return templates.TemplateResponse("client/homepage.html", {
        "request": request,
        "client": client,
        "contest": contest,
        "recent_songs": recent_songs,
    })

# Admin dashboard (HTML)
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

# Admin upload page (HTML)
@app.get("/admin/upload", response_class=HTMLResponse)
async def admin_upload_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Admin page for uploading new songs"""
    # Get all boards for the dropdown
    from .models import Board
    boards_res = await db.execute(select(Board).order_by(Board.title))
    boards = boards_res.scalars().all()
    
    return templates.TemplateResponse("admin/admin_upload.html", {
        "request": request,
        "boards": boards
    })

@app.post("/admin/upload", response_class=HTMLResponse)
async def admin_upload_song(
    request: Request,
    title: str = Form(...),
    artist_name: str = Form(...),
    url: str = Form(...),
    board_id: int = Form(...),
    social_link: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle admin song upload form submission"""
    try:
        from .models import Song
        
        # Create new song
        new_song = Song(
            title=title,
            artist_name=artist_name,
            external_link=url,
            board_id=board_id,
            creator_linktree=social_link,
            is_approved=True,  # Admin uploads are auto-approved
            content_source="admin_upload"
        )
        
        db.add(new_song)
        await db.commit()
        
        # Redirect back to upload page with success message
        return RedirectResponse(url="/admin/upload?success=true", status_code=303)
        
    except Exception as e:
        # Redirect back with error message
        return RedirectResponse(url=f"/admin/upload?error={str(e)}", status_code=303)

# Auth pages (if you use server-rendered forms)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Client leaderboard (server-rendered)
@app.get("/client/{client_slug}/leaderboard", response_class=HTMLResponse)
async def client_leaderboard(
    client_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    client_res = await db.execute(select(Client).where(Client.slug == client_slug))
    client = client_res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    contest_res = await db.execute(
        select(Contest).where(Contest.client_id == client.id, Contest.is_active == True)
    )
    contest = contest_res.scalar_one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="No active contest found")

    songs_res = await db.execute(
        select(Song)
        .where(Song.contest_id == contest.id, Song.is_approved == True)
        .order_by(Song.created_at.desc())
    )
    songs = songs_res.scalars().all()

    # Attach vote counts
    for s in songs:
        vc_res = await db.execute(select(func.count(Vote.id)).where(Vote.song_id == s.id))
        s.vote_count = vc_res.scalar() or 0

    # Sort by votes desc
    songs.sort(key=lambda x: x.vote_count, reverse=True)

    return templates.TemplateResponse("client/leaderboard.html", {
        "request": request,
        "client": client,
        "contest": contest,
        "songs": songs,
    })

# How-to-submit static page
@app.get("/how-to-submit", response_class=HTMLResponse)
async def how_to_submit_page(request: Request):
    return templates.TemplateResponse("how-to-submit.html", {"request": request})

# Templates page route
@app.get("/templates", response_class=HTMLResponse)
async def templates_page(request: Request):
    return templates.TemplateResponse("templates.html", {"request": request})

# Success page route (post-purchase)
@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request, session_id: str = None):
    return templates.TemplateResponse("success.html", {"request": request, "session_id": session_id})

# Legal pages
@app.get("/legal/terms-of-service", response_class=HTMLResponse)
async def terms_of_service_page(request: Request):
    return templates.TemplateResponse("legal/terms-of-service.html", {"request": request})

@app.get("/legal/privacy-policy", response_class=HTMLResponse)
async def privacy_policy_page(request: Request):
    return templates.TemplateResponse("legal/privacy-policy.html", {"request": request})

# Shorter legal routes for easier access
@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service_short(request: Request):
    return templates.TemplateResponse("legal/terms-of-service.html", {"request": request})

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy_short(request: Request):
    return templates.TemplateResponse("legal/privacy-policy.html", {"request": request})

# About page
@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Contact page
@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# Pricing page
@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

# FAQ page
@app.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

# ------------------------------------------------------------------------------
# Health & Error Handlers
# ------------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "UrVote.Rocks"}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    # Optional: serve a friendly 404 template if you have one
    # return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)
    return JSONResponse({"detail": "Not Found"}, status_code=404)



@app.post("/api/openwebui/webhook")
async def openwebui_webhook(req: Request):
    payload = await req.json()
    # TODO: validate shared secret header if configured
    # Example: log or route events by type
    event_type = payload.get("type", "unknown")
    # e.g., store prompt snippets, trigger moderation, etc.
    return {"status": "ok", "received": event_type}

