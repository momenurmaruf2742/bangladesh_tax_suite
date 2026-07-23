import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.schema import UserResponse
from app.modules.users.service import UserService

router = APIRouter(tags=["Users Oversight"])


class UserStatusUpdate(BaseModel):
    is_active: bool


@router.get("/admin/all", response_model=list[UserResponse])
async def get_all_users(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all users for Super Admin dashboard."""
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Super Admin only."
        )
    user_service = UserService(db)
    return await user_service.get_all_users()


@router.put("/admin/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: uuid.UUID,
    status_in: UserStatusUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve or suspend a user account (Super Admin only)."""
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Super Admin only."
        )
    user_service = UserService(db)
    return await user_service.update_user_status(user_id, status_in.is_active)
