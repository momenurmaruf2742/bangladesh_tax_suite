from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.modules.auth.schema import TokenResponse
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.utils.redis import redis_client


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user using either email or phone number."""
        user = None
        # Check if it looks like an email or phone
        if "@" in username:
            user = await self.user_repo.get_by_email(username)
        else:
            user = await self.user_repo.get_by_phone(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending Super Admin approval. Please wait for activation or contact support."
            )

        return user

    def generate_tokens(self, user_id: uuid.UUID) -> TokenResponse:
        """Generate Access and Refresh tokens for user."""
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and return a new token pair."""
        # 1. Check if token is blacklisted in Redis
        is_blacklisted = await redis_client.exists(f"blacklist:{refresh_token}")
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Decode refresh token
        user_id_str = decode_token(refresh_token, is_refresh=True)
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Retrieve user
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # 4. Optional: Blacklist old refresh token (token rotation security)
        # We can blacklist it for a short duration to allow clients to receive the response
        await redis_client.set_value(f"blacklist:{refresh_token}", "revoked", 86400 * 7)

        # 5. Return new tokens
        return self.generate_tokens(user.id)

    async def revoke_tokens(self, access_token: str, refresh_token: str) -> None:
        """Revoke user tokens by blacklisting them in Redis."""
        # Blacklist Access Token (typically short-lived, expire after 30 mins)
        if access_token:
            await redis_client.set_value(f"blacklist:{access_token}", "logged_out", 1800)
        
        # Blacklist Refresh Token (long-lived, expire after 7 days)
        if refresh_token:
            await redis_client.set_value(f"blacklist:{refresh_token}", "logged_out", 86400 * 7)
            
        return
