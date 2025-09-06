from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database import get_db
from app.models import Board, User, Song, Video, Visual, Vote
import os
import uuid
import hashlib
import re

# File size limits (in bytes)
MAX_MUSIC_SIZE = 50 * 1024 * 1024      # 50MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024     # 100MB  
MAX_VISUAL_SIZE = 25 * 1024 * 1024     # 25MB

router = APIRouter(
    prefix="/api/boards",
    tags=["boards"]
)

@router.get("/{board_id}/content")
async def get_board_content(
    board_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None, description="Filter by content type: music, video, visuals"),
    db: AsyncSession = Depends(get_db)
):
    """Get content for a specific Media Board"""
    try:
        # First check if board exists
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Build content query based on board's media type preferences
        content_items = []
        
        # Get music content if board allows it
        if board.allow_music:
            music_query = select(Song).where(Song.board_id == board_id)
            if content_type and content_type != "music":
                music_query = music_query.where(False)  # Don't include if filtering for other types
            
            music_res = await db.execute(music_query)
            music_items = music_res.scalars().all()
            
            for song in music_items:
                # Get vote counts for this song
                upvotes_res = await db.execute(
                    select(func.count(Vote.id)).where(
                        Vote.media_type == "music",
                        Vote.media_id == song.id,
                        Vote.vote_type == "like"
                    )
                )
                downvotes_res = await db.execute(
                    select(func.count(Vote.id)).where(
                        Vote.media_type == "music",
                        Vote.media_id == song.id,
                        Vote.vote_type == "dislike"
                    )
                )
                
                content_items.append({
                    "id": song.id,
                    "title": song.title,
                    "artist_name": song.artist_name,
                    "description": song.description,
                    "genre": song.genre,
                    "ai_tools_used": song.ai_tools_used,
                    "file_path": song.file_path,
                    "external_link": song.external_link,
                    "content_type": "music",
                    "upvotes": upvotes_res.scalar() or 0,
                    "downvotes": downvotes_res.scalar() or 0,
                    "created_at": song.created_at,
                    "content_source": song.content_source,
                    "creator_website": song.creator_website,
                    "creator_linktree": song.creator_linktree,
                    "creator_instagram": song.creator_instagram,
                    "creator_twitter": song.creator_twitter,
                    "creator_youtube": song.creator_youtube,
                    "creator_tiktok": song.creator_tiktok
                })
        
        # Get video content if board allows it
        if board.allow_video:
            video_query = select(Video).where(Video.board_id == board_id)
            if content_type and content_type != "video":
                video_query = video_query.where(False)
            
            video_res = await db.execute(video_query)
            video_items = video_res.scalars().all()
            
            for video in video_items:
                # Get vote counts for this video
                upvotes_res = await db.execute(
                    select(func.count(Vote.id)).where(
                        Vote.media_type == "video",
                        Vote.media_id == video.id,
                        Vote.vote_type == "like"
                    )
                )
                downvotes_res = await db.execute(
                    select(func.count(Vote.id)).where(
                        Vote.media_type == "video",
                        Vote.media_id == video.id,
                        Vote.vote_type == "dislike"
                    )
                )
                
                content_items.append({
                    "id": video.id,
                    "title": video.title,
                    "artist_name": video.artist_name,
                    "description": video.description,
                    "video_type": video.video_type,
                    "file_path": video.file_path,
                    "external_link": video.external_link,
                    "content_type": "video",
                    "upvotes": upvotes_res.scalar() or 0,
                    "downvotes": downvotes_res.scalar() or 0,
                    "created_at": video.created_at,
                    "content_source": video.content_source,
                    "creator_website": video.creator_website,
                    "creator_linktree": video.creator_linktree,
                    "creator_instagram": video.creator_instagram,
                    "creator_twitter": video.creator_twitter,
                    "creator_youtube": video.creator_youtube,
                    "creator_tiktok": video.creator_tiktok
                })
        
        # Get visual content if board allows it
        if board.allow_visuals:
            visual_query = select(Visual).where(Visual.board_id == board_id)
            if content_type and content_type != "visuals":
                visual_query = visual_query.where(False)
            
            visual_res = await db.execute(visual_query)
            visual_items = visual_res.scalars().all()
            
            for visual in visual_items:
                # Get vote counts for this visual
                upvotes_res = await db.execute(
                    select(func.count(Vote.id)).where(
                        Vote.media_type == "visuals",
                        Vote.media_id == visual.id,
                        Vote.vote_type == "like"
                    )
                )
                downvotes_res = await db.execute(
                    select(func.count(Vote.id)).where(
                        Vote.media_type == "visuals",
                        Vote.media_id == visual.id,
                        Vote.vote_type == "dislike"
                    )
                )
                
                content_items.append({
                    "id": visual.id,
                    "title": visual.title,
                    "artist_name": visual.artist_name,
                    "description": visual.description,
                    "visual_type": visual.visual_type,
                    "file_path": visual.file_path,
                    "external_link": visual.external_link,
                    "content_type": "visuals",
                    "upvotes": upvotes_res.scalar() or 0,
                    "downvotes": downvotes_res.scalar() or 0,
                    "created_at": visual.created_at,
                    "content_source": visual.content_source,
                    "creator_website": visual.creator_website,
                    "creator_linktree": visual.creator_linktree,
                    "creator_instagram": visual.creator_instagram,
                    "creator_twitter": visual.creator_twitter,
                    "creator_youtube": visual.creator_youtube,
                    "creator_tiktok": visual.creator_tiktok
                })
        
        # Sort by creation date (newest first)
        content_items.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_content = content_items[start_idx:end_idx]
        
        return {
            "content": paginated_content,
            "total": len(content_items),
            "page": page,
            "limit": limit,
            "has_more": end_idx < len(content_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching content: {str(e)}")

from pydantic import BaseModel

class VoteRequest(BaseModel):
    vote_type: str

@router.post("/{board_id}/content/{content_id}/vote")
async def vote_on_content(
    board_id: int,
    content_id: int,
    vote_data: VoteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Vote on content (like/dislike)"""
    try:
        print(f"DEBUG: Vote request received - board_id: {board_id}, content_id: {content_id}, vote_type: {vote_data.vote_type}")
        
        vote_type = vote_data.vote_type
        if vote_type not in ["like", "dislike"]:
            raise HTTPException(status_code=400, detail="Invalid vote type")
        
        # For now, use a default voter_id (in production, this would be the authenticated user)
        voter_id = 1
        
        # Check if vote already exists
        existing_vote_query = select(Vote).where(
            Vote.media_id == content_id,
            Vote.voter_id == voter_id
        )
        print(f"DEBUG: Checking for existing vote with query: {existing_vote_query}")
        
        existing_vote_res = await db.execute(existing_vote_query)
        existing_vote = existing_vote_res.scalar_one_or_none()
        print(f"DEBUG: Existing vote found: {existing_vote is not None}")
        
        if existing_vote:
            print(f"DEBUG: Found existing vote: ID={existing_vote.id}, type={existing_vote.vote_type}")
            if existing_vote.vote_type == vote_type:
                # Remove vote if clicking same button
                print(f"DEBUG: Removing existing vote")
                await db.delete(existing_vote)
                await db.commit()
                return {"message": "Vote removed", "action": "removed"}
            else:
                # Change vote type
                print(f"DEBUG: Updating existing vote from {existing_vote.vote_type} to {vote_type}")
                existing_vote.vote_type = vote_type
                await db.commit()
                return {"message": "Vote updated", "action": "updated"}
        else:
            # Create new vote - determine media type by checking which table has this content_id
            media_type = None
            
            print(f"DEBUG: Determining media type for content_id: {content_id}")
            
            # Check if it's a song
            song_res = await db.execute(select(Song).where(Song.id == content_id, Song.board_id == board_id))
            song = song_res.scalar_one_or_none()
            if song:
                media_type = "music"
                print(f"DEBUG: Found song with title: {song.title}")
            else:
                # Check if it's a video
                video_res = await db.execute(select(Video).where(Video.id == content_id, Video.board_id == board_id))
                video = video_res.scalar_one_or_none()
                if video:
                    media_type = "video"
                    print(f"DEBUG: Found video with title: {video.title}")
                else:
                    # Check if it's a visual
                    visual_res = await db.execute(select(Visual).where(Visual.id == content_id, Visual.board_id == board_id))
                    visual = visual_res.scalar_one_or_none()
                    if visual:
                        media_type = "visuals"
                        print(f"DEBUG: Found visual with title: {visual.title}")
                    else:
                        print(f"DEBUG: Content not found in any table")
                        raise HTTPException(status_code=404, detail="Content not found")
            
            print(f"DEBUG: Determined media_type: {media_type}")
            
            new_vote = Vote(
                media_type=media_type,
                media_id=content_id,
                voter_id=voter_id,
                vote_type=vote_type,
                ip_address="127.0.0.1"  # In production, get from request
            )
            print(f"DEBUG: Creating new vote: media_type={media_type}, media_id={content_id}, voter_id={voter_id}, vote_type={vote_type}")
            
            db.add(new_vote)
            await db.commit()
            print(f"DEBUG: Vote saved successfully with ID: {new_vote.id}")
            
            return {"message": "Vote added", "action": "added"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing vote: {str(e)}")

@router.get("/{board_id}/test-vote")
async def test_vote_endpoint(board_id: int, db: AsyncSession = Depends(get_db)):
    """Test endpoint to verify voting system is working"""
    try:
        # Check if board exists
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Check if there's any content to vote on
        music_count = await db.execute(select(func.count(Song.id)).where(Song.board_id == board_id))
        video_count = await db.execute(select(func.count(Video.id)).where(Video.board_id == board_id))
        visual_count = await db.execute(select(func.count(Visual.id)).where(Visual.board_id == board_id))
        
        return {
            "board_id": board_id,
            "board_title": board.title,
            "content_counts": {
                "music": music_count.scalar() or 0,
                "video": video_count.scalar() or 0,
                "visuals": visual_count.scalar() or 0
            },
            "total_content": (music_count.scalar() or 0) + (video_count.scalar() or 0) + (visual_count.scalar() or 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing vote endpoint: {str(e)}")

@router.get("/{board_id}/test-upload")
async def test_upload_endpoint(board_id: int, db: AsyncSession = Depends(get_db)):
    """Test endpoint to verify upload system is working"""
    try:
        # Check if board exists
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Check upload directories
        import os
        base_upload_dir = os.path.join(os.getcwd(), "uploads")
        board_slug = board.slug
        
        upload_dirs = {
            "music": os.path.join(base_upload_dir, "music", board_slug),
            "video": os.path.join(base_upload_dir, "video", board_slug),
            "visuals": os.path.join(base_upload_dir, "visuals", board_slug)
        }
        
        dir_status = {}
        for media_type, dir_path in upload_dirs.items():
            exists = os.path.exists(dir_path)
            writable = os.access(dir_path, os.W_OK) if exists else False
            dir_status[media_type] = {
                "exists": exists,
                "writable": writable,
                "path": dir_path,
                "board_specific": True
            }
        
        return {
            "board_id": board_id,
            "board_title": board.title,
            "board_settings": {
                "allow_music": board.allow_music,
                "allow_video": board.allow_video,
                "allow_visuals": board.allow_visuals
            },
            "upload_directories": dir_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing upload endpoint: {str(e)}")

@router.get("/upload-limits")
async def get_upload_limits():
    """Get current file upload size limits"""
    return {
        "music": {
            "max_size_mb": MAX_MUSIC_SIZE // (1024 * 1024),
            "max_size_bytes": MAX_MUSIC_SIZE,
            "formats": ["MP3", "WAV", "FLAC", "AAC"]
        },
        "video": {
            "max_size_mb": MAX_VIDEO_SIZE // (1024 * 1024),
            "max_size_bytes": MAX_VIDEO_SIZE,
            "formats": ["MP4", "MOV", "AVI", "WebM"]
        },
        "visuals": {
            "max_size_mb": MAX_VISUAL_SIZE // (1024 * 1024),
            "max_size_bytes": MAX_VISUAL_SIZE,
            "formats": ["JPG", "PNG", "GIF", "WebP"]
        }
    }

@router.get("/{board_id}/stats")
async def get_board_stats(
    board_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a Media Board"""
    try:
        # Check if board exists
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Count content by type
        music_count = 0
        video_count = 0
        visuals_count = 0
        
        if board.allow_music:
            music_res = await db.execute(select(func.count(Song.id)).where(Song.board_id == board_id))
            music_count = music_res.scalar() or 0
        
        if board.allow_video:
            video_res = await db.execute(select(func.count(Video.id)).where(Video.board_id == board_id))
            video_count = video_res.scalar() or 0
        
        if board.allow_visuals:
            visual_res = await db.execute(select(func.count(Visual.id)).where(Visual.board_id == board_id))
            visuals_count = visual_res.scalar() or 0
        
        total_content = music_count + video_count + visuals_count
        
        # Count total votes
        votes_res = await db.execute(select(func.count(Vote.id)).where(Vote.media_id.in_(
            select(Song.id).where(Song.board_id == board_id).union(
                select(Video.id).where(Video.board_id == board_id)
            ).union(
                select(Visual.id).where(Visual.board_id == board_id)
            )
        )))
        total_votes = votes_res.scalar() or 0
        
        return {
            "total_content": total_content,
            "music_count": music_count,
            "video_count": video_count,
            "visuals_count": visuals_count,
            "total_votes": total_votes,
            "community_members": 1,  # Placeholder - could be enhanced
            "trending_content": 0    # Placeholder - could be enhanced
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@router.post("/create-board")
async def create_media_board(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Create a new Media Board with the selected theme and business information"""
    try:
        # Parse JSON body
        body = await request.json()
        theme_name = body.get("theme_name", "default")
        business_name = body.get("business_name", "My Media Board")
        business_tagline = body.get("business_tagline")
        business_description = body.get("business_description", "A beautiful Media Board")
        website_url = body.get("website_url")
        industry = body.get("industry")
        contact_email = body.get("contact_email")
        social_linkedin = body.get("social_linkedin")
        social_twitter = body.get("social_twitter")
        social_instagram = body.get("social_instagram")
        social_facebook = body.get("social_facebook")
        
        # For now, use a default user_id (in production, this would be the authenticated user)
        user_id = 1

        # Generate a unique slug based on business name
        import uuid
        import re
        
        # Clean business name for slug
        clean_name = re.sub(r'[^a-zA-Z0-9\s-]', '', business_name)
        clean_name = re.sub(r'\s+', '-', clean_name).lower()
        base_slug = f"{clean_name}-{uuid.uuid4().hex[:8]}"

        # Create the board with business information
        new_board = Board(
            slug=base_slug,
            title=business_name,  # Use business name as title
            description=business_description,  # Use business description
            theme=theme_name,
            user_id=user_id,
            website_url=website_url,
            contact_email=contact_email,
            industry=industry,
            business_tagline=business_tagline,
            social_facebook=social_facebook,
            social_linkedin=social_linkedin,
            social_twitter=social_twitter,
            social_instagram=social_instagram,
            allow_music=True,
            allow_video=True,
            allow_visuals=True,
            max_music_uploads=100,
            max_video_uploads=50,
            max_visuals_uploads=100,
            require_approval=False,
            allow_anonymous_uploads=True
        )

        db.add(new_board)
        await db.commit()
        await db.refresh(new_board)

        # Store additional business info (you might want to create a separate BusinessInfo model)
        # For now, we'll store it in the board description or create a new field later

        return {
            "success": True,
            "boardId": new_board.id,
            "slug": new_board.slug,
            "message": f"Media Board '{business_name}' created successfully with {theme_name} theme!"
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"DEBUG: Board creation error: {str(e)}")
        print(f"DEBUG: Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error creating board: {str(e)}")

@router.post("/{board_id}/upload/music")
async def upload_music(
    board_id: int,
    title: str = Form(...),
    artist_name: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(None),
    external_link: str = Form(None),
    creator_website: str = Form(None),
    creator_linktree: str = Form(None),
    creator_instagram: str = Form(None),
    creator_twitter: str = Form(None),
    creator_youtube: str = Form(None),
    creator_tiktok: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload music content to a Media Board"""
    try:
        # Check if board exists and allows music
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        print(f"DEBUG: Board found - ID: {board.id}, Title: '{board.title}', Slug: '{board.slug}'")
        
        if not board.allow_music:
            raise HTTPException(status_code=400, detail="This board does not allow music uploads")
        
        # Validate that we have either a file or external link
        if not file and not external_link:
            raise HTTPException(status_code=400, detail="Please provide either a file or external link")
        
        if file and external_link:
            raise HTTPException(status_code=400, detail="Please provide either a file OR external link, not both")
        
        # For now, use a default user_id (in production, this would be the authenticated user)
        user_id = 1
        
        if file:
            # Handle file upload
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")
            
            # Validate file type
            if not file.content_type.startswith('audio/'):
                raise HTTPException(status_code=400, detail="File must be an audio file")
            
            # Validate file size
            if file.size and file.size > MAX_MUSIC_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Music file too large. Maximum size is {MAX_MUSIC_SIZE // (1024*1024)}MB. Your file is {file.size / (1024*1024):.1f}MB"
                )
            
            # Get board slug and IDs for database and directory structure
            board_slug = board.slug  # Use board slug for directory naming
            board_owner_id = board.user_id if board.user_id else 1  # For database foreign key
            uploader_id = user_id  # This will be the authenticated user in production
            
            # Create uploads directory structure: uploads/music/{board_slug}/{uploader_id}/
            from ..utils import create_upload_directory_structure, get_upload_file_path
            
            upload_dir = create_upload_directory_structure("music", board_slug, uploader_id)
            print(f"DEBUG: Upload directory: {upload_dir}")
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = get_upload_file_path("music", board_slug, uploader_id, unique_filename)
            print(f"DEBUG: File path: {file_path}")
            
            # Save the file
            try:
                print(f"DEBUG: About to save file to: {file_path}")
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                print(f"DEBUG: File saved successfully")
                
                # Calculate file size and hash
                file_size = len(content)
                file_hash = hashlib.sha256(content).hexdigest()
                print(f"DEBUG: File size: {file_size}, Hash: {file_hash[:8]}...")
                
                content_source = "upload"
                
            except Exception as e:
                print(f"DEBUG: Error saving file: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        
        else:
            # Handle external link
            file_path = None
            file_size = 0
            file_hash = ""
            content_source = "external"
            
            # Validate external link (basic validation)
            if not external_link.startswith(('http://', 'https://')):
                raise HTTPException(status_code=400, detail="Invalid external link format")
        
        # Create the music entry
        print(f"DEBUG: Creating Song with file_path: {file_path}")
        new_music = Song(
            title=title,
            artist_name=artist_name,
            description=description,
            board_id=board_id,
            artist_id=user_id,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            external_link=external_link,
            content_source=content_source,
            creator_website=creator_website,
            creator_linktree=creator_linktree,
            creator_instagram=creator_instagram,
            creator_twitter=creator_twitter,
            creator_youtube=creator_youtube,
            creator_tiktok=creator_tiktok,
            board_owner_id=board_owner_id,
            uploader_id=uploader_id,
            is_approved=True  # For now, auto-approve
        )
        
        db.add(new_music)
        await db.commit()
        await db.refresh(new_music)
        print(f"DEBUG: Song saved to database with ID: {new_music.id}")
        
        return {
            "success": True,
            "id": new_music.id,
            "message": "Music uploaded successfully!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading music: {str(e)}")

@router.post("/{board_id}/upload/video")
async def upload_video(
    board_id: int,
    title: str = Form(...),
    artist_name: str = Form(...),
    description: str = Form(None),
    video_type: str = Form("general"),  # Default to "general" if not provided
    file: UploadFile = File(None),
    external_link: str = Form(None),
    creator_website: str = Form(None),
    creator_linktree: str = Form(None),
    creator_instagram: str = Form(None),
    creator_twitter: str = Form(None),
    creator_youtube: str = Form(None),
    creator_tiktok: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload video content to a Media Board"""
    try:
        # Check if board exists and allows video
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        if not board.allow_video:
            raise HTTPException(status_code=400, detail="This board does not allow video uploads")
        
        # Validate that we have either a file or external link
        if not file and not external_link:
            raise HTTPException(status_code=400, detail="Please provide either a file or external link")
        
        if file and external_link:
            raise HTTPException(status_code=400, detail="Please provide either a file OR external link, not both")
        
        # For now, use a default user_id (in production, this would be the authenticated user)
        user_id = 1
        
        if file:
            # Handle file upload
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")
            
            # Validate file type
            if not file.content_type.startswith('video/'):
                raise HTTPException(status_code=400, detail="File must be a video file")
            
            # Validate file size
            if file.size and file.size > MAX_VIDEO_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Video file too large. Maximum size is {MAX_VIDEO_SIZE // (1024*1024)}MB. Your file is {file.size / (1024*1024):.1f}MB"
                )
            
            # Get board slug and IDs for database and directory structure
            board_slug = board.slug  # Use board slug for directory naming
            board_owner_id = board.user_id if board.user_id else 1  # For database foreign key
            uploader_id = user_id  # This will be the authenticated user in production
            
            # Create uploads directory structure: uploads/video/{board_slug}/{uploader_id}/
            from ..utils import create_upload_directory_structure, get_upload_file_path
            
            upload_dir = create_upload_directory_structure("video", board_slug, uploader_id)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = get_upload_file_path("video", board_slug, uploader_id, unique_filename)
            
            # Save the file
            try:
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Calculate file size and hash
                file_size = len(content)
                file_hash = hashlib.sha256(content).hexdigest()
                
                content_source = "upload"
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        
        else:
            # Handle external link
            file_path = None
            file_size = 0
            file_hash = ""
            content_source = "external"
            
            # Validate external link (basic validation)
            if not external_link.startswith(('http://', 'https://')):
                raise HTTPException(status_code=400, detail="Invalid external link format")
        
        # Create the video entry
        new_video = Video(
            title=title,
            artist_name=artist_name,
            description=description,
            video_type=video_type,  # Use video_type from form
            board_id=board_id,
            artist_id=user_id,
            file_path=file_path,
            external_link=external_link,
            file_size=file_size,  # Add file size
            file_hash=file_hash,  # Add file hash
            content_source=content_source,
            creator_website=creator_website,
            creator_linktree=creator_linktree,
            creator_instagram=creator_instagram,
            creator_twitter=creator_twitter,
            creator_youtube=creator_youtube,
            creator_tiktok=creator_tiktok,
            board_owner_id=board_owner_id,
            uploader_id=uploader_id,
            is_approved=True  # For now, auto-approve
        )
        
        db.add(new_video)
        await db.commit()
        await db.refresh(new_video)
        
        return {
            "success": True,
            "id": new_video.id,
            "message": "Video uploaded successfully!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

@router.post("/{board_id}/upload/visuals")
async def upload_visuals(
    board_id: int,
    title: str = Form(...),
    artist_name: str = Form(...),
    description: str = Form(None),
    visual_type: str = Form("general"),  # Default to "general" if not provided
    file: UploadFile = File(None),
    external_link: str = Form(None),
    creator_website: str = Form(None),
    creator_linktree: str = Form(None),
    creator_instagram: str = Form(None),
    creator_twitter: str = Form(None),
    creator_youtube: str = Form(None),
    creator_tiktok: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload visual content to a Media Board"""
    try:
        # Check if board exists and allows visuals
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        if not board.allow_visuals:
            raise HTTPException(status_code=400, detail="This board does not allow visual uploads")
        
        # Validate that we have either a file or external link
        if not file and not external_link:
            raise HTTPException(status_code=400, detail="Please provide either a file or external link")
        
        if file and external_link:
            raise HTTPException(status_code=400, detail="Please provide either a file OR external link, not both")
        
        # For now, use a default user_id (in production, this would be the authenticated user)
        user_id = 1
        
        if file:
            # Handle file upload
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")
            
            # Validate file type
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image file")
            
            # Validate file size
            if file.size and file.size > MAX_VISUAL_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Image file too large. Maximum size is {MAX_VISUAL_SIZE // (1024*1024)}MB. Your file is {file.size / (1024*1024):.1f}MB"
                )
            
            # Get board slug and IDs for database and directory structure
            board_slug = board.slug  # Use board slug for directory naming
            board_owner_id = board.user_id if board.user_id else 1  # For database foreign key
            uploader_id = user_id  # This will be the authenticated user in production
            
            # Create uploads directory structure: uploads/visuals/{board_slug}/{uploader_id}/
            from ..utils import create_upload_directory_structure, get_upload_file_path
            
            upload_dir = create_upload_directory_structure("visuals", board_slug, uploader_id)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = get_upload_file_path("visuals", board_slug, uploader_id, unique_filename)
            
            # Save the file
            try:
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Calculate file size and hash
                file_size = len(content)
                file_hash = hashlib.sha256(content).hexdigest()
                
                content_source = "upload"
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
            
        else:
            # Handle external link
            file_path = None
            file_size = 0
            file_hash = ""
            content_source = "external"
            
            # Validate external link (basic validation)
            if not external_link.startswith(('http://', 'https://')):
                raise HTTPException(status_code=400, detail="Invalid external link format")
        
        # Create the visual entry
        new_visual = Visual(
            title=title,
            artist_name=artist_name,
            description=description,
            visual_type=visual_type,  # Use visual_type from form
            board_id=board_id,
            artist_id=user_id,
            file_path=file_path,
            external_link=external_link,
            file_size=file_size,  # Add file size
            file_hash=file_hash,  # Add file hash
            content_source=content_source,
            creator_website=creator_website,
            creator_linktree=creator_linktree,
            creator_instagram=creator_instagram,
            creator_twitter=creator_twitter,
            creator_youtube=creator_youtube,
            creator_tiktok=creator_tiktok,
            board_owner_id=board_owner_id,
            uploader_id=uploader_id,
            is_approved=True  # For now, auto-approve
        )
        
        db.add(new_visual)
        await db.commit()
        await db.refresh(new_visual)
        
        return {
            "success": True,
            "id": new_visual.id,
            "message": "Visual uploaded successfully!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading visual: {str(e)}")

@router.get("/{board_id}/vote-stats")
async def get_board_vote_stats(
    board_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get voting statistics for a specific Media Board"""
    try:
        # First check if board exists
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Get total vote counts by joining through content tables
        # Get upvotes for music
        music_upvotes_res = await db.execute(
            select(func.count(Vote.id)).join(Song, Vote.media_id == Song.id).where(
                Vote.media_type == "music",
                Vote.vote_type == "like",
                Song.board_id == board_id
            )
        )
        music_upvotes = music_upvotes_res.scalar() or 0
        
        # Get upvotes for videos
        video_upvotes_res = await db.execute(
            select(func.count(Vote.id)).join(Video, Vote.media_id == Video.id).where(
                Vote.media_type == "video",
                Vote.vote_type == "like",
                Video.board_id == board_id
            )
        )
        video_upvotes = video_upvotes_res.scalar() or 0
        
        # Get upvotes for visuals
        visual_upvotes_res = await db.execute(
            select(func.count(Vote.id)).join(Visual, Vote.media_id == Visual.id).where(
                Vote.media_type == "visuals",
                Vote.vote_type == "like",
                Visual.board_id == board_id
            )
        )
        visual_upvotes = visual_upvotes_res.scalar() or 0
        
        total_upvotes = music_upvotes + video_upvotes + visual_upvotes
        
        # Get downvotes for music
        music_downvotes_res = await db.execute(
            select(func.count(Vote.id)).join(Song, Vote.media_id == Song.id).where(
                Vote.media_type == "music",
                Vote.vote_type == "dislike",
                Song.board_id == board_id
            )
        )
        music_downvotes = music_downvotes_res.scalar() or 0
        
        # Get downvotes for videos
        video_downvotes_res = await db.execute(
            select(func.count(Vote.id)).join(Video, Vote.media_id == Video.id).where(
                Vote.media_type == "video",
                Vote.vote_type == "dislike",
                Video.board_id == board_id
            )
        )
        video_downvotes = video_downvotes_res.scalar() or 0
        
        # Get downvotes for visuals
        visual_downvotes_res = await db.execute(
            select(func.count(Vote.id)).join(Visual, Vote.media_id == Visual.id).where(
                Vote.media_type == "visuals",
                Vote.vote_type == "dislike",
                Visual.board_id == board_id
            )
        )
        visual_downvotes = visual_downvotes_res.scalar() or 0
        
        total_downvotes = music_downvotes + video_downvotes + visual_downvotes
        
        total_votes = total_upvotes + total_downvotes
        
        # Get top performing content (by upvotes)
        top_content = []
        
        # Get top music
        if board.allow_music:
            music_query = select(Song, func.count(Vote.id).label('upvotes')).join(
                Vote, (Vote.media_type == "music") & (Vote.media_id == Song.id) & (Vote.vote_type == "like")
            ).where(Song.board_id == board_id).group_by(Song.id).order_by(func.count(Vote.id).desc()).limit(5)
            music_res = await db.execute(music_query)
            music_items = music_res.all()
            for song, upvotes in music_items:
                top_content.append({
                    "id": song.id,
                    "title": song.title,
                    "artist_name": song.artist_name,
                    "content_type": "music",
                    "upvotes": upvotes
                })
        
        # Get top videos
        if board.allow_video:
            video_query = select(Video, func.count(Vote.id).label('upvotes')).join(
                Vote, (Vote.media_type == "video") & (Vote.media_id == Video.id) & (Vote.vote_type == "like")
            ).where(Video.board_id == board_id).group_by(Video.id).order_by(func.count(Vote.id).desc()).limit(5)
            video_res = await db.execute(video_query)
            video_items = video_res.all()
            for video, upvotes in video_items:
                top_content.append({
                    "id": video.id,
                    "title": video.title,
                    "artist_name": video.artist_name,
                    "content_type": "video",
                    "upvotes": upvotes
                })
        
        # Get top visuals
        if board.allow_visuals:
            visual_query = select(Visual, func.count(Vote.id).label('upvotes')).join(
                Vote, (Vote.media_type == "visuals") & (Vote.media_id == Visual.id) & (Vote.vote_type == "like")
            ).where(Visual.board_id == board_id).group_by(Visual.id).order_by(func.count(Vote.id).desc()).limit(5)
            visual_res = await db.execute(visual_query)
            visual_items = visual_res.all()
            for visual, upvotes in visual_items:
                top_content.append({
                    "id": visual.id,
                    "title": visual.title,
                    "artist_name": visual.artist_name,
                    "content_type": "visuals",
                    "upvotes": upvotes
                })
        
        # Sort all content by upvotes and take top 5
        top_content.sort(key=lambda x: x['upvotes'], reverse=True)
        top_content = top_content[:5]
        
        return {
            "total_upvotes": total_upvotes,
            "total_downvotes": total_downvotes,
            "total_votes": total_votes,
            "top_content": top_content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting vote stats: {str(e)}")

@router.get("/{board_id}/debug-votes")
async def debug_votes(board_id: int, db: AsyncSession = Depends(get_db)):
    """Debug endpoint to check all votes for a board"""
    try:
        # Get all votes for this board
        votes_query = select(Vote).join(
            Song, (Vote.media_type == "music") & (Vote.media_id == Song.id)
        ).where(Song.board_id == board_id)
        
        votes_res = await db.execute(votes_query)
        music_votes = votes_res.scalars().all()
        
        # Get video votes
        video_votes_query = select(Vote).join(
            Video, (Vote.media_type == "video") & (Vote.media_id == Video.id)
        ).where(Video.board_id == board_id)
        
        video_votes_res = await db.execute(video_votes_query)
        video_votes = video_votes_res.scalars().all()
        
        # Get visual votes
        visual_votes_query = select(Vote).join(
            Visual, (Vote.media_type == "visuals") & (Vote.media_id == Visual.id)
        ).where(Visual.board_id == board_id)
        
        visual_votes_res = await db.execute(visual_votes_query)
        visual_votes = visual_votes_res.scalars().all()
        
        return {
            "board_id": board_id,
            "music_votes": [{"id": v.id, "media_id": v.media_id, "vote_type": v.vote_type, "voter_id": v.voter_id} for v in music_votes],
            "video_votes": [{"id": v.id, "media_id": v.media_id, "vote_type": v.vote_type, "voter_id": v.voter_id} for v in video_votes],
            "visual_votes": [{"id": v.id, "media_id": v.media_id, "vote_type": v.vote_type, "voter_id": v.voter_id} for v in visual_votes],
            "total_votes": len(music_votes) + len(video_votes) + len(visual_votes)
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/{board_id}/upload-structure")
async def get_upload_structure(board_id: int, db: AsyncSession = Depends(get_db)):
    """Get the current upload directory structure for a board"""
    try:
        # Check if board exists
        board_res = await db.execute(select(Board).where(Board.id == board_id))
        board = board_res.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        import os
        base_upload_dir = os.path.join(os.getcwd(), "uploads")
        board_slug = board.slug
        
        structure = {
            "board_id": board_id,
            "board_name": board.title,
            "board_slug": board_slug,
            "base_path": base_upload_dir,
            "directories": {}
        }
        
        # Check each media type directory
        for media_type in ["music", "video", "visuals"]:
            media_dir = os.path.join(base_upload_dir, media_type, board_slug)
            exists = os.path.exists(media_dir)
            
            if exists:
                # List files in the directory
                try:
                    files = os.listdir(media_dir)
                    file_info = []
                    total_size = 0
                    
                    for filename in files:
                        file_path = os.path.join(media_dir, filename)
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            file_info.append({
                                "filename": filename,
                                "size_bytes": file_size,
                                "size_mb": round(file_size / (1024 * 1024), 2)
                            })
                    
                    structure["directories"][media_type] = {
                        "exists": True,
                        "path": media_dir,
                        "file_count": len(file_info),
                        "total_size_mb": round(total_size / (1024 * 1024), 2),
                        "files": file_info
                    }
                except Exception as e:
                    structure["directories"][media_type] = {
                        "exists": True,
                        "path": media_dir,
                        "error": str(e)
                    }
            else:
                structure["directories"][media_type] = {
                    "exists": False,
                    "path": media_dir
                }
        
        return structure
        
    except Exception as e:
        return {"error": str(e)}
