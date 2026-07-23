# API Documentation

The Bangladesh Tax Suite exposes a RESTful API under the `/api/v1` namespace.

## Base Paths
- **API Base URL**: `http://localhost:8000/api/v1`
- **Swagger Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc Interactive Docs**: `http://localhost:8000/redoc`

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### Register User
- **URL**: `/auth/register`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "email": "user@example.com",
    "phone": "+8801700000000",
    "first_name": "First",
    "last_name": "Last",
    "tin": "123456789012",
    "password": "securepassword",
    "role": "Employee",
    "company_name": "Optional Corporate Name"
  }
  ```
- **Response (`201 Created`)**:
  ```json
  {
    "id": "uuid-v4-string",
    "email": "user@example.com",
    "phone": "+8801700000000",
    "first_name": "First",
    "last_name": "Last",
    "is_active": true,
    "role": "Employee"
  }
  ```

### Login User
- **URL**: `/auth/login`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "user@example.com",
    "password": "securepassword"
  }
  ```
  *(Note: `username` accepts either Email or Phone Number)*

---

## 2. Super Admin Control Center (`/api/v1/users`)

### Get All System Users
- **URL**: `/users/admin/all`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <super_admin_token>`

### Approve / Suspend User Status
- **URL**: `/users/admin/{user_id}/status`
- **Method**: `PUT`
- **Payload**: `{"is_active": true}`

---

## 3. Reports & Exports (`/api/v1/reports`)

### Download PDF Return & Computation Sheet
- **URL**: `/reports/tax-return/pdf?financial_year=2025-2026`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `application/pdf` (Downloadable NBR Computation Summary)

### Download Excel Salary Statement
- **URL**: `/reports/salary/excel?financial_year=2025-2026`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (Multi-tab Excel Log)

---

## 4. OCR Document Parser (`/api/v1/ocr`)

### Parse Salary Slip / Certificate PDF
- **URL**: `/ocr/parse-salary-pdf`
- **Method**: `POST`
- **Body**: `FormData` (`file`: PDF Document)
- **Response (`200 OK`)**:
  ```json
  {
    "success": true,
    "message": "Parsed successfully",
    "data": {
      "basic": 60000.0,
      "house_rent": 20000.0,
      "medical": 5000.0,
      "conveyance": 5000.0,
      "festival_bonus": 0.0,
      "tds_deducted": 2000.0,
      "financial_year": "2025-2026"
    }
  }
  ```

---

## 5. AI Tax Assistant (`/api/v1/ai`)

### Tax Chat Advisory
- **URL**: `/ai/tax-chat`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "prompt": "What is the maximum DPS investment rebate cap under Section 78?"
  }
  ```
- **Response (`200 OK`)**:
  ```json
  {
    "reply": "Under Section 78 of the Income Tax Act 2023...",
    "key_points": ["Max eligible DPS investment: BDT 1,20,000 / year", "15% rebate rate"],
    "reference_laws": ["Income Tax Act 2023 - Section 78"]
  }
  ```

---

## 6. Tax Calculation Engine (`/api/v1/taxes`)

### Calculate Tax & Investment Rebates
- **URL**: `/taxes/calculate`
- **Method**: `POST`
- **Payload**: `{"financial_year": "2025-2026", "other_income": "0.00"}`

### Calculate and Persist History
- **URL**: `/taxes/calculate-save`
- **Method**: `POST`

---

## 7. Utility & Health (`/health`)

### System Readiness Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response (`200 OK`)**:
  ```json
  {
    "status": "healthy",
    "services": {
      "api": "online",
      "database": "online",
      "cache": "online"
    }
  }
  ```
