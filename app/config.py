from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://urvote_user:Securepass1@localhost/urvote"
    
    # Security
    secret_key: str = "hfdfsf78gj558"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Upload - Multi-Client Structure
    upload_dir: str = "/opt/urvote/uploads"
    clients_dir: str = "/opt/urvote/uploads/clients"
    contests_dir: str = "/opt/urvote/uploads/contests"
    processed_dir: str = "/opt/urvote/uploads/processed"
    temp_dir: str = "/opt/urvote/uploads/temp"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # Client Configuration
    default_client: str = "payportpro"
    default_contest: str = "patriotic-2024"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # External Services
    recaptcha_secret: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # App Settings
    app_name: str = "UrVote.Rocks"
    debug: bool = False
    
    # GeoIP Service
    geoip_api_key: Optional[str] = None
    
    @property
    def allowed_extensions(self) -> set:
        """Get allowed file extensions"""
        return {".mp3", ".wav", ".flac", ".m4a"}
    
    class Config:
        env_file = ".env"

settings = Settings()