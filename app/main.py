from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .routers import auth, songs, voting
from . import admin
from .config import settings
from .database import get_db
from .models import Contest, Client, Song

# Create FastAPI app
app = FastAPI(
    title="UrVote.Rocks",
    description="Contest Platform for Brands, Events, and Creators",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://urvote.rocks", "https://www.urvote.rocks"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(songs.router, prefix="/api")
app.include_router(voting.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# Root route - Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Upload form route
@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Leaderboard page
@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

# Client contest page route
@app.get("/contest/{client_slug}/{contest_slug}", response_class=HTMLResponse)
async def client_contest_page(
    client_slug: str, 
    contest_slug: str, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Dynamic client contest page"""
    # Get contest data from database
    result = await db.execute(
        select(Contest).where(
            Contest.client_slug == client_slug,
            Contest.contest_slug == contest_slug
        )
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    return templates.TemplateResponse("client_contest.html", {
        "request": request,
        "contest": contest,
        "client_slug": client_slug,
        "contest_slug": contest_slug
    })

# Client homepage route
@app.get("/client/{client_slug}", response_class=HTMLResponse)
async def client_homepage(
    client_slug: str, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Client homepage"""
    # Get client data from database
    result = await db.execute(
        select(Client).where(Client.slug == client_slug)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get client's active contest
    contest_result = await db.execute(
        select(Contest).where(
            Contest.client_id == client.id,
            Contest.is_active == True
        )
    )
    contest = contest_result.scalar_one_or_none()
    
    # Get recent songs for this client
    songs_result = await db.execute(
        select(Song).where(
            Song.contest_id == contest.id if contest else None
        ).order_by(Song.created_at.desc()).limit(4)
    )
    recent_songs = songs_result.scalars().all()
    
    return templates.TemplateResponse("client/homepage.html", {
        "request": request,
        "client": client,
        "contest": contest,
        "recent_songs": recent_songs
    })

# Admin route - Direct access without API prefix
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

# Login page route
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Register page route
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})    

# Pricing page route
@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "UrVote.Rocks"}

# Client leaderboard route
@app.get("/client/{client_slug}/leaderboard", response_class=HTMLResponse)
async def client_leaderboard(
    client_slug: str, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Client-specific leaderboard"""
    # Get client data from database
    result = await db.execute(
        select(Client).where(Client.slug == client_slug)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get client's active contest
    contest_result = await db.execute(
        select(Contest).where(
            Contest.client_id == client.id,
            Contest.is_active == True
        )
    )
    contest = contest_result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(status_code=404, detail="No active contest found")
    
    # Get approved songs for this contest with vote counts
    songs_result = await db.execute(
        select(Song).where(
            Song.contest_id == contest.id,
            Song.is_approved == True
        ).order_by(Song.created_at.desc())
    )
    songs = songs_result.scalars().all()
    
    # Get vote counts for each song
    for song in songs:
        vote_count_result = await db.execute(
            select(func.count(Vote.id)).where(Vote.song_id == song.id)
        )
        song.vote_count = vote_count_result.scalar() or 0
    
    # Sort by vote count (highest first)
    songs.sort(key=lambda x: x.vote_count, reverse=True)
    
    return templates.TemplateResponse("client/leaderboard.html", {
        "request": request,
        "client": client,
        "contest": contest,
        "songs": songs
    })    

# Legacy upload endpoint (keeping for backward compatibility)
@app.post("/api/v1/upload")
async def legacy_upload(
    artist: str = None,
    email: str = None,
    file = None,
    request: Request = None
):
    """Legacy upload endpoint - redirects to new system"""
    return {"message": "Please use the new upload form at /upload"}