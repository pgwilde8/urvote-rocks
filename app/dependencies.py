from fastapi import Depends, HTTPException, status
from app.models import User
from app.auth import get_current_user
from datetime import datetime

async def get_current_board_owner(current_user: User = Depends(get_current_user)):
    if not current_user.membership_expires_at or current_user.membership_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must have an active board owner membership."
        )
    return current_user