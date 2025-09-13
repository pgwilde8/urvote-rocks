#!/usr/bin/env python3
"""
Utility functions for UrVote.Rocks
"""

import os
from pathlib import Path


def create_upload_directory_structure(content_type: str, board_slug: str, uploader_id: int) -> str:
    """
    Create the directory structure for file uploads.
    
    Args:
        content_type: Type of content (music, video, visual)
        board_slug: Slug of the board
        uploader_id: ID of the user uploading
        
    Returns:
        str: Path to the created directory
    """
    # Base upload directory
    base_dir = Path("/opt/urvote/uploads")
    
    # Create the directory path: uploads/{content_type}/{board_slug}/{uploader_id}/
    upload_dir = base_dir / content_type / board_slug / str(uploader_id)
    
    # Create the directory if it doesn't exist
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    return str(upload_dir)


def get_upload_file_path(content_type: str, board_slug: str, uploader_id: int, filename: str) -> str:
    """
    Get the full file path for an uploaded file.
    
    Args:
        content_type: Type of content (music, video, visual)
        board_slug: Slug of the board
        uploader_id: ID of the user uploading
        filename: Name of the file
        
    Returns:
        str: Full path to the file
    """
    # Base upload directory
    base_dir = Path("/opt/urvote/uploads")
    
    # Create the file path: uploads/{content_type}/{board_slug}/{uploader_id}/{filename}
    file_path = base_dir / content_type / board_slug / str(uploader_id) / filename
    
    return str(file_path)


def ensure_upload_directory_exists() -> None:
    """
    Ensure the base upload directory exists.
    """
    base_dir = Path("/opt/urvote/uploads")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each content type
    for content_type in ["music", "video", "visual"]:
        (base_dir / content_type).mkdir(parents=True, exist_ok=True)
