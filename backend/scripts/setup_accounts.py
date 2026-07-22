import argparse
import asyncio
import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

parser = argparse.ArgumentParser(description="Setup default accounts for testing.")
parser.add_argument("--db-url", default=None, help="Database Connection URL")
args = parser.parse_args()

if args.db_url:
    os.environ["DATABASE_URL"] = args.db_url
    from app.core.config import settings
    settings.DATABASE_URL = args.db_url

from sqlmodel import select
from app.db.database import async_session_maker, init_db
from app.modules.users.model import User
from app.core.security import hash_password


async def setup_accounts():
    await init_db()
    async with async_session_maker() as session:
        # 1. Setup normal user: momenur.maruf@gmail.com
        stmt1 = select(User).where(User.email == "momenur.maruf@gmail.com")
        res1 = await session.exec(stmt1)
        user1 = res1.first()
        if user1:
            user1.role = "Employee"
            user1.is_active = True
            user1.is_verified = True
            user1.password_hash = hash_password("strongpassword123")
            session.add(user1)
            print("✅ Existing user 'momenur.maruf@gmail.com' updated to Normal User (Employee)!")
        else:
            user1 = User(
                email="momenur.maruf@gmail.com",
                phone="01711223344",
                password_hash=hash_password("strongpassword123"),
                first_name="Momenur",
                last_name="Maruf",
                is_active=True,
                is_verified=True,
                role="Employee"
            )
            session.add(user1)
            print("✅ New Normal User 'momenur.maruf@gmail.com' created!")

        # 2. Setup super user: momenur.tax@taxsuite.com
        stmt2 = select(User).where(User.email == "momenur.tax@taxsuite.com")
        res2 = await session.exec(stmt2)
        user2 = res2.first()
        if user2:
            user2.role = "SuperAdmin"
            user2.is_active = True
            user2.is_verified = True
            user2.password_hash = hash_password("strongpassword123")
            session.add(user2)
            print("✅ Existing user 'momenur.tax@taxsuite.com' updated to Super Admin!")
        else:
            user2 = User(
                email="momenur.tax@taxsuite.com",
                phone="01963191891",
                password_hash=hash_password("strongpassword123"),
                first_name="Momenur",
                last_name="TaxAdmin",
                is_active=True,
                is_verified=True,
                role="SuperAdmin"
            )
            session.add(user2)
            print("✅ New Super Admin 'momenur.tax@taxsuite.com' created!")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(setup_accounts())
