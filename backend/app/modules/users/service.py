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
        new_user = await self.repo.create(user_create, hashed_password)

        # If role is Admin or CA and company_name is provided, auto-create Employer/Firm record
        if user_create.role in ["Admin", "CA"] and user_create.company_name:
            try:
                from app.modules.employers.model import Employer
                from app.modules.employers.repository import EmployerRepository
                employer_repo = EmployerRepository(self.repo.db)
                bin_str = f"BIN-{uuid.uuid4().hex[:8].upper()}"
                employer = Employer(
                    name=user_create.company_name,
                    address="Head Office, Bangladesh",
                    bin=bin_str,
                    contact_email=user_create.email,
                    contact_phone=user_create.phone
                )
                await employer_repo.create(employer)
            except Exception as e:
                print(f"Notice: Auto employer creation failed: {e}")

        return new_user

    async def get_all_users(self) -> list[User]:
        return await self.repo.get_all_users()

    async def update_user_status(self, user_id: uuid.UUID, is_active: bool) -> User:
        user = await self.repo.update_status(user_id, is_active)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user



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
