import hashlib
import os
import re
from pathlib import Path
from typing import Optional, Tuple
import aiofiles
import httpx
from ..config import settings
import time

def validate_file_type(filename: str) -> bool:
    """Validate if file type is allowed"""
    if not filename:
        return False
    ext = Path(filename).suffix.lower()
    return ext in settings.allowed_extensions

def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits"""
    return file_size <= settings.max_file_size

def generate_file_hash(file_data: bytes) -> str:
    """Generate SHA256 hash of file data"""
    return hashlib.sha256(file_data).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return safe_filename[:100]  # Limit length

async def save_uploaded_file(file_data: bytes, original_filename: str, artist_name: str) -> Tuple[str, str]:
    """Save uploaded file and return file path and hash"""
    # Generate safe filename
    timestamp = int(time.time())
    safe_artist = re.sub(r'[^\w\-_]', '_', artist_name).strip('_')
    file_hash = generate_file_hash(file_data)
    ext = Path(original_filename).suffix.lower()
    
    safe_filename = f"{timestamp}__{safe_artist}__{file_hash[:10]}{ext}"
    file_path = Path(settings.upload_dir) / safe_filename
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_data)
    
    return str(file_path), file_hash

def is_disposable_email(email: str) -> bool:
    """Check if email is from a disposable email service"""
    disposable_domains = {
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'trashmail.com'
    }
    
    domain = email.split('@')[-1].lower()
    return domain in disposable_domains

async def verify_recaptcha(token: str, remote_ip: str) -> float:
    """Verify reCAPTCHA token and return score"""
    if not settings.recaptcha_secret:
        return 0.5  # Default score if reCAPTCHA not configured
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.recaptcha_secret,
                    'response': token,
                    'remoteip': remote_ip
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('score', 0.0)
    except Exception:
        pass
    
    return 0.0

def is_suspicious_vote(ip_address: str, user_agent: str, recaptcha_score: float) -> bool:
    """Check if a vote appears suspicious"""
    # Low reCAPTCHA score
    if recaptcha_score < 0.3:
        return True
    
    # Missing or suspicious user agent
    if not user_agent or len(user_agent) < 20:
        return True
    
    # Add more fraud detection logic here
    return False

async def send_verification_email(email: str, token: str) -> bool:
    """Send verification email to user"""
    if not all([settings.smtp_server, settings.smtp_username, settings.smtp_password]):
        # Log that email sending is not configured
        print(f"Email not configured - verification token for {email}: {token}")
        return False
    
    # TODO: Implement actual email sending
    # For now, just log the token
    print(f"Verification email would be sent to {email} with token: {token}")
    return True

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def create_upload_directory_structure(content_type: str, board_slug: str, uploader_id: int) -> str:
    """
    Create directory structure for uploads: uploads/{content_type}/{board_slug}/{uploader_id}/
    
    Args:
        content_type: Type of content (music, video, visuals)
        board_slug: Slug of the board (e.g., "businessorganization-nam-aee51a0f")
        uploader_id: ID of the content uploader
    
    Returns:
        Relative path to the upload directory
    """
    base_uploads_dir = os.path.join(os.getcwd(), "uploads")
    content_dir = os.path.join(base_uploads_dir, content_type)
    board_dir = os.path.join(content_dir, board_slug)
    uploader_dir = os.path.join(board_dir, str(uploader_id))
    
    # Create the directory structure
    os.makedirs(uploader_dir, exist_ok=True)
    
    # Return relative path for database storage
    return f"uploads/{content_type}/{board_slug}/{uploader_id}"

def get_upload_file_path(content_type: str, board_slug: str, uploader_id: int, filename: str) -> str:
    """
    Get the full file path for an upload using the new directory structure
    
    Args:
        content_type: Type of content (music, video, visuals)
        board_slug: Slug of the board (e.g., "businessorganization-nam-aee51a0f")
        uploader_id: ID of the content uploader
        filename: The filename to store
    
    Returns:
        Relative path to the file for database storage
    """
    return f"uploads/{content_type}/{board_slug}/{uploader_id}/{filename}"
