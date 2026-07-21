from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from app.core.security import decode_token
from app.db.database import get_db
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.utils.redis import redis_client

security_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to retrieve the currently authenticated user from the JWT access token."""
    token = credentials.credentials
    
    # 1. Check if access token is blacklisted in Redis (e.g. logged out)
    is_blacklisted = await redis_client.exists(f"blacklist:{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Decode the token
    user_id_str = decode_token(token, is_refresh=False)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload format",
        )

    # 3. Retrieve user from db
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
        
    return user


async def get_current_active_admin(user: User = Depends(get_current_user)) -> User:
    """Check if the current user has the Admin role."""
    if user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return user


async def get_current_active_ca_or_admin(user: User = Depends(get_current_user)) -> User:
    """Check if the current user has either Admin or Chartered Accountant (CA) role."""
    if user.role not in ["Admin", "CA"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin or CA role required."
        )
    return user
