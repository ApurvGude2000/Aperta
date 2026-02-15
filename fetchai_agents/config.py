# ABOUTME: Configuration management for Fetch.ai agent deployment.
# ABOUTME: Loads environment variables and provides typed config access.

from pydantic_settings import BaseSettings
from typing import Optional


class FetchAIConfig(BaseSettings):
    """Configuration for Fetch.ai Agentverse deployment."""

    # Fetch.ai credentials
    fetchai_api_key: str = ""
    agent_seed: str = ""

    # Backend API
    backend_api_url: str = "http://localhost:8000"

    # Pricing (in FET tokens)
    price_context_understanding: float = 0.10
    price_privacy_redaction: float = 0.05
    price_followup_generation: float = 0.08
    price_crosspollination: float = 0.15
    price_qa_routing: float = 0.03
    price_retrieval: float = 0.05
    price_insight: float = 0.12
    price_response_compose: float = 0.05

    # Agent configuration
    enable_payment_verification: bool = False
    agent_port_start: int = 8001

    class Config:
        env_file = ".env"
        extra = "ignore"


# Global config instance
config = FetchAIConfig()
