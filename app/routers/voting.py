from fastapi import APIRouter, Request, Depends
from typing import List
from ..auth import get_current_user
from .. import templates

router = APIRouter(prefix="/voting", tags=["voting"])

# API endpoints
@router.post("/vote")
async def cast_vote():
    # Voting logic here
    return {"message": "Vote cast"}

@router.get("/leaderboard")
async def get_leaderboard():
    # Leaderboard logic here
    return []

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