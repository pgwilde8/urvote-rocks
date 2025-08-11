from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pathlib import Path
import hashlib
import time
import os

from ..database import get_db
from ..models import Song, User, Vote
from ..schemas import SongCreate, SongResponse, SongApproval
from ..auth import get_current_admin_user, get_current_user
from ..config import settings

router = APIRouter(prefix="/songs", tags=["songs"])

@router.get("/upload", response_class=HTMLResponse)
async def upload_form():
    """Show song upload form"""
    from ..templates.upload import upload
    return upload()

@router.post("/upload")
async def upload_song(
    title: str = Form(...),
    artist_name: str = Form(...),
    email: str = Form(...),
    genre: Optional[str] = Form(None),
    ai_tools_used: str = Form(...),
    description: Optional[str] = Form(None),
    license_type: str = Form("stream_only"),
    external_link: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload a new song submission"""
    
    # Validate file or external link
    if not file and not external_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file upload or external link is required"
        )
    
    # Handle file upload
    file_path = None
    file_size = 0
    file_hash = ""
    
    if file:
        # Validate file type
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}"
            )
        
        # Read file data
        data = await file.read()
        if len(data) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum: {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Generate file hash and path
        file_hash = hashlib.sha256(data).hexdigest()
        timestamp = int(time.time())
        safe_artist = "".join(c for c in artist_name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        safe_filename = f"{timestamp}__{safe_artist}__{file_hash[:10]}{ext}"
        file_path = str(Path(settings.upload_dir) / safe_filename)
        file_size = len(data)
        
        # Save file
        os.makedirs(Path(settings.upload_dir), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data)
    
    # Create song record
    new_song = Song(
        title=title,
        artist_name=artist_name,
        genre=genre,
        ai_tools_used=ai_tools_used,
        description=description,
        license_type=license_type,
        file_path=file_path or "",
        file_size=file_size,
        file_hash=file_hash,
        external_link=external_link,
        is_approved=False
    )
    
    db.add(new_song)
    await db.commit()
    await db.refresh(new_song)
    
    # Log submission
    logline = f'{int(time.time())},"{artist_name}","{email}","{title}",{file_size},"{file_hash}","{request.client.host if request else ""}","{file_path or external_link}"\n'
    log_file = Path(settings.upload_dir) / "submissions.csv"
    with open(log_file, "a", encoding="utf-8") as f:
        if f.tell() == 0:
            f.write("ts,artist,email,title,bytes,digest,ip,file_path\n")
        f.write(logline)
    
    return {
        "ok": True,
        "message": "Song submitted successfully! It will be reviewed by our team.",
        "song_id": new_song.id
    }

@router.get("/", response_model=List[SongResponse])
async def list_songs(
    approved_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List songs with optional filtering"""
    query = select(Song)
    
    if approved_only:
        query = query.where(Song.is_approved == True)
    
    query = query.offset(offset).limit(limit).order_by(Song.created_at.desc())
    
    result = await db.execute(query)
    songs = result.scalars().all()
    
    return songs

@router.get("/{song_id}", response_model=SongResponse)
async def get_song(song_id: int, db: AsyncSession = Depends(get_db)):
    """Get song details by ID"""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()
    
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    return song

@router.post("/{song_id}/approve", response_model=dict)
async def approve_song(
    song_id: int,
    approval: SongApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Approve or reject a song (admin only)"""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()
    
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    if approval.is_approved:
        song.is_approved = True
        song.is_rejected = False
        song.rejection_reason = None
        song.approved_at = func.now()
    else:
        song.is_approved = False
        song.is_rejected = True
        song.rejection_reason = approval.rejection_reason
    
    await db.commit()
    
    return {
        "message": f"Song {'approved' if approval.is_approved else 'rejected'} successfully",
        "song_id": song_id
    }

@router.get("/pending/approval", response_model=List[SongResponse])
async def get_pending_songs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get songs pending approval (admin only)"""
    result = await db.execute(
        select(Song).where(
            Song.is_approved == False,
            Song.is_rejected == False
        ).order_by(Song.created_at.asc())
    )
    songs = result.scalars().all()
    
    return songs
