from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from .database import get_db
from .models import User, Song, Vote, Contest
from .schemas import SongApproval
from .auth import get_current_admin_user
from .config import settings

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """Admin dashboard main page"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@router.get("/songs/pending", response_class=HTMLResponse)
async def pending_songs_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """Page showing songs pending approval"""
    return templates.TemplateResponse("admin/pending_songs.html", {"request": request})

@router.get("/api/songs/pending")
async def get_pending_songs_api(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """API endpoint to get songs pending approval"""
    result = await db.execute(
        select(Song).where(
            and_(
                Song.is_approved == False,
                Song.is_rejected == False
            )
        ).order_by(Song.created_at.asc())
    )
    songs = result.scalars().all()
    
    return songs

@router.post("/api/songs/{song_id}/approve")
async def approve_song_api(
    song_id: int,
    approval: SongApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """API endpoint to approve/reject a song"""
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
        song.approved_at = datetime.utcnow()
    else:
        song.is_approved = False
        song.is_rejected = True
        song.rejection_reason = approval.rejection_reason
    
    await db.commit()
    
    return {
        "message": f"Song {'approved' if approval.is_approved else 'rejected'} successfully",
        "song_id": song_id
    }

@router.get("/api/stats/overview")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get overview statistics for admin dashboard"""
    
    # Total counts
    total_users = await db.execute(select(func.count(User.id)))
    total_users = total_users.scalar()
    
    total_songs = await db.execute(select(func.count(Song.id)))
    total_songs = total_songs.scalar()
    
    total_votes = await db.execute(select(func.count(Vote.id)))
    total_votes = total_votes.scalar()
    
    # Pending approvals
    pending_songs = await db.execute(
        select(func.count(Song.id)).where(
            and_(Song.is_approved == False, Song.is_rejected == False)
        )
    )
    pending_songs = pending_songs.scalar()
    
    # Recent activity
    recent_songs = await db.execute(
        select(Song).order_by(Song.created_at.desc()).limit(5)
    )
    recent_songs = recent_songs.scalars().all()
    
    recent_votes = await db.execute(
        select(Vote).order_by(Vote.created_at.desc()).limit(10)
    )
    recent_votes = recent_votes.scalars().all()
    
    # Daily stats for the last 7 days
    daily_stats = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Songs submitted
        songs_count = await db.execute(
            select(func.count(Song.id)).where(
                and_(Song.created_at >= start_of_day, Song.created_at < end_of_day)
            )
        )
        songs_count = songs_count.scalar()
        
        # Votes cast
        votes_count = await db.execute(
            select(func.count(Vote.id)).where(
                and_(Vote.created_at >= start_of_day, Vote.created_at < end_of_day)
            )
        )
        votes_count = votes_count.scalar()
        
        daily_stats.append({
            "date": date.strftime("%Y-%m-%d"),
            "songs": songs_count,
            "votes": votes_count
        })
    
    return {
        "overview": {
            "total_users": total_users,
            "total_songs": total_songs,
            "total_votes": total_votes,
            "pending_songs": pending_songs
        },
        "recent_songs": recent_songs,
        "recent_votes": recent_votes,
        "daily_stats": daily_stats
    }

@router.get("/api/users")
async def get_users(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get list of users for admin management"""
    result = await db.execute(
        select(User).offset(offset).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    
    return users

@router.post("/api/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle user active/inactive status"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    await db.commit()
    
    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "user_id": user_id,
        "is_active": user.is_active
    }

@router.get("/api/export/voters")
async def export_voters(
    song_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Export voter information for marketing purposes"""
    
    if song_id:
        # Export voters for specific song
        result = await db.execute(
            select(Vote).where(Vote.song_id == song_id)
        )
        votes = result.scalars().all()
    else:
        # Export all voters
        result = await db.execute(select(Vote))
        votes = result.scalars().all()
    
    # Format for export
    export_data = []
    for vote in votes:
        export_data.append({
            "email": vote.voter.email if vote.voter else "Unknown",
            "ip_address": vote.ip_address,
            "country": vote.country_code,
            "voted_at": vote.created_at.isoformat(),
            "song_id": vote.song_id
        })
    
    return export_data
