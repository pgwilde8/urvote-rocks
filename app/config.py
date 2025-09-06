from pydantic_settings import BaseSettings
from typing import Optional
import os
os.environ.clear()  # Clear any cached environment variables

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

    # DigitalOcean Spaces Configuration
    spaces_endpoint: str = "https://sfo3.digitaloceanspaces.com"
    spaces_bucket: str = "urvote.rocks"
    spaces_access_key: str = "DO00DLYYGZ83P833NDQB"
    spaces_secret_key: str = "KTWro6oES5YqxAvI2Oq52MlqxkuVjz8NJlL9WdEncT0"
    spaces_region: str = "sfo3"
    
    # Stripe Configuration (Optional - can be disabled for free launch)
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_price_id: Optional[str] = None
    stripe_prod_id: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Free Launch Mode
    free_boards_enabled: bool = True  # Set to False when ready to charge
    
    # Brevo Email Configuration
    brevo_api: Optional[str] = None
    brevo_api_key: Optional[str] = None
    
    # Google OAuth Configuration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    @property
    def allowed_extensions(self) -> set:
        """Get allowed file extensions"""
        return {".mp3", ".wav", ".flac", ".m4a"}
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file

settings = Settings()