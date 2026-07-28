# ৳ Bangladesh Tax Suite

> Enterprise-Grade, Production-Ready Income Tax Management SaaS for Bangladesh based on Income Tax Act 2023.

## 📌 About The Project

**Bangladesh Tax Suite** is an automated, production-ready SaaS platform built to simplify individual and corporate income tax management in Bangladesh under the **National Board of Revenue (NBR) Income Tax Act 2023**.

### Key Features
- 🔐 **Multi-Role Authentication & Access Control**: Self-registration for Individual Taxpayers, Corporate Admins, and CA Firms with Super Admin approval workflow.
- 📐 **NBR Income Tax Act 2023 Calculation Engine**: Automated progressive slab calculations (0%, 5%, 10%, 15%, 20%, 25%), 1/3rd salary exemption limits (up to ৳4.5L), and tax-free threshold rules.
- 💎 **Section 78 Investment Rebate Engine**: Automated rebate calculations for DPS (৳1.2L cap), Sanchayapatra, Life Insurance, Stock Market, and Provident Fund (PF) contributions.
- ⚡ **PDF OCR Salary Certificate Parser**: Automated text extraction from uploaded salary certificates and payslips with smart zero-tax (Nil) fallback detection.
- 📥 **PDF & Excel Exporters**: One-click downloadable official NBR Form IT-1152023 Income Tax Return Computation Sheet (PDF) and multi-tab Excel Salary Statements.
- 📊 **Visual Analytics**: Interactive Recharts Donut & Bar charts for salary component breakdowns and tax slab progressions.
- 🤖 **AI Tax Assistant**: Embedded AI chatbot grounded in Bangladesh Income Tax Act 2023 regulations.

---

## 🚀 Tech Stack

### Backend
- **Core Framework**: Python 3.12+ (FastAPI)
- **Database & ORM**: PostgreSQL & SQLModel (SQLAlchemy AsyncSession + Pydantic v2)
- **Caching & Sessions**: Redis
- **PDF & Excel Engine**: ReportLab & OpenPyXL
- **PDF OCR Parser**: PyPDF with Regex Pattern Recognition
- **Testing & Quality**: Pytest (13 Unit & Integration Tests)
- **Deployment**: Docker & Docker Compose

### Frontend
- **Core Framework**: React 19 (TypeScript, Vite)
- **Styling**: Tailwind CSS (Dark Mode Glassmorphic UI)
- **Visual Analytics**: Recharts (Donut & Bar Charts)
- **State & Data Fetching**: TanStack Query (React Query v5) & Axios
- **Form Management**: React Hook Form & Zod
- **Icons**: Lucide React

---

## ✨ System Capabilities & Workflows

- 🔐 **Multi-Role Authentication & Access Control**:
  - Self-registration for **Individual Taxpayers** (auto-approved), **Company Admins**, and **CA Firms** (pending Super Admin approval).
  - JWT Access & Refresh Token rotation with Redis blacklist revocation.
- 👑 **Super Admin Control Center**:
  - Platform user oversight table, one-click account activation/suspension toggles, and live NBR Act 2023 rules engine viewer.
- 🏢 **Employer & Employee Management**:
  - Corporate employer group registration, NID, 12-digit TIN validation, Tax Zone, and Circle tracking.
- 💵 **Salary Components & Payslips**:
  - Monthly salary logs, quick gross auto-split helper (60% basic, 30% house rent, 5% medical, 5% conveyance), and annual salary summary aggregator.
- 📈 **Investments & AIT Tracker**:
  - DPS (max ৳1.2L cap), Sanchayapatra, Life Insurance, Stock Market, and AIT Challans with Section 78 15% investment tax rebate engine.
- 📊 **Visual Analytics (Sprint 7)**:
  - Interactive Recharts Donut Chart for salary allowances and Bar Chart for progressive NBR tax slabs (0%, 5%, 10%, 15%, 20%, 25%).
- 📥 **PDF Return & Excel Export (Sprint 6)**:
  - One-click downloadable **NBR Income Tax Return Computation Sheet** (PDF) and **Multi-tab Monthly Salary & Investment Statement** (Excel `.xlsx`).
