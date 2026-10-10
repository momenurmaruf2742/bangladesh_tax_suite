# ৳ Bangladesh Tax Suite

> Enterprise-Grade, Production-Ready Income Tax Management SaaS for Bangladesh based on Income Tax Act 2023.

## 📌 About The Project

**Bangladesh Tax Suite** is an automated, production-ready SaaS platform built to simplify individual and corporate income tax management in Bangladesh under the **National Board of Revenue (NBR) Income Tax Act 2023**.

### Key Features
- 🔐 **Multi-Role Authentication & Access Control**: Self-registration for Individual Taxpayers, Corporate Admins, and CA Firms with Super Admin approval workflow.
- 📐 **NBR Income Tax Act 2023 Calculation Engine**: Dynamic, multi-year support via a central rules registry config. Performs automated progressive slab calculations, 1/3rd salary exemptions, and tax-free threshold rule application for FY 2024-2025 and 2025-2026 with 100% mathematical parity against official NBR e-Returns.
- 💎 **Section 78 Investment Rebate Engine**: Automated, assessment-year-aware rebate calculations. It dynamically adjusts investment tax rebate rates (15% for FY 24-25, 10% for FY 25-26), investment ceilings (৳1 Crore down to ৳75 Lakh), and DPS limits (৳1.2L cap).
- ⚖️ **NBR Form IT-10B & IT-10BB Wealth Reconciliation**: Full statutory implementation of Statement of Assets & Liabilities (Form IT-10B) and Lifestyle Expenses (Form IT-10BB). Enforces automated double-entry net wealth reconciliation: $\text{Total Inflow} == \text{Total Outflow}$ and $\text{Difference} = \text{৳0.00}$, complete with an auto-balance cash-in-hand assistant.
- ⚡ **PDF OCR Salary Certificate Parser**: Automated text extraction from uploaded salary certificates and payslips with smart zero-tax (Nil) fallback detection.
- 📥 **Official Multi-Page NBR Form IT-11GA (2023) PDF Exporter**: Generates authentic, production-ready multi-page NBR return packets including Part 1-5, Schedule 1 (Salary), Schedule 5 (Rebate), Form IT-10BB, Form IT-10B, TDS Challans, and Acknowledgement Receipts, alongside multi-tab Excel Salary Statements.
- 📊 **Visual Analytics & Wealth Wizard**: Interactive Recharts Donut & Bar charts for salary component breakdowns and tax slab progressions, plus a dedicated interactive IT-10B Wealth Reconciliation wizard.
- 🤖 **AI Tax Assistant**: Embedded AI chatbot grounded in Bangladesh Income Tax Act 2023 regulations.

---

## 🚀 Tech Stack

### Backend
- **Core Framework**: Python 3.12+ / 3.13 (FastAPI)
- **Database & ORM**: PostgreSQL & SQLModel (SQLAlchemy AsyncSession + Pydantic v2)
- **Caching & Sessions**: Redis
- **Rules Registry**: Dynamic, configuration-driven tax rules system (`app/core/tax_rules.py`) supporting Finance Act 2024 and 2026.
- **Reporting Engine**: ReportLab multi-page canvas with custom grids and NBR-compliant tables.
- **Testing & Quality**: Pytest (19 comprehensive Unit & Integration Tests covering multi-year calculations, IT-10B, IT-10BB, and PDF generation)
- **Deployment**: Docker & Docker Compose

### Frontend
- **Core Framework**: React 19 (TypeScript, Vite)
- **Styling**: Tailwind CSS (Dark Mode Glassmorphic UI)
- **Visual Analytics**: Recharts (Donut & Bar Charts)
- **State & Data Fetching**: TanStack Query (React Query v5) & Axios (reactive to active financial year)
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
  - DPS (max ৳1.2L cap), Sanchayapatra, Life Insurance, Stock Market, and AIT Challans with year-aware Section 78 investment tax rebate engine (15% or 10% rebate rate).
- ⚖️ **Form IT-10B Wealth & IT-10BB Expense Statements**:
  - Comprehensive 9-line categorized lifestyle expenditures (essentials, rent, transport, utility, festival, tax).
  - Detailed asset and liability tracking (business, property, DPS, ornaments, vehicles, furniture, cash/bank).
  - Live double-entry reconciliation checking $\text{Total Sources of Fund} - \text{Total Fund Outflow} = 0$, with auto-balance cash feature.
- 📊 **Visual Analytics & Dashboards**:
  - Interactive Recharts Donut Chart for salary allowances, Bar Chart for progressive NBR tax slabs (0%, 5%, 10%, 15%, 20%, 25%), and Wealth Reconciliation View.
- 📥 **Authentic NBR Return PDF & Excel Export**:
  - One-click downloadable multi-page **Form IT-11GA (2023)** PDF return with schedules, IT-10B/BB, and tax acknowledgement receipt, plus **Multi-tab Monthly Salary & Investment Statement** (Excel `.xlsx`).
- ⚡ **PDF OCR Auto-Parser**:
  - Upload PDF payslips or salary certificates to automatically extract Basic, House Rent, Medical, Conveyance, Bonus, and TDS figures.
- 🤖 **AI Tax Assistant**:
  - Interactive floating AI chatbot grounded in **Bangladesh Income Tax Act 2023** regulations.

---

## 🔧 Environment Configuration Guide (`.env`)

Configure the environment files before running the application:

