import uuid
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.security import hash_password
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self, user_create: UserCreate) -> User:
        # Check duplicate email
        existing_email = await self.repo.get_by_email(user_create.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check duplicate phone
        existing_phone = await self.repo.get_by_phone(user_create.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Check duplicate TIN (if provided)
        if user_create.tin:
            existing_tin = await self.repo.get_by_tin(user_create.tin)
            if existing_tin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="TIN already registered"
                )
        
        hashed_password = hash_password(user_create.password)
        return await self.repo.create(user_create, hashed_password)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> User:
        user = await self.get_user_by_id(user_id)
        
        # Check duplicate email
        if user_update.email and user_update.email != user.email:
            existing_email = await self.repo.get_by_email(user_update.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
        
        # Check duplicate phone
        if user_update.phone and user_update.phone != user.phone:
            existing_phone = await self.repo.get_by_phone(user_update.phone)
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already in use"
                )
        
        # Check duplicate TIN
        if user_update.tin and user_update.tin != user.tin:
            existing_tin = await self.repo.get_by_tin(user_update.tin)
            if existing_tin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="TIN already in use"
                )

        if user_update.password:
            user.password_hash = hash_password(user_update.password)
            
        return await self.repo.update(user, user_update)
