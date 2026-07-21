# Installation Guide

This guide explains how to install and run the Bangladesh Tax Suite project locally and inside Docker.

## Prerequisites

Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js v18+](https://nodejs.org/)

---

## 🐳 Docker Deployment (Recommended)

To launch the entire stack (PostgreSQL, Redis, FastAPI, and React Vite) in containerized mode:

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd bangladesh-tax-suite
   ```

2. Start the services:
   ```bash
   docker compose up --build
   ```

3. Access the interfaces:
   - **Frontend App**: [http://localhost:5173](http://localhost:5173)
   - **FastAPI Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Alternative API Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 💻 Local Development Setup

If you prefer to run services locally without Docker:

### 1. Database & Cache Services
Ensure PostgreSQL is running locally on port `5432` with a database named `tax_db` and Redis is running on port `6379`.

### 2. Backend Setup
1. Move to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables template and customize:
   ```bash
   cp .env.example .env
   ```
5. Run the FastAPI development server:
   ```bash
   python main.py
   ```
   The backend will be live on [http://localhost:8000](http://localhost:8000).

### 3. Frontend Setup
1. Move to the frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   The frontend will be live on [http://localhost:5173](http://localhost:5173).
