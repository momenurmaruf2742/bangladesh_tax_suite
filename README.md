# ৳ Bangladesh Tax Suite

> Enterprise-Grade, Production-Ready Income Tax Management SaaS for Bangladesh.

The **Bangladesh Tax Suite** is a modern, scalable web application designed to manage employee tax profiles, salary structures, tax investments, source taxes (AIT), and generate official tax returns according to current National Board of Revenue (NBR) rules.

---

## 🚀 Tech Stack

### Backend
- **Core**: Python 3.12+ (FastAPI)
- **Database Mapping**: SQLModel (SQLAlchemy + Pydantic v2)
- **Database & Cache**: PostgreSQL & Redis
- **Testing & Quality**: Pytest & Ruff
- **Deployment**: Docker & Docker Compose

### Frontend
- **Core**: React 19 (TypeScript, Vite)
- **Styling**: Tailwind CSS v4 (Vanilla UI design with Glassmorphism)
- **State & Routing**: TanStack Query & React Router
- **Forms & Validation**: React Hook Form & Zod

---

## 🛠️ Project Structure

```text
bangladesh-tax-suite/
├── backend/          # FastAPI async backend code
│   ├── app/          # Core modules (auth, users, database, etc.)
│   └── tests/        # Python integration testing suites
├── frontend/         # React typescript frontend interface
│   ├── src/          # Source components, pages, routes, and services
│   └── dist/         # Production compiled assets
├── docs/             # Technical specifications & installation details
├── docker-compose.yml# Main orchestration script
└── .gitignore        # Version control exclude configurations
```

---

## ⚡ Quick Start (Docker Compose)

Start the entire application suite (Database, Cache, Backend API, and Frontend web portal) using Docker:

```bash
# Build and run all container services
docker compose up --build
```

### Access Points
- **Frontend App**: [http://localhost:5173](http://localhost:5173)
- **FastAPI backend Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Local Tests

Run integration and API test cases locally using the configured SQLite memory driver:

```bash
# Move to backend folder
cd backend

# Activate virtual environment
source ../.venv/bin/activate

# Execute pytest
pytest
```

---

## 📅 Development Roadmap

- **Sprint 1 (Current)**: Foundation Setup, DB & Cache Connections, JWT Authentication (Email & Phone), User registration/profiles, Docker integration.
- **Sprint 2**: Employee Profiles & Salary Structures.
- **Sprint 3**: NBR Tax Calculation Engine & Slabbing rules.
- **Sprint 4**: Rebate engines & AIT adjustments.
- **Sprint 5**: Document uploads & OCR PDF parsing.
