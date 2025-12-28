from pydantic_settings import BaseSettings
from pydantic import field_validator
import os

class Settings(BaseSettings):
    # Default to SQLite for local no-docker setup
    DATABASE_URL: str = "sqlite:///./banking_dashboard.db"
    
    TRUELAYER_CLIENT_ID: str
    TRUELAYER_CLIENT_SECRET: str
    TRUELAYER_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    TRUELAYER_AUTH_URL: str = "https://auth.truelayer-sandbox.com"
    TRUELAYER_API_URL: str = "https://api.truelayer-sandbox.com"
    
    # Default to Sandbox Mock, but allow override for Live
    TRUELAYER_PROVIDERS: str = "uk-cs-mock" 
    ENCRYPTION_KEY: str
    JWT_SECRET: str | None = None
    FRONTEND_URL: str = "http://localhost:3000"

    @field_validator("TRUELAYER_CLIENT_ID", "TRUELAYER_CLIENT_SECRET", "TRUELAYER_REDIRECT_URI", "TRUELAYER_AUTH_URL", "TRUELAYER_API_URL", "ENCRYPTION_KEY", "JWT_SECRET", "FRONTEND_URL")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    class Config:
        # Look for .env in current dir or parent dir
        env_file = ".env"
        extra = "ignore" 

settings = Settings()
