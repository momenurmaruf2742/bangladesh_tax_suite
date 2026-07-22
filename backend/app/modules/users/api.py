from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.schema import UserResponse
from app.modules.users.service import UserService

router = APIRouter(tags=["Users Oversight"])


@router.get("/admin/all", response_model=list[UserResponse])
async def get_all_users(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all users for Super Admin dashboard."""
    if current_user.role not in ["SuperAdmin", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to platform administrators."
        )
    user_service = UserService(db)
    return await user_service.get_all_users()
