from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .routers import auth, songs, voting
from . import admin
import os

from .routers import auth, songs, voting
from .config import settings

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
    allow_origins=["https://urvote.rocks", "https://www.urvote.rocks"],  # Configure appropriately for production
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

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "UrVote.Rocks"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
