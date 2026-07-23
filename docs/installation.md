# Installation & Setup Guide

This guide explains how to deploy the Bangladesh Tax Suite using Docker Compose or for local development.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js v18+](https://nodejs.org/)

---

## 🐳 Docker Deployment (Recommended)

To launch the complete containerized stack (PostgreSQL, Redis, FastAPI Backend, React Frontend):

1. Clone the repository and navigate to root:
   ```bash
   git clone <repo-url>
   cd bangladesh-tax-suite
   ```

2. Build and start containers:
   ```bash
   docker compose up --build
   ```

3. Provision default Super Admin and Test User accounts in Docker database:
   ```bash
   docker compose exec backend python /app/scripts/setup_accounts.py
   ```

4. Access the applications:
   - **Frontend App**: [http://localhost:5173](http://localhost:5173)
   - **FastAPI Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 💻 Local Development Setup

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
