from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    email_verified: bool
    
    class Config:
        from_attributes = True

# Song schemas
class SongBase(BaseModel):
    title: str
    artist_name: str
    genre: Optional[str] = None
    ai_tools_used: Optional[str] = None
    description: Optional[str] = None
    license_type: str = "stream_only"
    external_link: Optional[str] = None

class SongCreate(SongBase):
    pass

class SongResponse(SongBase):
    id: int
    file_path: str
    file_size: int
    file_hash: str
    is_approved: bool
    is_rejected: bool
    rejection_reason: Optional[str]
    created_at: datetime
    approved_at: Optional[datetime]
    vote_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class SongApproval(BaseModel):
    is_approved: bool
    rejection_reason: Optional[str] = None

# Vote schemas
class VoteCreate(BaseModel):
    song_id: int
    recaptcha_token: Optional[str] = None

class VoteResponse(BaseModel):
    id: int
    song_id: int
    voter_id: int
    ip_address: str
    country_code: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Contest schemas
class ContestBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    max_entries_per_user: int = 1

class ContestCreate(ContestBase):
    pass

class ContestResponse(ContestBase):
    id: int
    is_active: bool
    voting_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Leaderboard schemas
class LeaderboardEntry(BaseModel):
    song_id: int
    title: str
    artist_name: str
    vote_count: int
    rank: int

class LeaderboardResponse(BaseModel):
    contest_id: int
    contest_name: str
    entries: List[LeaderboardEntry]
    total_votes: int
    last_updated: datetime

# Upload response
class UploadResponse(BaseModel):
    ok: bool
    message: str
    song_id: Optional[int] = None
    file_path: Optional[str] = None
