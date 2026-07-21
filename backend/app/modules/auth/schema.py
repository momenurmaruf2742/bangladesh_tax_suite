from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Email address or Phone number")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid JWT Refresh Token")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
