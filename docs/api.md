# API Documentation

The Bangladesh Tax Suite exposes a RESTful API under the `/api/v1` namespace.

## Base Paths
- **API Base URL**: `http://localhost:8000/api/v1`
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Docs**: `http://localhost:8000/redoc`

---

## Authentication Endpoints

### 1. Register User
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
    "password": "securepassword"
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
    "tin": "123456789012",
    "is_active": true,
    "is_verified": false,
    "role": "Employee",
    "created_at": "ISO-datetime-string",
    "updated_at": "ISO-datetime-string"
  }
  ```

### 2. Login User
- **URL**: `/auth/login`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "user@example.com",
    "password": "securepassword"
  }
  ```
  *(Note: `username` can be either Email or Phone Number)*
- **Response (`200 OK`)**:
  ```json
  {
    "access_token": "jwt-access-token-string",
    "refresh_token": "jwt-refresh-token-string",
    "token_type": "bearer"
  }
  ```

### 3. Refresh Token
- **URL**: `/auth/refresh`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "refresh_token": "jwt-refresh-token-string"
  }
  ```
- **Response (`200 OK`)**:
  ```json
  {
    "access_token": "jwt-new-access-token-string",
    "refresh_token": "jwt-new-refresh-token-string",
    "token_type": "bearer"
  }
  ```

### 4. Logout User
- **URL**: `/auth/logout`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Payload**:
  ```json
  {
    "refresh_token": "jwt-refresh-token-string"
  }
  ```
- **Response (`200 OK`)**:
  ```json
  {
    "detail": "Successfully logged out"
  }
  ```

### 5. Get Profile
- **URL**: `/auth/profile`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Response (`200 OK`)**:
  ```json
  {
    "id": "uuid-v4-string",
    "email": "user@example.com",
    "phone": "+8801700000000",
    "first_name": "First",
    "last_name": "Last",
    "tin": "123456789012",
    "is_active": true,
    "is_verified": false,
    "role": "Employee",
    "created_at": "ISO-datetime-string",
    "updated_at": "ISO-datetime-string"
  }
  ```

---

## Utility Endpoints

### Health Check
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
