from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Dict, Any

from app.models import Contest, Client, Song, Vote
from app.database import get_db

router = APIRouter(tags=["campaigns"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/campaigns", response_class=HTMLResponse)
async def campaigns_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Campaigns page with dynamic data"""
    try:
        # Get all active contests with their client information
        result = await db.execute(
            select(Contest, Client)
            .join(Client, Contest.client_id == Client.id)
            .where(Contest.is_active == True)
            .order_by(Contest.created_at.desc())
        )
        contests_with_clients = result.all()
        
        print(f"DEBUG: Found {len(contests_with_clients)} contests in database")
        
        # Prepare campaign data for template
        campaigns = []
        for contest, client in contests_with_clients:
            print(f"DEBUG: Processing contest: {contest.name} for client: {client.name}")
            
            # Get song count for this contest
            songs_result = await db.execute(
                select(func.count(Song.id)).where(Song.contest_id == contest.id)
            )
            song_count = songs_result.scalar() or 0
            
            # Get vote count for this contest (from Vote table)
            votes_result = await db.execute(
                select(func.count(Vote.id)).where(Vote.song_id.in_(
                    select(Song.id).where(Song.contest_id == contest.id)
                ))
            )
            vote_count = votes_result.scalar() or 0
            
            # Determine campaign type and styling based on client and contest name
            if client.slug == "payportpro":
                campaign_type = "patriotic"
                colors = "from-red-500 to-blue-600"
                features = ["🎵 Patriotic Theme", "🇺🇸 American Values", "🤖 AI-Generated", "🗳️ Community Voting"]
                action_text = "Enter Contest"
                action_url = f"/campaigns/{client.slug}/american-greatness"
            elif client.slug == "soundofchi":
                campaign_type = "community"
                colors = "from-purple-500 to-pink-600"
                features = ["🎵 Community Playlist", "🤖 AI-Generated", "📱 Spotify-Style", "🌍 Global Community"]
                action_text = "View Playlist"
                action_url = f"/campaigns/{client.slug}/playlist"
            elif client.slug == "jerichohomestead":
                campaign_type = "spiritual"
                colors = "from-green-500 to-teal-600"
                features = ["🙏 Sacred Music", "🏠 Community", "🤖 AI-Generated", "🌿 Spiritual"]
                action_text = "Enter Contest"
                action_url = f"/campaigns/{client.slug}/house-of-mary-joseph"
            else:
                # Generic campaign for any new ones
                campaign_type = "generic"
                colors = "from-blue-500 to-indigo-600"
                features = ["🎵 AI-Generated", "🤖 AI Music", "🗳️ Community Voting", "🎯 Contest"]
                action_text = "Enter Contest"
                action_url = f"/campaigns/{client.slug}/{contest.id}"
            
            campaigns.append({
                "client_name": client.name,
                "client_slug": client.slug,
                "contest_name": contest.name,
                "contest_id": contest.id,
                "description": contest.description or "AI-generated music contest",
                "song_count": song_count,
                "vote_count": vote_count,
                "campaign_type": campaign_type,
                "colors": colors,
                "features": features,
                "action_text": action_text,
                "action_url": action_url,
                "website_url": client.website_url,
                "website_display": client.website_url,
                "end_date": contest.end_date,
                "is_always_open": not contest.end_date,
                "created_at": contest.created_at
            })
        
        # If no campaigns in database, create default campaigns
        if not campaigns:
            print("DEBUG: No campaigns found in database, using fallback data")
            campaigns = [
                {
                    "client_name": "PayPortPro",
                    "client_slug": "payportpro",
                    "contest_name": "American Greatness",
                    "contest_id": 1,
                    "description": "Show us your best AI-generated patriotic music! Brought to you by PayPortPro - Bridging Dollars To Stable Coins",
                    "song_count": 15,
                    "vote_count": 127,
                    "campaign_type": "patriotic",
                    "colors": "from-red-500 to-blue-600",
                    "features": ["🎵 Patriotic Theme", "🇺🇸 American Values", "🤖 AI-Generated", "🗳️ Community Voting"],
                    "action_text": "Enter Contest",
                    "action_url": "/campaigns/payportpro/american-greatness",
                    "website_url": "https://www.payportpro.com",
                    "website_display": "www.payportpro.com",
                    "end_date": None,
                    "is_always_open": False,
                    "created_at": datetime(2024, 1, 15)
                },
                {
                    "client_name": "Sound of Chi",
                    "client_slug": "soundofchi",
                    "contest_name": "Community Playlist Contest",
                    "contest_id": 2,
                    "description": "Like Spotify playlists, but with AI-generated music! Upload your songs, vote for favorites, and build the ultimate community-curated playlist.",
                    "song_count": 8,
                    "vote_count": 43,
                    "campaign_type": "community",
                    "colors": "from-purple-500 to-pink-600",
                    "features": ["🎵 Community Playlist", "🤖 AI-Generated", "📱 Spotify-Style", "🌍 Global Community"],
                    "action_text": "View Playlist",
                    "action_url": "/campaigns/soundofchi/playlist",
                    "website_url": "https://soundcloud.com/sound-of-chi",
                    "website_display": "soundcloud.com/sound-of-chi",
                    "end_date": None,
                    "is_always_open": True,
                    "created_at": datetime(2024, 1, 10)
                },
                {
                    "client_name": "Jericho Homestead",
                    "client_slug": "jerichohomestead",
                    "contest_name": "The House of Mary & Joseph",
                    "contest_id": 3,
                    "description": "Sacred music for spiritual reflection and community building. AI-generated hymns and worship songs that inspire faith and hope.",
                    "song_count": 0,
                    "vote_count": 0,
                    "campaign_type": "spiritual",
                    "colors": "from-green-500 to-teal-600",
                    "features": ["🙏 Sacred Music", "🏠 Community", "🤖 AI-Generated", "🌿 Spiritual"],
                    "action_text": "Enter Contest",
                    "action_url": "/campaigns/jerichohomestead/house-of-mary-joseph",
                    "website_url": "https://www.jerichohomestead.org",
                    "website_display": "www.jerichohomestead.org",
                    "end_date": None,
                    "is_always_open": True,
                    "created_at": datetime(2024, 1, 20)
                }
            ]
        
        # Get platform-wide stats from database (site-wide totals)
        try:
            # Get total songs across all contests
            total_songs_result = await db.execute(select(func.count(Song.id)))
            total_songs = total_songs_result.scalar() or 0
            
            # Get total votes across all songs
            total_votes_result = await db.execute(select(func.count(Vote.id)))
            total_votes = total_votes_result.scalar() or 0
            
            # Get total campaigns
            total_campaigns = len(campaigns)
            
            print(f"DEBUG: Site-wide stats - Songs: {total_songs}, Votes: {total_votes}, Campaigns: {total_campaigns}")
            
        except Exception as e:
            print(f"Error getting site-wide stats: {str(e)}")
            # Fallback to campaign-based stats
            total_songs = sum(c["song_count"] for c in campaigns)
            total_votes = sum(c["vote_count"] for c in campaigns)
            total_campaigns = len(campaigns)
        
        return templates.TemplateResponse("campaigns.html", {
            "request": request,
            "campaigns": campaigns,
            "platform_stats": {
                "total_campaigns": total_campaigns,
                "total_songs": total_songs,
                "total_votes": total_votes,
                "active_users": max(1, total_votes // 10) if total_votes > 0 else 1
            }
        })
        
    except Exception as e:
        print(f"Error loading campaigns: {str(e)}")
        # Fallback to static template with default data
        try:
            # Even in fallback, try to get site-wide stats
            total_songs_result = await db.execute(select(func.count(Song.id)))
            total_songs = total_songs_result.scalar() or 0
            
            total_votes_result = await db.execute(select(func.count(Vote.id)))
            total_votes = total_votes_result.scalar() or 0
            
            print(f"DEBUG: Fallback site-wide stats - Songs: {total_songs}, Votes: {total_votes}")
            
        except Exception as stats_error:
            print(f"Error getting fallback stats: {str(stats_error)}")
            total_songs = 0
            total_votes = 0
        
        return templates.TemplateResponse("campaigns.html", {
            "request": request,
            "campaigns": [],
            "platform_stats": {
                "total_campaigns": 0,
                "total_songs": total_songs,
                "total_votes": total_votes,
                "active_users": max(1, total_votes // 10) if total_votes > 0 else 1
            }
        })

@router.get("/create", response_class=HTMLResponse)
async def create_campaign_page(request: Request):
    """Campaign creation page"""
    return templates.TemplateResponse("campaigns/create.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page for premium subscription"""
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """Pricing page for premium subscription"""
    return templates.TemplateResponse("pricing.html", {"request": request})

@router.get("/{client_slug}/{contest_slug}", response_class=HTMLResponse)
async def campaign_detail_page(request: Request, client_slug: str, contest_slug: str):
    """Individual campaign page"""
    # Route to specific templates based on client and contest
    if client_slug == "jerichohomestead" and contest_slug == "house-of-mary-joseph":
        return templates.TemplateResponse("campaigns/jerichohomestead.html", {"request": request})
    elif client_slug == "soundofchi" and contest_slug == "playlist":
        return templates.TemplateResponse("campaigns/soundofchi.html", {"request": request})
    elif client_slug == "payportpro" and contest_slug == "american-greatness":
        return templates.TemplateResponse("campaigns/payportpro.html", {"request": request})
    else:
        # Generic dynamic template for unknown campaigns
        return templates.TemplateResponse("campaigns/dynamic.html", {"request": request})

@router.get("/api/count")
async def get_campaign_count(db: AsyncSession = Depends(get_db)):
    """API endpoint to get total count of active contests"""
    try:
        result = await db.execute(select(func.count(Contest.id)).where(Contest.is_active == True))
        count = result.scalar() or 0
        return {"count": count}
    except Exception as e:
        print(f"Error getting campaign count: {str(e)}")
        return {"count": 0}

@router.get("/debug/campaigns")
async def debug_campaigns(db: AsyncSession = Depends(get_db)):
    """Debug endpoint to check database connection and counts"""
    try:
        # Check Contest table
        contests_result = await db.execute(select(func.count(Contest.id)))
        contest_count = contests_result.scalar() or 0
        
        # Check Client table
        clients_result = await db.execute(select(func.count(Client.id)))
        client_count = clients_result.scalar() or 0
        
        # Check Song table
        songs_result = await db.execute(select(func.count(Song.id)))
        song_count = songs_result.scalar() or 0
        
        return {
            "status": "success",
            "database": "connected",
            "counts": {
                "contests": contest_count,
                "clients": client_count,
                "songs": song_count
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }
