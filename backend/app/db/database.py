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
    """Initialize database tables and ensure schema updates for existing tables."""
    # Import all models to populate SQLModel metadata
    try:
        import app.modules.users.model  # noqa
        import app.modules.employers.model  # noqa
        import app.modules.employees.model  # noqa
        import app.modules.salaries.model  # noqa
        import app.modules.investments.model  # noqa
        import app.modules.taxes.model  # noqa
    except Exception:
        pass

    async with engine.begin() as conn:
        # Create all tables if they do not exist
        await conn.run_sync(SQLModel.metadata.create_all)
        # Ensure new columns exist on existing tables
        try:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE salary_slips ADD COLUMN IF NOT EXISTS doc_path VARCHAR;"))
            await conn.execute(text("UPDATE users SET tin = NULL WHERE tin = '' OR tin IS NOT NULL AND TRIM(tin) = '';"))
        except Exception:
            pass

    # Ensure required accounts exist with correct roles
    async with async_session_maker() as session:
        try:
            from sqlmodel import select
            from app.modules.users.model import User
            from app.core.security import hash_password

            # 1. Ensure SuperAdmin: momenur.tax@taxsuite.com
            stmt1 = select(User).where(User.email == "momenur.tax@taxsuite.com")
            res1 = await session.exec(stmt1)
            user_super = res1.first()
            if not user_super:
                user_super = User(
                    email="momenur.tax@taxsuite.com",
                    phone="01963191891",
                    password_hash=hash_password("strongpassword123"),
                    first_name="Momenur",
                    last_name="TaxAdmin",
                    is_active=True,
                    is_verified=True,
                    role="SuperAdmin"
                )
                session.add(user_super)
            else:
                user_super.role = "SuperAdmin"
                user_super.is_active = True
                user_super.is_verified = True
                user_super.password_hash = hash_password("strongpassword123")
                session.add(user_super)

            # 2. Ensure Normal User: momenur.maruf@gmail.com
            stmt2 = select(User).where(User.email == "momenur.maruf@gmail.com")
            res2 = await session.exec(stmt2)
            user_norm = res2.first()
            if user_norm:
                user_norm.role = "Employee"
                user_norm.is_active = True
                session.add(user_norm)

            await session.commit()
        except Exception as e:
            print(f"Notice: Initial account seeding status: {e}")






async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        yield session
        await session.commit()
