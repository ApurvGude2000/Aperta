"""
Authentication dependencies for FastAPI routes.
Extracts and validates JWT tokens from request headers.
"""

from fastapi import HTTPException, status, Header
from typing import Optional
from auth.utils import get_user_from_token


async def get_token_from_header(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Extract JWT token from Authorization header.

    Expected format: "Bearer <token>"

    Args:
        authorization: Authorization header value

    Returns:
        JWT token

    Raises:
        HTTPException: If token is missing or invalid format
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>"
        )

    return parts[1]


async def get_current_user_id(
    token: str = Header(None, alias="Authorization")
) -> str:
    """
    Get current user ID from valid JWT token.

    Args:
        token: Authorization header value

    Returns:
        User ID

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    # Extract token from "Bearer <token>" format
    parts = token.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token_str = parts[1]
    user_id = get_user_from_token(token_str)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return user_id
