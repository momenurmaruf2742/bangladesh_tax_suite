import argparse
import asyncio
import os
import sys

parser = argparse.ArgumentParser(description="Create or promote a Super Admin user account.")
parser.add_argument("--email", default="superadmin@taxsuite.com", help="Super Admin Email")
parser.add_argument("--phone", default="01963191891", help="Super Admin Phone Number")
parser.add_argument("--password", default="strongpassword123", help="Super Admin Password")
parser.add_argument("--first-name", default="Super", help="First Name")
parser.add_argument("--last-name", default="Admin", help="Last Name")
parser.add_argument("--db-url", default=None, help="Database Connection URL")

args = parser.parse_args()

if args.db_url:
    os.environ["DATABASE_URL"] = args.db_url

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlmodel import select
from app.db.database import async_session_maker, init_db
from app.modules.users.model import User
from app.core.security import hash_password


async def run_create():
    await init_db()
    async with async_session_maker() as session:
        statement = select(User).where((User.email == args.email) | (User.phone == args.phone))
        result = await session.exec(statement)
        existing_user = result.first()

        if existing_user:
            existing_user.role = "SuperAdmin"
            existing_user.is_active = True
            existing_user.is_verified = True
            existing_user.password_hash = hash_password(args.password)
            session.add(existing_user)
            await session.commit()
            print(f"✅ Existing user '{args.email}' updated to SuperAdmin role successfully!")
        else:
            new_admin = User(
                email=args.email,
                phone=args.phone,
                password_hash=hash_password(args.password),
                first_name=args.first_name,
                last_name=args.last_name,
                is_active=True,
                is_verified=True,
                role="SuperAdmin"
            )
            session.add(new_admin)
            await session.commit()
            print(f"✅ New SuperAdmin account created successfully for '{args.email}'!")


if __name__ == "__main__":
    asyncio.run(run_create())