- ⚡ **PDF OCR Auto-Parser (Sprint 8)**:
  - Upload PDF payslips or salary certificates to automatically extract Basic, House Rent, Medical, Conveyance, Bonus, and TDS figures.
- 🤖 **AI Tax Assistant (Sprint 8)**:
  - Interactive floating AI chatbot grounded in **Bangladesh Income Tax Act 2023** regulations.

---

## 🛠️ Project Structure

```text
bangladesh-tax-suite/
├── backend/                  # FastAPI async backend code
│   ├── app/
│   │   ├── core/             # Security, JWT, settings
│   │   ├── db/               # Database engine & init_db
│   │   ├── modules/          # Domain Modules
│   │   │   ├── auth/         # Login, Register, JWT, Profile
│   │   │   ├── users/        # Super Admin Oversight & Approval
│   │   │   ├── employers/    # Corporate Employer Directory
│   │   │   ├── employees/    # Employee Profiles & NID/TIN
│   │   │   ├── salaries/     # Monthly Slips & Summary
│   │   │   ├── investments/  # DPS, Insurance, AIT Challans
│   │   │   ├── taxes/        # NBR Act 2023 Tax Calculation Engine
│   │   │   ├── reports/      # ReportLab PDF & OpenPyXL Excel Exporters
│   │   │   ├── ocr/          # PyPDF OCR Text Extraction Parser
│   │   │   └── ai/           # AI Tax Advisory Assistant
│   │   └── main.py           # FastAPI entrypoint & router registry
│   ├── scripts/
│   │   └── setup_accounts.py # CLI Account Provisioning Script
│   └── tests/                # Integration & unit tests
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # Loader, TaxCalculatorPanel, AiTaxAssistantDrawer
│   │   ├── pages/            # Login, Register, Dashboard
│   │   └── services/         # Axios API client
├── docs/                     # Technical specifications (api.md, architecture.md, installation.md)
└── docker-compose.yml        # Orchestration configuration
```

---

## ⚡ Quick Start (Docker Compose)

Launch the entire stack (PostgreSQL, Redis, FastAPI Backend, React Frontend) with one command:

```bash
# 1. Build and run all docker services
docker compose up --build

# 2. Provision default Super Admin & Test User accounts inside container
docker compose exec backend python /app/scripts/setup_accounts.py
```

### Access URLs
- **Frontend App**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **API Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

### Default Test Credentials
- 👑 **Super Admin**: `momenur.tax@taxsuite.com` | Password: `strongpassword123`
- 👤 **Normal User**: `momenur.maruf@gmail.com` | Password: `strongpassword123`

---

## 🧪 Running Local Tests

Execute backend pytest suite (13 tests passing):

```bash
# Move to backend folder
cd backend

# Execute pytest
.venv/bin/pytest app/tests
```

---

## 📅 Development Roadmap & Status

- ✅ **Sprint 1 (Foundation + Auth)**: Stack Initialization, Docker, Redis Token Blacklist, JWT Authentication.
- ✅ **Sprint 2 (Employee & Employer)**: Employee Profiles, NID, TIN, Corporate Employer Directory.
- ✅ **Sprint 3 (Salary Management)**: Monthly Salary Slips, Payslip PDF Storage, Annual Summary.
- ✅ **Sprint 4 (Investment & AIT)**: DPS, Sanchayapatra, Insurance, Stocks, AIT Challan Log.
- ✅ **Sprint 5 (Tax Engine Act 2023)**: Tax Slabs, Thresholds, Section 78 Rebate Engine, Form 108 HTML View.
- ✅ **Sprint 6 (Reports & Exports)**: ReportLab PDF Return Computation & OpenPyXL Excel Export.
- ✅ **Sprint 7 (Dashboard Analytics)**: Recharts Salary & Tax Slab Visualizations.
- ✅ **Sprint 8 (OCR & AI Assistant)**: PDF Payslip OCR Auto-Parser & Interactive AI Tax Assistant Chatbot.
- ⏳ **Sprint 9+**: Official NBR e-Return XML exporter & Bangla i18n language switcher.
