"""
Google Cloud OAuth2 authentication for Aperta.
Supports local development and production environments.
"""

import os
import logging
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)


class GoogleOAuthConfig:
    """Google OAuth configuration."""

    def __init__(self):
        # Get from environment or .env file
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback/google")

        # Validate required config
        if not self.client_id:
            logger.warning("GOOGLE_CLIENT_ID not set - Google OAuth will not work")
        if not self.client_secret:
            logger.warning("GOOGLE_CLIENT_SECRET not set - Google OAuth will not work")

    def is_configured(self) -> bool:
        """Check if Google OAuth is properly configured."""
        return bool(self.client_id and self.client_secret)


class GoogleTokenPayload(BaseModel):
    """Google token payload after verification."""
    sub: str  # User ID
    email: EmailStr
    email_verified: bool
    name: str
    picture: Optional[str] = None
    aud: str  # Audience (should match client_id)


class GoogleOAuthProvider:
    """Google OAuth provider for authentication."""

    def __init__(self, config: GoogleOAuthConfig):
        self.config = config
        self.request_obj = requests.Request()

    async def verify_token(self, token: str) -> Optional[GoogleTokenPayload]:
        """
        Verify a Google ID token.

        Args:
            token: Google ID token from frontend

        Returns:
            GoogleTokenPayload if valid, None otherwise
        """
        if not self.config.is_configured():
            logger.error("Google OAuth not configured")
            return None

        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token,
                self.request_obj,
                self.config.client_id
            )

            # Additional security check
            if idinfo.get('aud') != self.config.client_id:
                logger.error(f"Token audience mismatch: {idinfo.get('aud')} != {self.config.client_id}")
                return None

            # Extract payload
            payload = GoogleTokenPayload(
                sub=idinfo.get('sub'),
                email=idinfo.get('email'),
                email_verified=idinfo.get('email_verified', False),
                name=idinfo.get('name', ''),
                picture=idinfo.get('picture'),
                aud=idinfo.get('aud')
            )

            return payload

        except ValueError as e:
            logger.error(f"Invalid Google token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            return None

    def get_google_login_url(self) -> str:
        """
        Get the Google login URL for redirecting users.

        Returns:
            Google OAuth login URL
        """
        if not self.config.is_configured():
            logger.error("Google OAuth not configured")
            return ""

        # Base Google OAuth URL
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"

        # Query parameters
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }

        # Build URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"


# Global instance
_google_config: Optional[GoogleOAuthConfig] = None
_google_provider: Optional[GoogleOAuthProvider] = None


def get_google_config() -> GoogleOAuthConfig:
    """Get or initialize Google OAuth config."""
    global _google_config
    if _google_config is None:
        _google_config = GoogleOAuthConfig()
    return _google_config


def get_google_provider() -> GoogleOAuthProvider:
    """Get or initialize Google OAuth provider."""
    global _google_provider
    if _google_provider is None:
        config = get_google_config()
        _google_provider = GoogleOAuthProvider(config)
    return _google_provider
