from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
import httpx

from ..database import get_db
from ..models import Vote, Song, User
from ..schemas import VoteCreate, VoteResponse
from ..auth import get_current_user, verify_token
from ..config import settings

router = APIRouter(prefix="/voting", tags=["voting"])

async def get_geoip_info(ip_address: str) -> dict:
    """Get GeoIP information for an IP address"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip_address}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "country_code": data.get("countryCode"),
                    "region": data.get("regionName"),
                    "city": data.get("city")
                }
    except:
        pass
    
    return {"country_code": None, "region": None, "city": None}

@router.post("/vote", response_model=VoteResponse)
async def cast_vote(
    vote_data: VoteCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Cast a vote for a song"""
    
    # Try to get current user if authentication header is present
    current_user = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            # Extract token and verify manually
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            if payload and payload.get("sub"):
                user_id = int(payload.get("sub"))
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if user and user.is_active:
                    current_user = user
        except:
            current_user = None
    
    # Check if song exists and is approved
    result = await db.execute(select(Song).where(Song.id == vote_data.song_id))
    song = result.scalar_one_or_none()
    
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    if not song.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot vote for unapproved songs"
        )
    
    # Get GeoIP information
    client_ip = request.client.host
    geoip_info = await get_geoip_info(client_ip)
    
    # Determine voter type and check existing votes
    if current_user:
        # Authenticated user voting
        voter_id = current_user.id
        voter_type = "authenticated"
        
        # Check if user already voted for this song today
        today = func.date(func.now())
        existing_vote = await db.execute(
            select(Vote).where(
                and_(
                    Vote.song_id == vote_data.song_id,
                    Vote.voter_id == current_user.id,
                    func.date(Vote.created_at) == today
                )
            )
        )
        
        if existing_vote.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already voted for this song today"
            )
    else:
        # Anonymous voting - check IP-based rate limiting
        voter_id = None
        voter_type = "anonymous"
        
        # Check if IP already voted for this song today (rate limiting)
        today = func.date(func.now())
        existing_vote = await db.execute(
            select(Vote).where(
                and_(
                    Vote.song_id == vote_data.song_id,
                    Vote.ip_address == client_ip,
                    Vote.voter_type == "anonymous",
                    func.date(Vote.created_at) == today
                )
            )
        )
        
        if existing_vote.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already voted for this song today. See you tomorrow!"
            )
    
    # Create vote
    try:
        new_vote = Vote(
            song_id=vote_data.song_id,
            voter_id=voter_id,
            voter_type=voter_type,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            recaptcha_score=vote_data.recaptcha_token,  # TODO: Add real reCAPTCHA
            country_code=geoip_info["country_code"],
            region=geoip_info["region"],
            city=geoip_info["city"]
        )
        
        print(f"DEBUG: Creating vote with voter_id={voter_id}, voter_type={voter_type}, ip={client_ip}")
        
        db.add(new_vote)
        await db.commit()
        await db.refresh(new_vote)
        
        print(f"DEBUG: Vote created successfully with ID {new_vote.id}")
        return new_vote
        
    except Exception as e:
        print(f"DEBUG: Error creating vote: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/leaderboard", response_model=List[dict])
async def get_leaderboard(
    country_filter: str = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard with optional country filtering"""
    
    # Build query to get songs with vote counts
    query = select(
        Song.id,
        Song.title,
        Song.artist_name,
        func.count(Vote.id).label("vote_count")
    ).join(Vote, Song.id == Vote.song_id)
    
    if country_filter:
        query = query.where(Vote.country_code == country_filter.upper())
    
    query = query.where(Song.is_approved == True).group_by(Song.id).order_by(
        func.count(Vote.id).desc()
    ).limit(limit)
    
    result = await db.execute(query)
    leaderboard = []
    
    for i, row in enumerate(result, 1):
        leaderboard.append({
            "rank": i,
            "song_id": row.id,
            "title": row.title,
            "artist_name": row.artist_name,
            "vote_count": row.vote_count
        })
    
    return leaderboard

@router.get("/stats", response_model=dict)
async def get_voting_stats(db: AsyncSession = Depends(get_db)):
    """Get overall voting statistics"""
    
    # Total votes
    total_votes = await db.execute(select(func.count(Vote.id)))
    total_votes = total_votes.scalar()
    
    # Total approved songs
    total_songs = await db.execute(select(func.count(Song.id)).where(Song.is_approved == True))
    total_songs = total_songs.scalar()
    
    # Votes by country
    country_stats = await db.execute(
        select(Vote.country_code, func.count(Vote.id)).group_by(Vote.country_code).order_by(
            func.count(Vote.id).desc()
        ).limit(10)
    )
    
    country_breakdown = [
        {"country": row.country_code, "votes": row.count} 
        for row in country_stats
    ]
    
    return {
        "total_votes": total_votes,
        "total_songs": total_songs,
        "country_breakdown": country_breakdown
    }

@router.get("/my-votes", response_model=List[VoteResponse])
async def get_user_votes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's voting history"""
    result = await db.execute(
        select(Vote).where(Vote.voter_id == current_user.id).order_by(Vote.created_at.desc())
    )
    votes = result.scalars().all()
    
    return votes
