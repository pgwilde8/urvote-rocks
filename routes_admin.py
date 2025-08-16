import os
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Board, Song
from db import get_async_session
from starlette.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/upload", response_class=HTMLResponse)
async def admin_upload_form(request: Request, session: AsyncSession = Depends(get_async_session)):
    boards = (await session.execute(select(Board))).scalars().all()
    return templates.TemplateResponse("admin_upload.html", {"request": request, "boards": boards})

@router.post("/admin/upload", response_class=HTMLResponse)
async def admin_upload_submit(
    request: Request,
    title: str = Form(...),
    artist_name: str = Form(...),
    url: str = Form(...),
    social_link: str = Form(None),
    board_id: int = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    board = (await session.execute(select(Board).where(Board.id == board_id))).scalar_one_or_none()
    if not board:
        raise HTTPException(400, "Board not found")
    song = Song(
        title=title,
        artist_name=artist_name,
        url=url,
        social_link=social_link,
        board_id=board_id,
    )
    session.add(song)
    await session.commit()
    return RedirectResponse(url=f"/board/{board.slug}", status_code=303)
