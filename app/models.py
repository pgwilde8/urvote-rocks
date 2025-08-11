from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    
    # Relationships
    songs = relationship("Song", back_populates="artist")
    votes = relationship("Vote", back_populates="voter")

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    artist_name = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=True)
    ai_tools_used = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    license_type = Column(String(50), default="stream_only")  # stream_only, cc_by_nc
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA256
    external_link = Column(String(500), nullable=True)  # YouTube/SoundCloud
    
    # Status
    is_approved = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    
    # Metadata
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    artist = relationship("User", back_populates="songs")
    votes = relationship("Vote", back_populates="song")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    recaptcha_score = Column(String(10), nullable=True)
    
    # GeoIP data
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    song = relationship("Song", back_populates="votes")
    voter = relationship("User", back_populates="votes")

class Contest(Base):
    __tablename__ = "contests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    max_entries_per_user = Column(Integer, default=1)
    voting_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
