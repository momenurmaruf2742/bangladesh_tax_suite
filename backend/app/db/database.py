from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

# Create database engine
# echo=True is helpful for debugging, but in production, you might want to disable it
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10
)

# Async session maker
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """Initialize database tables and seed default Super Admin if missing."""
    async with engine.begin() as conn:
        # Create all tables if they do not exist
        await conn.run_sync(SQLModel.metadata.create_all)
        # Ensure new columns exist on existing tables
        try:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS doc_path VARCHAR;"))
        except Exception:
            pass

    # Seed default Super Admin user
    async with async_session_maker() as session:
        try:
            from sqlmodel import select
            from app.modules.users.model import User
            from app.core.security import hash_password

            statement = select(User).where((User.email == "superadmin@taxsuite.com") | (User.phone == "01963191891"))
            result = await session.exec(statement)
            existing_admin = result.first()

            if not existing_admin:
                admin_user = User(
                    email="superadmin@taxsuite.com",
                    phone="01963191891",
                    password_hash=hash_password("strongpassword123"),
                    first_name="Super",
                    last_name="Admin",
                    is_active=True,
                    is_verified=True,
                    role="SuperAdmin"
                )
                session.add(admin_user)
                await session.commit()
            else:
                existing_admin.role = "SuperAdmin"
                existing_admin.password_hash = hash_password("strongpassword123")
                session.add(existing_admin)
                await session.commit()
        except Exception as e:
            print(f"Notice: Super Admin seeding status: {e}")




async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        yield session
        await session.commit()
