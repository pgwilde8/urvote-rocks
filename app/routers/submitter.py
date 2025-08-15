from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import Song, User
from ..auth import get_current_user
from .. import templates
from ..routers.songs import upload_song_logic  # Import your upload logic

router = APIRouter(
    prefix="/submitter",
    tags=["submitter"]
)

@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("submitter/upload.html", {"request": request})

@router.post("/upload", response_class=HTMLResponse)
async def handle_upload_form(
    request: Request,
    title: str = Form(...),
    artist_name: str = Form(...),
    email: str = Form(...),
    genre: str = Form(None),
    ai_tools_used: str = Form(...),
    description: str = Form(None),
    license_type: str = Form("stream_only"),
    external_link: str = Form(None),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        song = await upload_song_logic(
            title=title,
            artist_name=artist_name,
            email=email,
            genre=genre,
            ai_tools_used=ai_tools_used,
            description=description,
            license_type=license_type,
            external_link=external_link,
            file=file,
            request=request,
            db=db
        )
        return RedirectResponse(
            url=f"/submitter/upload/success?song_id={song.id}",
            status_code=303
        )
    except HTTPException as e:
        return templates.TemplateResponse("submitter/upload.html", {
            "request": request,
            "error": e.detail
        })

@router.get("/upload/success", response_class=HTMLResponse)
async def upload_success(request: Request, song_id: int = None, db: AsyncSession = Depends(get_db)):
    song_data = None
    if song_id:
        result = await db.execute(select(Song).where(Song.id == song_id))
        song_data = result.scalar_one_or_none()
    return templates.TemplateResponse("submitter/upload-success.html", {
        "request": request,
        "song": song_data
    })