"""
Application configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ConfigDict
from typing import List, Optional, Union, Any, Dict
from functools import lru_cache
from pathlib import Path
import json
import os

# Load .env file explicitly
from dotenv import load_dotenv
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file, override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Anthropic API Configuration
    anthropic_api_key: str

    # OpenAI API Configuration (optional)
    openai_api_key: Optional[str] = None

    # HuggingFace Token (required for Pyannote speaker diarization)
    hf_token: Optional[str] = None

    # Perplexity API Configuration (for Cross-Pollination Agent)
    perplexity_api_key: Optional[str] = None

    # Fetch.ai Configuration
    fetchai_api_key: Optional[str] = None
    fetchai_agent_address: Optional[str] = None

    # Storage Settings
    max_upload_size_mb: int = 100
    allowed_audio_formats: List[str] = ["mp3", "wav", "m4a", "ogg"]
    local_storage_path: str = "./uploads"

    # Database Configuration (Supabase PostgreSQL)
    # Format: postgresql+asyncpg://user:password@host:port/database
    # For Supabase: postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres
    # Get from: Project Settings → Database → Connection string (Psycopg)
    database_url: str = "sqlite+aiosqlite:///./networkai.db"  # Fallback for local development

    # Supabase Configuration (PostgreSQL)
    supabase_url: Optional[str] = None  # e.g., https://xxxxx.supabase.co
    supabase_key: Optional[str] = None  # Anon public key
    supabase_db_password: Optional[str] = None  # Database password for direct connection

    # Cloud SQL Configuration (optional - for GCP Cloud SQL)
    gcp_project_id: Optional[str] = None
    gcp_region: Optional[str] = "us-central1"
    cloud_sql_instance_connection_name: Optional[str] = None  # project:region:instance
    cloud_sql_database_name: Optional[str] = "aperta_db"
    cloud_sql_user: Optional[str] = "postgres"
    cloud_sql_password: Optional[str] = None

    # ChromaDB Configuration
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "networkai_documents"

    # GCS Configuration (for audio, transcripts, and ChromaDB persistence)
    gcp_bucket_name: Optional[str] = None
    gcp_service_account_json: Optional[str] = None  # Path to service account JSON file
    use_gcs_for_chroma: bool = False  # Whether to backup ChromaDB to GCS

    # Application Configuration
    app_name: str = "NetworkAI"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"

    # CORS Configuration
    cors_origins: Optional[str] = "http://localhost:5173,http://localhost:3000"
    cors_credentials: bool = True
    cors_methods: Optional[str] = "*"
    cors_headers: Optional[str] = "*"

    # WebSocket Configuration
    ws_heartbeat_interval: int = 30
    ws_max_connections: int = 100

    # Agent Configuration
    default_agent_model: str = "claude-opus-4-6"
    max_agent_turns: int = 10
    agent_timeout: int = 300

    # Privacy Configuration
    enable_pii_detection: bool = True
    enable_auto_redaction: bool = True
    encryption_enabled: bool = True

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="null"
    )

    def __init__(self, **data):
        """Initialize settings and build database URL from Supabase if provided."""
        super().__init__(**data)

        # Convert string CORS values to lists
        if isinstance(self.cors_origins, str):
            self.cors_origins = [item.strip() for item in self.cors_origins.split(',') if item.strip()]
        if isinstance(self.cors_methods, str):
            self.cors_methods = [item.strip() for item in self.cors_methods.split(',') if item.strip()]
        if isinstance(self.cors_headers, str):
            self.cors_headers = [item.strip() for item in self.cors_headers.split(',') if item.strip()]

        # Auto-build database URL from Supabase credentials if provided
        if self.supabase_db_password and self.supabase_url:
            # Extract host from Supabase URL (e.g., xxxxx.supabase.co)
            supabase_host = self.supabase_url.replace("https://", "").replace("http://", "")

            # Build PostgreSQL async connection string
            self.database_url = (
                f"postgresql+asyncpg://postgres:{self.supabase_db_password}"
                f"@db.{supabase_host}:5432/postgres"
            )



@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings
    """
    return Settings()


# Convenience function for getting settings
settings = get_settings()
