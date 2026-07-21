from fastapi import APIRouter, Depends, Header, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schema import LoginRequest, RefreshTokenRequest, TokenResponse
from app.modules.auth.service import AuthService
from app.modules.users.schema import UserCreate, UserResponse
from app.modules.users.service import UserService

router = APIRouter(tags=["Authentication"])
security_bearer = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user in the system."""
    user_service = UserService(db)
    return await user_service.create_user(user_in)


@router.post("/login", response_model=TokenResponse)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Standard JSON API Login using Email or Phone."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(login_in.username, login_in.password)
    return auth_service.generate_tokens(user.id)


@router.post("/token", response_model=TokenResponse, include_in_schema=True)
async def login_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """OAuth2 Form-compatible Login for Swagger UI compatibility."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    return auth_service.generate_tokens(user.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_in: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh JWT access token using a valid refresh token."""
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(refresh_in.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_in: RefreshTokenRequest,
    authorization: str = Header(..., description="Bearer <access_token>"),
    db: AsyncSession = Depends(get_db)
):
    """Log out a user, revoking both current access and refresh tokens."""
    auth_service = AuthService(db)
    
    # Extract access token
    access_token = ""
    if authorization.startswith("Bearer "):
        access_token = authorization.split(" ")[1]
    elif authorization.startswith("bearer "):
        access_token = authorization.split(" ")[1]
    else:
        access_token = authorization
        
    await auth_service.revoke_tokens(access_token, refresh_in.refresh_token)
    return {"detail": "Successfully logged out"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    """Retrieve details of the currently authenticated user."""
    return current_user
