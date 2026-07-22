import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.users.model import User
from app.modules.users.schema import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Fetch user by primary key ID."""
        statement = select(User).where(User.id == user_id)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by unique email."""
        statement = select(User).where(User.email == email)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_phone(self, phone: str) -> User | None:
        """Fetch user by unique phone number."""
        statement = select(User).where(User.phone == phone)
        result = await self.db.exec(statement)
        return result.first()

    async def get_by_tin(self, tin: str) -> User | None:
        """Fetch user by unique TIN."""
        statement = select(User).where(User.tin == tin)
        result = await self.db.exec(statement)
        return result.first()

    async def create(self, user_create: UserCreate, hashed_password: str) -> User:
        """Create and persist a new user."""
        db_user = User(
            email=user_create.email,
            phone=user_create.phone,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            tin=user_create.tin,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False,
            role=getattr(user_create, "role", "Employee") or "Employee"
        )
        self.db.add(db_user)
        await self.db.flush()  # Populates ID and defaults
        return db_user

    async def get_all_users(self) -> list[User]:
        """Fetch all users for Super Admin oversight."""
        statement = select(User).order_by(User.created_at.desc())
        result = await self.db.exec(statement)
        return list(result.all())


    async def update(self, db_user: User, user_update: UserUpdate) -> User:
        """Update an existing user's attributes."""
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "password":
                # Handle password elsewhere or pass hashed_password directly
                continue
            setattr(db_user, key, value)
        
        self.db.add(db_user)
        await self.db.flush()
        return db_user
