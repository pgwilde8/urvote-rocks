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

@router.post("/{board_id}/content/{content_id}/vote")
async def vote_on_content(
    board_id: int,
    content_id: int,
    vote_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Vote on content (like/dislike)"""
    try:
        vote_type = vote_data.get("vote_type")
        if vote_type not in ["like", "dislike"]:
            raise HTTPException(status_code=400, detail="Invalid vote type")
        
        # For now, use a default voter_id (in production, this would be the authenticated user)
        voter_id = 1
        
        # Check if vote already exists
        existing_vote = await db.execute(
            select(Vote).where(
                Vote.media_id == content_id,
                Vote.voter_id == voter_id
            )
        )
        existing_vote = existing_vote.scalar_one_or_none()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote if clicking same button
                await db.delete(existing_vote)
                await db.commit()
                return {"message": "Vote removed", "action": "removed"}
            else:
                # Change vote type
                existing_vote.vote_type = vote_type
                await db.commit()
                return {"message": "Vote updated", "action": "updated"}
        else:
            # Create new vote
            # Determine media type from content_id (this is simplified - in production you'd query the content)
            media_type = "music"  # Default, could be enhanced
            
            new_vote = Vote(
                media_type=media_type,
                media_id=content_id,
                voter_id=voter_id,
                vote_type=vote_type,
                ip_address="127.0.0.1"  # In production, get from request
            )
            db.add(new_vote)
            await db.commit()
            return {"message": "Vote added", "action": "added"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing vote: {str(e)}")

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
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), "uploads", "music")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = f"uploads/music/{unique_filename}"  # Store relative path for database
            
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
        
        # Create the music entry
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
            is_approved=True  # For now, auto-approve
        )
        
        db.add(new_music)
        await db.commit()
        await db.refresh(new_music)
        
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
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), "uploads", "video")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = f"uploads/video/{unique_filename}"  # Store relative path for database
            
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
            board_id=board_id,
            artist_id=user_id,
            file_path=file_path,
            external_link=external_link,
            content_source=content_source,
            creator_website=creator_website,
            creator_linktree=creator_linktree,
            creator_instagram=creator_instagram,
            creator_twitter=creator_twitter,
            creator_youtube=creator_youtube,
            creator_tiktok=creator_tiktok,
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
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), "uploads", "visuals")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = f"uploads/visuals/{unique_filename}"
            
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
            board_id=board_id,
            artist_id=user_id,
            file_path=file_path,
            external_link=external_link,
            content_source=content_source,
            creator_website=creator_website,
            creator_linktree=creator_linktree,
            creator_instagram=creator_instagram,
            creator_twitter=creator_twitter,
            creator_youtube=creator_youtube,
            creator_tiktok=creator_tiktok,
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
