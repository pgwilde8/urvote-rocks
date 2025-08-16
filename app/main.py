# app/main.py
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile, APIRouter, Request, HTTPException
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
from .routers import auth, songs, voting, songboards, signup, static_pages
from . import admin
from app.routers import submitter, board_owner

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

# ------------------------------------------------------------------------------
# Static & Templates
# ------------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ------------------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------------------
# API namespace
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(songs.router, prefix="/api", tags=["songs"])
app.include_router(voting.router, prefix="/api", tags=["voting"])
app.include_router(admin.router, prefix="/api", tags=["admin"])

# Site features
app.include_router(songboards.router, tags=["songboards"])   # replaces campaigns
app.include_router(signup.router, tags=["signup"])
app.include_router(submitter.router, tags=["submitter"])
app.include_router(board_owner.router, tags=["board_owner"])
# app.include_router(sales.router, tags=["sales"])  # Removed because 'sales' is not defined


# ------------------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("lander.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

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

# Public pricing: redirect to sales module
@app.get("/pricing")
async def redirect_to_sales_pricing():
    return RedirectResponse(url="/sales/pricing", status_code=307)

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

