# app/routes/songboards.py
from datetime import datetime
from typing import Any, Dict, List, Optional

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Client, Contest, Song, Vote
from app.dependencies import get_current_board_owner

logger = logging.getLogger(__name__)

router = APIRouter(tags=["songboards"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/board-owner-area")
async def board_owner_area(current_owner=Depends(get_current_board_owner)):
    return {"message": f"Welcome, {current_owner.username}!"}


@router.get("/songboards", response_class=HTMLResponse)
async def songboards_page(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Songboards page with dynamic data.
    Shows active contests, pins PayPortPro first, and renders site-wide stats.
    """
    try:
        # Active contests + clients
        result = await db.execute(
            select(Contest, Client)
            .join(Client, Contest.client_id == Client.id)
            .where(Contest.is_active.is_(True))
            .order_by(Contest.created_at.desc())
        )
        contests_with_clients: List[tuple[Contest, Client]] = list(result.all())

        # Sort: PayPortPro first, then by created_at
        contests_with_clients.sort(
            key=lambda cc: (0 if cc[1].slug == "payportpro" else 1, cc[0].created_at or datetime.min)
        )

        songboards: List[Dict[str, Any]] = []
        for contest, client in contests_with_clients:
            # Song count
            songs_result = await db.execute(
                select(func.count(Song.id)).where(Song.contest_id == contest.id)
            )
            song_count = songs_result.scalar() or 0

            # Vote count (JOIN instead of IN-subquery)
            votes_result = await db.execute(
                select(func.count(Vote.id))
                .select_from(Vote)
                .join(Song, Song.id == Vote.song_id)
                .where(Song.contest_id == contest.id)
            )
            vote_count = votes_result.scalar() or 0

            # Per-client configuration
            if client.slug == "payportpro":
                songboard_type = "patriotic"
                colors = "from-red-500 to-blue-600"
                features = ["🎵 Patriotic Theme", "🇺🇸 American Values", "🤖 AI-Generated", "🗳️ Community Voting"]
                action_text = "Enter Contest"
                action_url = f"/songboards/{client.slug}/american-greatness"
            elif client.slug == "soundofchi":
                songboard_type = "community"
                colors = "from-purple-500 to-pink-600"
                features = ["🎵 Community Playlist", "🤖 AI-Generated", "📱 Spotify-Style", "🌍 Global Community"]
                action_text = "View Playlist"
                action_url = f"/songboards/{client.slug}/playlist"
            elif client.slug == "jerichohomestead":
                songboard_type = "spiritual"
                colors = "from-green-500 to-teal-600"
                features = ["🙏 Sacred Music", "🏠 Community", "🤖 AI-Generated", "🌿 Spiritual"]
                action_text = "Enter Contest"
                action_url = f"/songboards/{client.slug}/house-of-mary-joseph"
            else:
                songboard_type = "generic"
                colors = "from-blue-500 to-indigo-600"
                features = ["🎵 AI-Generated", "🤖 AI Music", "🗳️ Community Voting", "🎯 Contest"]
                action_text = "Enter Contest"
                action_url = f"/songboards/{client.slug}/{contest.id}"

            songboards.append({
                "client_name": client.name,
                "client_slug": client.slug,
                "contest_name": contest.name,
                "contest_id": contest.id,
                "description": contest.description or "AI-generated music contest",
                "song_count": song_count,
                "vote_count": vote_count,
                "songboard_type": songboard_type,
                "colors": colors,
                "features": features,
                "action_text": action_text,
                "action_url": action_url,
                "website_url": client.website_url,
                "website_display": client.website_url,
                "end_date": contest.end_date,
                "is_always_open": contest.end_date is None,
                "created_at": contest.created_at,
            })

        # Fallback demo data if empty
        if not songboards:
            logger.info("No songboards found in DB; serving fallback examples.")
            songboards = [
                {
                    "client_name": "PayPortPro",
                    "client_slug": "payportpro",
                    "contest_name": "American Greatness",
                    "contest_id": 1,
                    "description": "Show us your best AI-generated patriotic music! Brought to you by PayPortPro - Bridging Dollars To Stable Coins",
                    "song_count": 15,
                    "vote_count": 127,
                    "songboard_type": "patriotic",
                    "colors": "from-red-500 to-blue-600",
                    "features": ["🎵 Patriotic Theme", "🇺🇸 American Values", "🤖 AI-Generated", "🗳️ Community Voting"],
                    "action_text": "Enter Contest",
                    "action_url": "/songboards/payportpro/american-greatness",
                    "website_url": "https://www.payportpro.com",
                    "website_display": "www.payportpro.com",
                    "end_date": None,
                    "is_always_open": True,
                    "created_at": datetime(2024, 1, 15),
                },
                # ... add any other demo entries as needed ...
            ]

        # Site-wide stats
        try:
            total_songs = (await db.execute(select(func.count(Song.id)))).scalar() or 0
            total_votes = (
                await db.execute(select(func.count(Vote.id)).select_from(Vote))
            ).scalar() or 0
            total_songboards = len(songboards)
        except Exception as e:
            logger.warning("Stats fallback due to error: %s", e)
            total_songs = sum(c["song_count"] for c in songboards)
            total_votes = sum(c["vote_count"] for c in songboards)
            total_songboards = len(songboards)

        return templates.TemplateResponse(
            "songboards.html",
            {
                "request": request,
                "songboards": songboards,
                "platform_stats": {
                    "total_songboards": total_songboards,
                    "total_songs": total_songs,
                    "total_votes": total_votes,
                    "active_users": max(1, total_votes // 10) if total_votes > 0 else 1,
                },
            },
        )

    except Exception as e:
        logger.exception("Error loading songboards: %s", e)
        # Try to still show stats
        try:
            total_songs = (await db.execute(select(func.count(Song.id)))).scalar() or 0
            total_votes = (await db.execute(select(func.count(Vote.id)))).scalar() or 0
        except Exception:
            total_songs = 0
            total_votes = 0

        return templates.TemplateResponse(
            "songboards.html",
            {
                "request": request,
                "songboards": [],
                "platform_stats": {
                    "total_songboards": 0,
                    "total_songs": total_songs,
                    "total_votes": total_votes,
                    "active_users": max(1, total_votes // 10) if total_votes > 0 else 1,
                },
            },
        )


@router.get("/songboards/create", response_class=HTMLResponse)
async def create_songboard_page(request: Request):
    """Songboard creation page."""
    return templates.TemplateResponse("songboards/create.html", {"request": request})


@router.get("/songboards/{client_slug}/{contest_slug}", response_class=HTMLResponse)
async def songboard_detail_page(
    request: Request,
    client_slug: str,
    contest_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Individual songboard page.
    Known client/slug combos map to static templates; others render a generic dynamic page.
    """
    # Known routes → static templates
    if client_slug == "jerichohomestead" and contest_slug == "house-of-mary-joseph":
        return templates.TemplateResponse("songboards/jerichohomestead.html", {"request": request})
    if client_slug == "soundofchi" and contest_slug == "playlist":
        return templates.TemplateResponse("songboards/soundofchi.html", {"request": request})
    if client_slug == "payportpro" and contest_slug == "american-greatness":
        return templates.TemplateResponse("songboards/payportpro.html", {"request": request})

    # Dynamic fallback
    try:
        client = (
            await db.execute(select(Client).where(Client.slug == client_slug))
        ).scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        contest: Optional[Contest] = None
        # contest_slug might be an int id; else try ilike by name
        try:
            contest_id = int(contest_slug)
            contest = (
                await db.execute(
                    select(Contest).where(
                        Contest.id == contest_id, Contest.client_id == client.id
                    )
                )
            ).scalar_one_or_none()
        except ValueError:
            contest = (
                await db.execute(
                    select(Contest)
                    .where(Contest.client_id == client.id)
                    .where(Contest.name.ilike(f"%{contest_slug}%"))
                    .order_by(Contest.created_at.desc())
                )
            ).scalar_one_or_none()

        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")

        songs = (
            await db.execute(select(Song).where(Song.contest_id == contest.id))
        ).scalars().all()

        stats = {
            "total_songs": len(songs),
            "total_votes": 0,  # (optional) compute with a JOIN if needed
            "active_voters": 0,
        }

        featured_song = songs[0] if songs else None

        return templates.TemplateResponse(
            "songboards/dynamic.html",
            {
                "request": request,
                "contest": contest,
                "client": client,
                "songs": songs,
                "stats": stats,
                "featured_song": featured_song,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error loading dynamic songboard: %s", e)
        return templates.TemplateResponse(
            "songboards/dynamic.html",
            {
                "request": request,
                "contest": {"name": "Unknown Contest", "description": "Contest details unavailable"},
                "client": {"name": "Unknown Client", "slug": client_slug, "website_url": None},
                "songs": [],
                "stats": {"total_songs": 0, "total_votes": 0, "active_voters": 0},
                "featured_song": None,
            },
        )


@router.get("/songboards/api/count")
async def get_songboard_count(db: AsyncSession = Depends(get_db)):
    """API endpoint to get total count of active contests."""
    try:
        count = (
            await db.execute(select(func.count(Contest.id)).where(Contest.is_active.is_(True)))
        ).scalar() or 0
        return {"count": count}
    except Exception as e:
        logger.warning("Error getting songboard count: %s", e)
        return {"count": 0}


@router.get("/songboards/debug/songboards")
async def debug_songboards(db: AsyncSession = Depends(get_db)):
    """Debug endpoint to check database connection and counts."""
    try:
        contest_count = (await db.execute(select(func.count(Contest.id)))).scalar() or 0
        client_count = (await db.execute(select(func.count(Client.id)))).scalar() or 0
        song_count = (await db.execute(select(func.count(Song.id)))).scalar() or 0
        return {
            "status": "success",
            "database": "connected",
            "counts": {
                "contests": contest_count,
                "clients": client_count,
                "songs": song_count,
            },
        }
    except Exception as e:
        logger.error("DB debug failed: %s", e)
        return {"status": "error", "database": "disconnected", "error": str(e)}
