"""
Authentication API routes for user login/signup.
MVP: Local authentication with JWT tokens.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
import logging

from db.session import get_db_session
from db.models_auth import User
from auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_from_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from auth.google_oauth import get_google_provider, GoogleTokenPayload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Pydantic models for request/response
class UserRegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    username: str
    password: str
    full_name: str = None
    company: str = None


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


class UserResponse(BaseModel):
    """User response."""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response with user and tokens."""
    user: UserResponse
    tokens: TokenResponse


# Routes

@router.post("/register", response_model=LoginResponse, status_code=201)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db_session)
) -> LoginResponse:
    """
    Register a new user.

    Args:
        request: Registration details
        db: Database session

    Returns:
        User info and authentication tokens
    """
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(
                (User.email == request.email) | (User.username == request.username)
            )
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )

        # Validate password strength (MVP: simple check)
        if len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )

        # Create new user
        hashed_password = hash_password(request.password)
        new_user = User(
            email=request.email,
            username=request.username,
            password_hash=hashed_password,
            full_name=request.full_name,
            company=request.company,
            is_active=True,
            is_verified=False
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"New user registered: {new_user.email}")

        # Generate tokens
        access_token = create_access_token({"sub": new_user.id})
        refresh_token = create_refresh_token({"sub": new_user.id})

        return LoginResponse(
            user=UserResponse.from_orm(new_user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db_session)
) -> LoginResponse:
    """
    Login user with email and password.

    Args:
        request: Login credentials
        db: Database session

    Returns:
        User info and authentication tokens
    """
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"User logged in: {user.email}")

        # Generate tokens
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_refresh_token({"sub": user.id})

        return LoginResponse(
            user=UserResponse.from_orm(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Refresh token
        db: Database session

    Returns:
        New access token
    """
    try:
        # Decode refresh token
        payload = decode_token(refresh_token)

        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")

        # Verify user still exists
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new access token
        new_access_token = create_access_token({"sub": user.id})

        logger.info(f"Token refreshed for user: {user.email}")

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str = None
) -> UserResponse:
    """
    Get current logged-in user info.

    Requires Authorization header: Bearer <token>

    Args:
        db: Database session
        token: JWT token from header (dependency injection)

    Returns:
        Current user info
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided"
        )

    user_id = get_user_from_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.from_orm(user)


# Google OAuth endpoints

class GoogleLoginRequest(BaseModel):
    """Google OAuth login request."""
    token: str  # Google ID token from frontend


class GoogleLoginURL(BaseModel):
    """Google login URL response."""
    url: str


@router.get("/google/login-url", response_model=GoogleLoginURL)
async def get_google_login_url() -> GoogleLoginURL:
    """
    Get the Google OAuth login URL.

    Frontend should redirect user to this URL.

    Returns:
        Google OAuth login URL
    """
    try:
        provider = get_google_provider()
        url = provider.get_google_login_url()

        if not url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth is not configured"
            )

        return GoogleLoginURL(url=url)

    except Exception as e:
        logger.error(f"Error getting Google login URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Google login URL"
        )


@router.post("/google/login", response_model=LoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db_session)
) -> LoginResponse:
    """
    Login or register user with Google OAuth token.

    Args:
        request: Google ID token from frontend
        db: Database session

    Returns:
        User info and authentication tokens
    """
    try:
        # Verify Google token
        provider = get_google_provider()
        payload = await provider.verify_token(request.token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

        # Check if user exists
        result = await db.execute(
            select(User).where(User.email == payload.email)
        )
        user = result.scalar_one_or_none()

        # Create user if doesn't exist
        if not user:
            logger.info(f"Creating new user from Google OAuth: {payload.email}")

            # Generate username from email
            username = payload.email.split("@")[0]
            # Make username unique if needed
            counter = 1
            original_username = username
            while True:
                result = await db.execute(
                    select(User).where(User.username == username)
                )
                if result.scalar_one_or_none() is None:
                    break
                username = f"{original_username}{counter}"
                counter += 1

            # Create new user
            user = User(
                email=payload.email,
                username=username,
                password_hash="",  # OAuth users don't have password
                full_name=payload.name,
                is_active=True,
                is_verified=payload.email_verified
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Update last login
        user.last_login = datetime.utcnow()
        db.add(user)
        await db.commit()

        logger.info(f"User logged in via Google: {user.email}")

        # Generate tokens
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_refresh_token({"sub": user.id})

        return LoginResponse(
            user=UserResponse.from_orm(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during Google login: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google login failed"
        )
