import argparse
import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal
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
from app.modules.employees.model import Employee
from app.modules.salaries.model import SalarySlip
from app.modules.investments.model import Investment
from app.modules.taxes.model import IT10BStatement, IT10BAssetItem, LifestyleExpense
from app.core.security import hash_password


async def setup_accounts():
    await init_db()
    async with async_session_maker() as session:
        # 1. Setup normal user: momenur.maruf@gmail.com
        stmt1 = select(User).where((User.email == "momenur.maruf@gmail.com") | (User.phone == "01711223344"))
        res1 = await session.exec(stmt1)
        user1 = res1.first()
        if user1:
            user1.email = "momenur.maruf@gmail.com"
            user1.phone = "01711223344"
            user1.role = "Employee"
            user1.tin = "531631892211"
            user1.is_active = True
            user1.is_verified = True
            user1.password_hash = hash_password("strongpassword123")
            session.add(user1)
            print("✅ Existing user updated to Normal User 'momenur.maruf@gmail.com'!")
        else:
            user1 = User(
                email="momenur.maruf@gmail.com",
                phone="01711223344",
                password_hash=hash_password("strongpassword123"),
                first_name="Momenur",
                last_name="Maruf",
                tin="531631892211",
                is_active=True,
                is_verified=True,
                role="Employee"
            )
            session.add(user1)
            await session.flush()
            print("✅ New Normal User 'momenur.maruf@gmail.com' created!")

        # 2. Setup super user: momenur.tax@taxsuite.com
        stmt2 = select(User).where((User.email == "momenur.tax@taxsuite.com") | (User.phone == "01963191891"))
        res2 = await session.exec(stmt2)
        user2 = res2.first()
        if user2:
            user2.email = "momenur.tax@taxsuite.com"
            user2.phone = "01963191891"
            user2.role = "SuperAdmin"
            user2.is_active = True
            user2.is_verified = True
            user2.password_hash = hash_password("strongpassword123")
            session.add(user2)
            print("✅ Existing user updated to Super Admin 'momenur.tax@taxsuite.com'!")
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

        await session.flush()

        # 3. Setup Employee profile for user1
        stmt_emp = select(Employee).where(Employee.user_id == user1.id)
        emp = (await session.exec(stmt_emp)).first()
        if not emp:
            emp = Employee(
                user_id=user1.id,
                designation="Lead Software Engineer",
                department="Engineering",
                nid="1992123456789",
                tax_zone="Zone 15, Dhaka",
                tax_circle="Circle 330",
                gender="Male",
                location="Dhaka/Chittagong City Corporation",
                date_of_joining=date(2022, 1, 1),
            )
            session.add(emp)
            await session.flush()
            print("✅ Employee profile created for user1!")
        else:
            emp.tax_zone = "Zone 15, Dhaka"
            emp.tax_circle = "Circle 330"
            emp.designation = "Lead Software Engineer"
            emp.department = "Engineering"
            emp.nid = "1992123456789"
            session.add(emp)

        # 4. Seed Monthly Slips for FY 2025-2026 if not already present
        stmt_slips = select(SalarySlip).where(SalarySlip.employee_id == emp.id)
        existing_slips = (await session.exec(stmt_slips)).all()
        if not existing_slips:
            # 12 months from 2025-07 to 2026-06
            # Total Gross: 10,07,300 (Basic: 5,76,300, Allowances: 4,31,000, TDS: 9,542)
            # 10 regular months + 2 festival bonus months
            months = [
                "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12",
                "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"
            ]
            # Regular month: basic 48,025, rent 24,012.5, med 4,002, conv 4,002 = 80,041.5
            # We want exact totals:
            # basic: 48,025 * 12 = 5,76,300
            # house_rent: 24,012.50 * 12 = 2,88,150
            # medical: 4,002 * 12 = 48,024
            # conveyance: 4,002.16 * 12 = 48,026
            # bonus in 2 festival months: 23,400 each = 46,800
            # TDS: 795 * 10 + 796 * 2 = 9,542
            for i, m in enumerate(months):
                is_fest = i in (2, 8) # Sep & Mar
                fest_val = Decimal("23400.00") if is_fest else Decimal("0.00")
                tds_val = Decimal("796.00") if is_fest else Decimal("795.00")
                slip = SalarySlip(
                    employee_id=emp.id,
                    month=m,
                    basic_salary=Decimal("48025.00"),
                    house_rent=Decimal("24012.50"),
                    medical_allowance=Decimal("4002.00"),
                    conveyance=Decimal("4002.17") if i == 0 else Decimal("4002.17"),
                    festival_bonus=fest_val,
                    other_allowances=Decimal("0.00"),
                    employer_provident_fund=Decimal("0.00"),
                    provident_fund=Decimal("0.00"),
                    tax_deducted=tds_val,
                )
                session.add(slip)
            print("✅ 12 Monthly Salary slips seeded for FY 2025-2026!")

        # 5. Seed Investments for FY 2025-2026
        stmt_inv = select(Investment).where(Investment.employee_id == emp.id)
        existing_inv = (await session.exec(stmt_inv)).all()
        if not existing_inv:
            inv1 = Investment(
                employee_id=emp.id,
                category="DPS",
                financial_year="2025-2026",
                amount=Decimal("70000.00"),
                description="Sonali Bank DPS A/C 45012398",
            )
            inv2 = Investment(
                employee_id=emp.id,
                category="DPS",
                financial_year="2025-2026",
                amount=Decimal("10000.00"),
                description="Eastern Bank Ltd DPS A/C 10874521",
            )
            session.add(inv1)
            session.add(inv2)
            print("✅ DPS Investments seeded for FY 2025-2026!")

        # 6. Seed Lifestyle Expense (IT-10BB)
        stmt_life = select(LifestyleExpense).where(
            LifestyleExpense.user_id == user1.id,
            LifestyleExpense.financial_year == "2025-2026"
        )
        existing_life = (await session.exec(stmt_life)).first()
        if not existing_life:
            life = LifestyleExpense(
                user_id=user1.id,
                financial_year="2025-2026",
                assessment_year="2026-2027",
                food_clothing_essentials=Decimal("150000.00"),
                housing_expense=Decimal("70000.00"),
                transport_expense=Decimal("50000.00"),
                utility_expense=Decimal("49000.00"),
                education_expense=Decimal("0.00"),
                travel_vacation_expense=Decimal("0.00"),
                festival_special_expense=Decimal("50000.00"),
                tax_deducted_source_advance=Decimal("9542.00"),
                interest_borrowing_expense=Decimal("0.00"),
                total_lifestyle_expense=Decimal("378542.00"),
            )
            session.add(life)
            print("✅ IT-10BB Lifestyle expenses seeded!")

        # 7. Seed IT-10B Statement
        stmt_it10b = select(IT10BStatement).where(
            IT10BStatement.user_id == user1.id,
            IT10BStatement.financial_year == "2025-2026"
        )
        existing_it10b = (await session.exec(stmt_it10b)).first()
        if not existing_it10b:
            it10b = IT10BStatement(
                user_id=user1.id,
                financial_year="2025-2026",
                assessment_year="2026-2027",
                taxable_income=Decimal("671533.00"),
                tax_exempted_income=Decimal("335767.00"),
                gifts_and_other_receipts=Decimal("0.00"),
                net_wealth_previous_year=Decimal("127758.00"),
                lifestyle_expenses=Decimal("378542.00"),
                other_outflow_losses=Decimal("0.00"),
                financial_assets_dps=Decimal("55000.00"),
                furniture_electronics_value=Decimal("75000.00"),
                bank_balances=Decimal("320000.00"),
                cash_in_hand=Decimal("306516.00"),
                institutional_liabilities=Decimal("0.00"),
                non_institutional_liabilities=Decimal("0.00"),
                gross_wealth=Decimal("756516.00"),
                net_wealth_closing=Decimal("756516.00"),
                difference=Decimal("0.00"),
                is_balanced=True,
            )
            session.add(it10b)
            await session.flush()

            # Seed asset items
            item1 = IT10BAssetItem(
                statement_id=it10b.id,
                asset_category="motor_vehicles",
                description="Dhaka Metro LA 67-6774, Suzuki Gixxer (155 CC)",
                acquisition_type="Gift",
                cost_value=Decimal("0.00"),
                particulars={"quantity": "1 Unit", "engine_cc": "155 CC", "year": "2023"},
            )
            item2 = IT10BAssetItem(
                statement_id=it10b.id,
                asset_category="ornaments_gold",
                description="22K Gold Ring & Chain",
                acquisition_type="Gift",
                cost_value=Decimal("0.00"),
                particulars={"weight": "4.75 Gram", "year": "2022"},
            )
            session.add(item1)
            session.add(item2)
            print("✅ IT-10B Statement & Asset Items seeded!")

        await session.commit()
        print("🎉 All accounts & NBR benchmark data successfully setup!")


if __name__ == "__main__":
    asyncio.run(setup_accounts())
