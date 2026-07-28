# Installation & Production Deployment Guide

This guide explains how to install, configure environment variables, and deploy the Bangladesh Tax Suite locally and in a production server environment.

---

## 📋 Prerequisites

- **Docker & Docker Compose**: [Get Docker](https://docs.docker.com/get-docker/) & [Compose](https://docs.docker.com/compose/install/)
- **Python 3.12+** (For local non-containerized dev setup)
- **Node.js v18+ & npm** (For local frontend development)

---

## 🔧 Environment Configuration Guide (`.env`)

The project uses separate environment configuration files for the **Backend** and **Frontend**.

### 1. Backend Environment (`backend/.env`)

| Variable Key | Default / Recommended Value | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `"Bangladesh Tax Suite"` | Title of the SaaS application |
| `API_V1_STR` | `"/api/v1"` | Base URL prefix for REST API endpoints |
| `POSTGRES_USER` | `postgres` | PostgreSQL database user |
| `POSTGRES_PASSWORD` | `postgres` (Change in Prod) | PostgreSQL database password |
| `POSTGRES_DB` | `tax_db` | PostgreSQL database name |
| `POSTGRES_HOST` | `postgres` (Docker) / `localhost` (Local) | Database host address |
| `POSTGRES_PORT` | `5432` | Database connection port |
| `REDIS_HOST` | `redis` (Docker) / `localhost` (Local) | Redis server host address |
| `REDIS_PORT` | `6379` | Redis connection port |
| `JWT_SECRET_KEY` | *(Generate via `openssl rand -hex 32`)* | Secret key for signing JWT access tokens |
| `JWT_REFRESH_SECRET_KEY` | *(Generate via `openssl rand -hex 32`)* | Secret key for signing JWT refresh tokens |
| `JWT_ALGORITHM` | `HS256` | Token hashing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifespan in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifespan in days |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:5173", "*"]` | Allowed CORS origins for browser security |

---

### 2. Frontend Environment (`frontend/.env`)

| Variable Key | Default / Recommended Value | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | *(Leave blank for dynamic IP detection)* / `https://api.taxsuite.com/api/v1` | Backend API base URL |

> 💡 **Note on Dynamic Local IP Access:** Leaving `VITE_API_URL=` empty allows the React frontend to dynamically match the browser's hostname (e.g. `http://192.168.x.x:8000/api/v1` or `http://localhost:8000/api/v1`), making local network access on mobile devices seamless.

---

## 🐳 Docker Deployment (Recommended)

To launch the complete containerized stack (PostgreSQL 16, Redis 7, FastAPI Backend, React Frontend):

1. Clone the repository:
   ```bash
   git clone https://github.com/momenurmaruf2742/bangladesh_tax_suite.git
   cd bangladesh_tax_suite
   ```

2. Copy environment templates:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. Build and start services:
   ```bash
   docker compose up --build -d
   ```

4. Provision default Super Admin and Test User accounts:
   ```bash
   docker compose exec backend python /app/scripts/setup_accounts.py
   ```

5. Access the applications:
   - **Frontend Web Portal**: `http://<server-ip>:5173`
   - **FastAPI Interactive Docs (Swagger)**: `http://<server-ip>:8000/docs`

---

## 🚀 Production Server Deployment Guide

Follow these steps to deploy **Bangladesh Tax Suite** on an Ubuntu/Debian Linux VPS (DigitalOcean, AWS EC2, Hetzner, etc.):

### 1. Server Hardening & Port Setup
Ensure firewall allows HTTP/HTTPS and SSH traffic:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 2. Configure Production Secrets
Generate secure random keys for JWT in `backend/.env`:
```bash
openssl rand -hex 32
```
Update `backend/.env` with production DB password and the generated JWT secret keys. Set `BACKEND_CORS_ORIGINS=["https://taxsuite.yourdomain.com"]`.

### 3. Setup Nginx Reverse Proxy with SSL (Let's Encrypt)
Install Nginx and Certbot:
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

Create Nginx site configuration (`/etc/nginx/sites-available/taxsuite`):
```nginx
server {
    server_name taxsuite.yourdomain.com;

    # Frontend Static App
    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API Endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 20M;
    }
}
```

Enable site and obtain SSL Certificate:
```bash
sudo ln -s /etc/nginx/sites-available/taxsuite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d taxsuite.yourdomain.com
```

---

## 💻 Local Development Setup (Without Docker)

### 1. Local Database & Cache
Ensure local PostgreSQL (`tax_db` database) is running on port `5432` and Redis is running on `6379`.

### 2. Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/setup_accounts.py
python app/main.py
```

### 3. Frontend
```bash
cd ../frontend
npm install
cp .env.example .env
npm run dev
```
