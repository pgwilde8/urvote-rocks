from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy import DateTime
  

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
    
    # New fields for dual-purpose accounts
    artist_name = Column(String(255), nullable=True)  # For contestants
    bio = Column(Text, nullable=True)  # Artist bio
    website = Column(String(500), nullable=True)  # Artist website
    social_links = Column(JSON, nullable=True)  # Social media links
    profile_image = Column(String(500), nullable=True)  # Profile picture
    is_contestant = Column(Boolean, default=False)  # Can submit songs
    is_voter = Column(Boolean, default=True)  # Can vote (default for all)
    
    # Google OAuth fields
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    name = Column(String(255), nullable=True)  # Full name from Google
    user_type = Column(String(50), default="voter")  # voter, creator, board_owner
    membership_expires_at = Column(DateTime, nullable=True)
    
    # Additional fields for better artist profiles
    location = Column(String(255), nullable=True)  # Artist location
    genre = Column(String(100), nullable=True)  # Primary music genre
    years_active = Column(String(50), nullable=True)  # How long making music
    
    # Relationships
    votes = relationship("Vote", back_populates="voter")
    # Note: songs relationship removed to avoid SQLAlchemy conflicts

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    tagline = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    about = Column(Text, nullable=True)
    company_info = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    theme = Column(JSON, nullable=True)  # Store theme colors as JSON
    website_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    contests = relationship("Contest", back_populates="client")

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
    url = Column(String(500), nullable=True)
    linktree = Column(String(500), nullable=True)
    social_link = Column(String(500), nullable=True)
    
    # Creator information for backlinks
    creator_website = Column(String(500), nullable=True)
    creator_linktree = Column(String(500), nullable=True)
    creator_instagram = Column(String(500), nullable=True)
    creator_twitter = Column(String(500), nullable=True)
    creator_youtube = Column(String(500), nullable=True)
    creator_tiktok = Column(String(500), nullable=True)
    
    # Status
    is_approved = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    
    # Metadata
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=True)  # Changed from False to True
    audio_url = Column(String(500), nullable=True)  # Web-accessible URL for audio files
    content_source = Column(String(50), default="upload")  # upload or external
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # New fields for directory structure
    board_owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)  # Who owns the board
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who uploaded the content
    
    # Relationships
    contest = relationship("Contest")
    votes = relationship("Vote", back_populates="song")
    board_id = Column(BigInteger, ForeignKey("boards.id", ondelete="CASCADE"), nullable=True, index=True)
    board = relationship("Board", back_populates="songs")
    # Note: artist, board_owner and uploader relationships removed to avoid SQLAlchemy conflicts
    # These can be accessed via direct queries if needed
    
class Board(Base):
    __tablename__ = "boards"
    id = Column(BigInteger, primary_key=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    theme = Column(String(100), nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    # Business information
    website_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    business_tagline = Column(String(255), nullable=True)
    
    # Social media links
    social_facebook = Column(String(500), nullable=True)
    social_linkedin = Column(String(500), nullable=True)
    social_twitter = Column(String(500), nullable=True)
    social_instagram = Column(String(500), nullable=True)
    
    # Media type preferences
    allow_music = Column(Boolean, default=True)
    allow_video = Column(Boolean, default=True)
    allow_visuals = Column(Boolean, default=True)
    max_music_uploads = Column(Integer, default=100)
    max_video_uploads = Column(Integer, default=50)
    max_visuals_uploads = Column(Integer, default=100)
    require_approval = Column(Boolean, default=False)
    allow_anonymous_uploads = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    songs = relationship("Song", back_populates="board", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="board", cascade="all, delete-orphan")
    visuals = relationship("Visual", back_populates="board", cascade="all, delete-orphan")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    artist_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    video_type = Column(String(100), nullable=True)  # music_video, visualizer, etc.
    file_path = Column(String(500), nullable=True)  # For uploaded files
    external_link = Column(String(500), nullable=True)  # YouTube/Vimeo links
    file_size = Column(BigInteger, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    # Creator information for backlinks
    creator_website = Column(String(500), nullable=True)
    creator_linktree = Column(String(500), nullable=True)
    creator_instagram = Column(String(500), nullable=True)
    creator_twitter = Column(String(500), nullable=True)
    creator_youtube = Column(String(500), nullable=True)
    creator_tiktok = Column(String(500), nullable=True)
    
    # Status
    is_approved = Column(Boolean, default=True)
    is_rejected = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    
    # Metadata
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    board_id = Column(BigInteger, ForeignKey("boards.id", ondelete="CASCADE"), nullable=True, index=True)
    content_source = Column(String(50), default="upload")  # upload or external
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # New fields for directory structure
    board_owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)  # Who owns the board
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who uploaded the content
    
    # Relationships
    board = relationship("Board", back_populates="videos")
    # Note: board_owner and uploader relationships removed to avoid SQLAlchemy conflicts

class Visual(Base):
    __tablename__ = "visuals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    artist_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    visual_type = Column(String(100), nullable=True)  # artwork, photo, graphic, etc.
    file_path = Column(String(500), nullable=True)  # For uploaded files
    external_link = Column(String(500), nullable=True)  # Unsplash/Pexels links
    file_size = Column(BigInteger, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    # Creator information for backlinks
    creator_website = Column(String(500), nullable=True)
    creator_linktree = Column(String(500), nullable=True)
    creator_instagram = Column(String(500), nullable=True)
    creator_twitter = Column(String(500), nullable=True)
    creator_youtube = Column(String(500), nullable=True)
    creator_tiktok = Column(String(500), nullable=True)
    
    # Status
    is_approved = Column(Boolean, default=True)
    is_rejected = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    
    # Metadata
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    board_id = Column(BigInteger, ForeignKey("boards.id", ondelete="CASCADE"), nullable=True, index=True)
    content_source = Column(String(50), default="upload")  # upload or external
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # New fields for directory structure
    board_owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)  # Who owns the board
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who uploaded the content
    
    # Relationships
    board = relationship("Board", back_populates="visuals")
    # Note: board_owner and uploader relationships removed to avoid SQLAlchemy conflicts

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=True)  # Made nullable for generic voting
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Made optional for anonymous voting
    voter_type = Column(String(20), default="anonymous")  # "authenticated" or "anonymous"
    
    # Anonymous voting fields
    voter_email = Column(String(255), nullable=True, index=True)  # For anonymous voters
    voter_name = Column(String(255), nullable=True)  # Optional name for anonymous voters
    
    # Generic voting fields for all media types
    media_type = Column(String(20), nullable=True)  # "music", "video", "visuals"
    media_id = Column(BigInteger, nullable=True)  # ID of the content being voted on
    vote_type = Column(String(20), default="like")  # "like" or "dislike"
    
    # Fraud prevention
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    recaptcha_score = Column(String(10), nullable=True)
    
    # Rate limiting
    votes_per_email_per_day = Column(Integer, default=1)  # Track daily votes per email
    
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
    
    # Client relationship
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="contests")