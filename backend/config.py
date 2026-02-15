"""
Application configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional, Union
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Anthropic API Configuration
    anthropic_api_key: str

    # OpenAI API Configuration (optional)
    openai_api_key: Optional[str] = None

    # Fetch.ai Configuration
    fetchai_api_key: Optional[str] = None
    fetchai_agent_address: Optional[str] = None

    # AWS S3 / Cloud Storage Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: str = "networkai-transcripts"
    s3_region: str = "us-east-1"
    s3_endpoint_url: Optional[str] = None  # For S3-compatible services (Supabase, R2)

    # Storage Settings
    max_upload_size_mb: int = 100
    allowed_audio_formats: List[str] = ["mp3", "wav", "m4a", "ogg"]

    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./networkai.db"

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

    # GCS Configuration (for ChromaDB persistence)
    gcp_bucket_name: Optional[str] = None
    gcp_service_account_json: Optional[str] = None  # Path to service account JSON file
    use_gcs_for_chroma: bool = False

    # Application Configuration
    app_name: str = "NetworkAI"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

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

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v

    @field_validator('cors_methods', mode='before')
    @classmethod
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v

    @field_validator('cors_headers', mode='before')
    @classmethod
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v


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
