from fastapi import APIRouter, Depends, Request
from ..auth import get_current_board_owner
from .. import templates

router = APIRouter(
    prefix="/board-owner",
    tags=["board-owner"]
)

@router.get("/dashboard")
async def dashboard(request: Request, current_user=Depends(get_current_board_owner)):
    return templates.TemplateResponse("board_owner/dashboard.html", {"request": request})

# Add more board owner routes here