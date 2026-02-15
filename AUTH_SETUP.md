# Authentication Setup - MVP Guide

## Overview

Aperta now has a **complete MVP authentication system** with:
- ✅ User registration
- ✅ User login
- ✅ JWT token generation
- ✅ Password hashing (bcrypt)
- ✅ Token refresh
- ✅ Local database storage

---

## Quick Start

### 1. Install Dependencies

```bash
pip install PyJWT==2.8.1 bcrypt==4.1.2 email-validator==2.1.0
```

Or update from requirements.txt:
```bash
pip install -r backend/requirements.txt
```

### 2. Set JWT Secret Key

In your `.env` file:
```bash
JWT_SECRET_KEY=your-super-secret-key-change-in-production
```

If not set, it defaults to `"your-secret-key-change-in-production"` (not secure for production!)

### 3. Create User Table

The User table is automatically created when the app starts. Just ensure your database is set up.

### 4. Start the Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Endpoints

### 1. User Registration

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johnsmith",
  "password": "SecurePassword123!",
  "full_name": "John Smith",
  "company": "Acme Corp"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid-123",
    "email": "user@example.com",
    "username": "johnsmith",
    "full_name": "John Smith",
    "company": "Acme Corp",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-02-15T12:00:00"
  },
  "tokens": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Notes:**
- Password must be at least 6 characters
- Email must be unique
- Username must be unique

---

### 2. User Login

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid-123",
    "email": "user@example.com",
    "username": "johnsmith",
    "full_name": "John Smith",
    "company": "Acme Corp",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-02-15T12:00:00",
    "last_login": "2026-02-15T12:30:00"
  },
  "tokens": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

---

### 3. Get Current User

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid-123",
  "email": "user@example.com",
  "username": "johnsmith",
  "full_name": "John Smith",
  "company": "Acme Corp",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-02-15T12:00:00"
}
```

---

### 4. Refresh Token

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Using Tokens with Protected Endpoints

### In cURL:
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/audio/process
```

### In JavaScript/Fetch:
```javascript
const response = await fetch('http://localhost:8000/audio/process', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### In Python/Requests:
```python
import requests

headers = {
    'Authorization': f'Bearer {token}'
}
response = requests.get('http://localhost:8000/auth/me', headers=headers)
print(response.json())
```

---

## Token Details

### Access Token
- **Lifetime:** 30 minutes (configurable)
- **Use:** API requests authentication
- **Expires:** After 30 minutes

### Refresh Token
- **Lifetime:** 7 days (configurable)
- **Use:** Get new access token
- **Expires:** After 7 days

### Token Format
JWT (JSON Web Token) with:
- Header: Algorithm (HS256)
- Payload: User ID (`sub`), Expiration (`exp`)
- Signature: HMAC-SHA256

---

## Database Schema

### users table

```sql
CREATE TABLE users (
  id VARCHAR PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  username VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  full_name VARCHAR,
  company VARCHAR,
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

---

## Password Security

### Hashing
- Algorithm: **bcrypt** with 12 rounds
- Library: `bcrypt.hashpw()`
- Never stores plain passwords

### Verification
```python
from auth.utils import verify_password

if verify_password("user_password", hashed_password):
    # Password matches
    pass
else:
    # Password incorrect
    pass
```

---

## Configuration

### JWT Secret Key

In `.env`:
```bash
JWT_SECRET_KEY=your-super-secret-key-change-in-production
```

**Important:** Change this in production!

### Token Expiration

In `backend/auth/utils.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30      # 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7         # 7 days
```

Modify these values to change token lifetime.

---

## Error Responses

### Invalid Credentials
```json
{
  "detail": "Invalid email or password"
}
```
Status: `401 Unauthorized`

### User Not Found
```json
{
  "detail": "User not found or inactive"
}
```
Status: `401 Unauthorized`

### Duplicate Email/Username
```json
{
  "detail": "Email or username already registered"
}
```
Status: `400 Bad Request`

### Invalid Token
```json
{
  "detail": "Invalid or expired token"
}
```
Status: `401 Unauthorized`

### Missing Authorization Header
```json
{
  "detail": "Missing authorization header"
}
```
Status: `401 Unauthorized`

---

## Testing Authentication

### 1. Register a user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

Save the `access_token` from the response.

### 3. Get Current User

```bash
TOKEN="<your_access_token>"
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Upload Audio (Protected)

```bash
TOKEN="<your_access_token>"
curl -X POST http://localhost:8000/audio/process \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_audio.wav"
```

---

## Security Checklist

- [ ] Change `JWT_SECRET_KEY` in production
- [ ] Use HTTPS in production (not HTTP)
- [ ] Implement password strength validation
- [ ] Add rate limiting to login/register endpoints
- [ ] Add email verification before account activation
- [ ] Implement account lockout after failed attempts
- [ ] Log authentication events
- [ ] Rotate JWT secret key periodically

---

## Next Steps

### Short-term (MVP)
- ✅ User registration & login
- ✅ JWT token generation
- ✅ Password hashing
- ⏳ Protect audio endpoints with auth
- ⏳ Frontend login page

### Medium-term (Enhancement)
- Email verification
- Password reset
- Multi-factor authentication (MFA)
- OAuth2 integration
- Session management

### Long-term (Production)
- Account lockout policies
- Rate limiting
- Audit logging
- Compliance (GDPR, SOC2)

---

## Protecting Endpoints

To protect an endpoint, add user dependency:

```python
from fastapi import Depends
from auth.dependencies import get_current_user_id

@app.get("/protected")
async def protected_route(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}
```

User can only access if they provide valid token in `Authorization: Bearer <token>` header.

---

## Integration with Audio Endpoints

Audio processing endpoints can now optionally require authentication:

```python
# Optional: Add user dependency to audio.py
from auth.dependencies import get_current_user_id

@router.post("/process")
async def process_audio_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),  # Add this
    db: AsyncSession = Depends(get_db_session)
):
    # user_id is now available
    # Can associate recording with user
    pass
```

---

## Summary

✅ **Complete MVP authentication system implemented**
- User registration with email validation
- Secure login with password hashing
- JWT token generation and refresh
- Token-based API protection ready
- Local database storage
- Production-ready error handling

**Ready to integrate with frontend!**
