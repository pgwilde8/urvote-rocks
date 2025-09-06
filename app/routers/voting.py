from fastapi import APIRouter, Request, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import re
from ..database import get_db
from ..models import Vote, Song, Video, Visual, Board
from ..utils import is_disposable_email, verify_recaptcha, is_suspicious_vote
from ..auth import get_current_user
from .. import templates

router = APIRouter(prefix="/voting", tags=["voting"])

class AnonymousVoteRequest:
    def __init__(
        self,
        media_type: str = Form(...),
        media_id: int = Form(...),
        voter_email: str = Form(...),
        voter_name: Optional[str] = Form(None),
        recaptcha_token: Optional[str] = Form(None)
    ):
        self.media_type = media_type
        self.media_id = media_id
        self.voter_email = voter_email
        self.voter_name = voter_name
        self.recaptcha_token = recaptcha_token

@router.post("/vote/anonymous")
async def cast_anonymous_vote(
    request: Request,
    media_type: str = Form(...),
    media_id: int = Form(...),
    voter_email: str = Form(...),
    voter_name: Optional[str] = Form(None),
    recaptcha_token: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Cast an anonymous vote with fraud prevention
    """
    try:
        # Get client IP and user agent
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Validate email
        if not voter_email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', voter_email):
            raise HTTPException(status_code=400, detail="Valid email address required")
        
        # Check for disposable email
        if is_disposable_email(voter_email):
            raise HTTPException(status_code=400, detail="Disposable email addresses not allowed")
        
        # Verify reCAPTCHA
        recaptcha_score = 0.5  # Default score
        if recaptcha_token:
            recaptcha_score = await verify_recaptcha(recaptcha_token, client_ip)
        
        # Check for suspicious activity
        if is_suspicious_vote(client_ip, user_agent, recaptcha_score):
            raise HTTPException(status_code=400, detail="Vote rejected due to suspicious activity")
        
        # Check if user already voted today
        today = datetime.now().date()
        existing_vote = await db.execute(
            select(Vote).where(
                and_(
                    Vote.voter_email == voter_email,
                    Vote.media_type == media_type,
                    Vote.media_id == media_id,
                    func.date(Vote.created_at) == today
                )
            )
        )
        
        if existing_vote.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="You have already voted on this content today")
        
        # Verify the content exists and is approved
        content = None
        if media_type == "music":
            content = await db.execute(select(Song).where(Song.id == media_id, Song.is_approved == True))
        elif media_type == "video":
            content = await db.execute(select(Video).where(Video.id == media_id, Video.is_approved == True))
        elif media_type == "visuals":
            content = await db.execute(select(Visual).where(Visual.id == media_id, Visual.is_approved == True))
        
        if not content.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Content not found or not approved")
        
        # Generate device fingerprint
        device_fingerprint = hashlib.sha256(
            f"{client_ip}{user_agent}".encode()
        ).hexdigest()[:32]
        
        # Create vote record
        new_vote = Vote(
            media_type=media_type,
            media_id=media_id,
            voter_type="anonymous",
            voter_email=voter_email,
            voter_name=voter_name,
            vote_type="like",
            ip_address=client_ip,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            recaptcha_score=str(recaptcha_score),
            votes_per_email_per_day=1
        )
        
        db.add(new_vote)
        await db.commit()
        await db.refresh(new_vote)
        
        return {
            "success": True,
            "message": "Vote cast successfully!",
            "vote_id": new_vote.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error casting vote: {str(e)}")

@router.get("/leaderboard/{board_id}")
async def get_leaderboard(
    board_id: int,
    media_type: str = "music",
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Get leaderboard for a specific board
    """
    try:
        # Verify board exists
        board = await db.execute(select(Board).where(Board.id == board_id))
        if not board.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Get content with vote counts
        if media_type == "music":
            query = select(
                Song.id,
                Song.title,
                Song.artist_name,
                Song.file_path,
                Song.external_link,
                func.count(Vote.id).label("vote_count")
            ).select_from(
                Song.outerjoin(Vote, and_(
                    Vote.media_type == "music",
                    Vote.media_id == Song.id
                ))
            ).where(
                Song.board_id == board_id,
                Song.is_approved == True
            ).group_by(Song.id).order_by(func.count(Vote.id).desc()).limit(limit)
        
        elif media_type == "video":
            query = select(
                Video.id,
                Video.title,
                Video.artist_name,
                Video.file_path,
                Video.external_link,
                func.count(Vote.id).label("vote_count")
            ).select_from(
                Video.outerjoin(Vote, and_(
                    Vote.media_type == "video",
                    Vote.media_id == Video.id
                ))
            ).where(
                Video.board_id == board_id,
                Video.is_approved == True
            ).group_by(Video.id).order_by(func.count(Vote.id).desc()).limit(limit)
        
        elif media_type == "visuals":
            query = select(
                Visual.id,
                Visual.title,
                Visual.artist_name,
                Visual.file_path,
                Visual.external_link,
                func.count(Vote.id).label("vote_count")
            ).select_from(
                Visual.outerjoin(Vote, and_(
                    Vote.media_type == "visuals",
                    Vote.media_id == Visual.id
                ))
            ).where(
                Visual.board_id == board_id,
                Visual.is_approved == True
            ).group_by(Visual.id).order_by(func.count(Vote.id).desc()).limit(limit)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid media type")
        
        result = await db.execute(query)
        leaderboard = result.fetchall()
        
        return {
            "success": True,
            "board_id": board_id,
            "media_type": media_type,
            "leaderboard": [
                {
                    "id": row.id,
                    "title": row.title,
                    "artist_name": row.artist_name,
                    "file_path": row.file_path,
                    "external_link": row.external_link,
                    "vote_count": row.vote_count
                }
                for row in leaderboard
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leaderboard: {str(e)}")

@router.get("/stats/{board_id}")
async def get_voting_stats(
    board_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get voting statistics for a board
    """
    try:
        # Get total votes
        total_votes = await db.execute(
            select(func.count(Vote.id)).where(Vote.media_id.in_(
                select(Song.id).where(Song.board_id == board_id)
            ))
        )
        
        # Get unique voters
        unique_voters = await db.execute(
            select(func.count(func.distinct(Vote.voter_email))).where(Vote.media_id.in_(
                select(Song.id).where(Song.board_id == board_id)
            ))
        )
        
        # Get votes by country
        country_stats = await db.execute(
            select(
                Vote.country_code,
                func.count(Vote.id).label("vote_count")
            ).where(Vote.media_id.in_(
                select(Song.id).where(Song.board_id == board_id)
            )).group_by(Vote.country_code).order_by(func.count(Vote.id).desc())
        )
        
        return {
            "success": True,
            "board_id": board_id,
            "total_votes": total_votes.scalar(),
            "unique_voters": unique_voters.scalar(),
            "votes_by_country": [
                {"country": row.country_code, "votes": row.vote_count}
                for row in country_stats.fetchall()
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@router.get("/vote/{media_type}/{media_id}")
async def show_vote_form(
    media_type: str,
    media_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Show voting form for a specific piece of content
    """
    try:
        # Get content details
        content = None
        if media_type == "music":
            result = await db.execute(select(Song).where(Song.id == media_id, Song.is_approved == True))
        elif media_type == "video":
            result = await db.execute(select(Video).where(Video.id == media_id, Video.is_approved == True))
        elif media_type == "visuals":
            result = await db.execute(select(Visual).where(Visual.id == media_id, Visual.is_approved == True))
        else:
            raise HTTPException(status_code=400, detail="Invalid media type")
        
        content = result.scalar_one_or_none()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found or not approved")
        
        return templates.TemplateResponse("vote_form.html", {
            "request": request,
            "content": content
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading vote form: {str(e)}")

@router.get("/stats")
async def get_voting_stats():
    # Stats logic here
    return {}

@router.get("/my-votes")
async def get_user_votes():
    # User voting history logic here
    return []

# Template route (from voter.py)
@router.get("/leaderboard-page")
async def leaderboard_page(request: Request):
    return templates.TemplateResponse("voter/leaderboard.html", {"request": request})