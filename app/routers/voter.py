from fastapi import APIRouter, Request, Depends
from ..auth import get_current_user
from .. import templates

router = APIRouter(
    prefix="/voter",
    tags=["voter"]
)

@router.get("/leaderboard")
async def leaderboard(request: Request):
    return templates.TemplateResponse("voter/leaderboard.html", {"request": request})# Add more voter routes here