### 1. Backend Configuration (`backend/.env`)
Copy `backend/.env.example` to `backend/.env`:
```env
PROJECT_NAME="Bangladesh Tax Suite"
API_V1_STR="/api/v1"

# Database Settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tax_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379

# Security Settings (Generate secure keys for Production)
JWT_SECRET_KEY=supersecretaccesskeyforbangladeshtaxsuite2026!!!
JWT_REFRESH_SECRET_KEY=supersecretrefreshkeyforbangladeshtaxsuite2026!!!
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Allowed Origins
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "*"]
```

### 2. Frontend Configuration (`frontend/.env`)
Copy `frontend/.env.example` to `frontend/.env`:
```env
# Leave VITE_API_URL empty for automatic dynamic local IP / localhost detection
VITE_API_URL=
```
*(For production domain deployments, set `VITE_API_URL=https://api.taxsuite.com/api/v1`)*

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

## 💻 Local Development Setup (Without Docker)

If you prefer to run services locally without Docker:

### 1. Database & Cache Services
Ensure PostgreSQL is running locally on port `5432` with a database named `tax_db` and Redis is running on port `6379`.

### 2. Backend Setup
1. Move to backend folder:
   ```bash
   cd backend
   ```
2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
5. Provision test accounts:
   ```bash
   python scripts/setup_accounts.py
   ```
6. Run server:
   ```bash
   python app/main.py
   ```

### 3. Frontend Setup
1. Move to frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start Vite dev server:
   ```bash
   npm run dev
   ```

---

## 🌐 Production Deployment Guide

To deploy **Bangladesh Tax Suite** to a Linux VPS (DigitalOcean, AWS EC2, Hetzner, etc.):

### Step 1: Open Server Firewall Ports
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### Step 2: Set Production Environment Variables
Generate secure keys via `openssl rand -hex 32` and update `backend/.env`:
- Change `POSTGRES_PASSWORD` to a strong password.
- Update `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY`.
- Set `BACKEND_CORS_ORIGINS=["https://taxsuite.yourdomain.com"]`.
- Set `VITE_API_URL=https://taxsuite.yourdomain.com/api/v1` in `frontend/.env`.

### Step 3: Run Docker Compose in Background
```bash
docker compose up --build -d
```

### Step 4: Configure Nginx & SSL (Certbot)
Install Nginx and Let's Encrypt Certbot:
```bash
sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx
```
Configure Nginx reverse proxy pointing port 80/443 to `http://127.0.0.1:5173` (Frontend) and `/api/` to `http://127.0.0.1:8000` (Backend). Then obtain SSL:
```bash
sudo certbot --nginx -d taxsuite.yourdomain.com
```

Detailed technical specifications and architecture guidelines can be found in the [`docs/`](./docs) folder:
- [Installation & Setup Guide](docs/installation.md)
- [Architecture Specifications](docs/architecture.md)
- [REST API Reference](docs/api.md)

---

## 🛠️ Project Structure

```text
bangladesh-tax-suite/
├── backend/                  # FastAPI async backend code
│   ├── app/
│   │   ├── core/             # Security, JWT, dynamic tax rules registry
│   │   ├── db/               # Database engine & init_db
│   │   ├── modules/          # Domain Modules
│   │   │   ├── auth/         # Login, Register, JWT, Profile
│   │   │   ├── users/        # Super Admin Oversight & Approval
│   │   │   ├── employers/    # Corporate Employer Directory
│   │   │   ├── employees/    # Employee Profiles & NID/TIN/Zone/Circle
│   │   │   ├── salaries/     # Monthly Slips & Summary
│   │   │   ├── investments/  # DPS, Insurance, AIT Challans
│   │   │   ├── taxes/        # NBR Act 2023 Tax Engine, IT-10B, IT-10BB models
│   │   │   ├── reports/      # Multi-Page ReportLab PDF Return & Excel Exporters
│   │   │   ├── ocr/          # PyPDF OCR Text Extraction Parser
│   │   │   └── ai/           # AI Tax Advisory Assistant
│   │   └── main.py           # FastAPI entrypoint & router registry
│   ├── scripts/
│   │   ├── setup_accounts.py # CLI Account Provisioning Script
│   │   └── create_superadmin.py # Standalone Super Admin Creator
│   └── tests/                # 19 Unit & Integration tests (IT-10B, IT-10BB, PDF, Rules)
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # TaxCalculatorPanel, WealthReconciliationView, AiTaxAssistantDrawer
│   │   ├── pages/            # Login, Register, Dashboard
│   │   └── services/         # Axios API client
│   └── public/
├── docs/                     # Technical specifications (api.md, architecture.md, installation.md)
└── docker-compose.yml        # Orchestration configuration
```

---

## 🧪 Running Local Tests

Execute backend pytest suite (all 19 tests passing):

```bash
# Move to backend folder
cd backend

# Execute pytest using uv or active virtual environment
uv run pytest
# or
pytest app/tests
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
- ✅ **Phase 1-3 Compliance (NBR IT-11GA 2023 Parity)**:
  - Form IT-10BB Lifestyle Expenses Model & API (9 statutory lines).
  - Form IT-10B Statement of Assets & Liabilities with automated double-entry Net Wealth Reconciliation ($Difference = 0$).
  - Frontend Wealth Reconciliation Wizard with instant cash auto-balancing.
  - Multi-Page Authentic NBR Form IT-11GA (2023) PDF Generator (Parts 1-5, Schedules 1 & 5, IT-10B, IT-10BB, Challan Schedule & Receipt).
- ⏳ **Sprint 9+**: Official NBR e-Return XML exporter & Bangla i18n language switcher.
