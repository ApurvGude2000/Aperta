# Google Cloud OAuth Setup - Local Development

Complete guide to set up Google Cloud OAuth for local development and testing.

## Overview

This setup allows users to sign up and login using their Google account instead of creating a new password. Perfect for local development and testing.

## Prerequisites

- Google Cloud Project (free tier available)
- Python 3.10+ backend
- React frontend
- Node.js for frontend

## Step 1: Create Google Cloud Project

### 1.1 Create Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Enter project name: "Aperta" (or your choice)
4. Click "Create"
5. Wait for project to be created

### 1.2 Enable OAuth Consent Screen
1. In Google Cloud Console, go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (for testing)
3. Click **Create**
4. Fill in the form:
   - **App name:** Aperta
   - **User support email:** your-email@gmail.com
   - **Developer contact:** your-email@gmail.com
5. Click **Save and Continue**
6. Skip "Scopes" section, click **Save and Continue**
7. Skip "Test users" section, click **Save and Continue**
8. Click **Back to Dashboard**

## Step 2: Create OAuth 2.0 Credentials

### 2.1 Create Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Web application**
4. Fill in the form:
   - **Name:** Aperta Local
   - **Authorized JavaScript origins:** Add these:
     - `http://localhost:5173` (frontend)
     - `http://localhost:3000` (alternative frontend port)
     - `http://localhost` (general localhost)
   - **Authorized redirect URIs:** Add these:
     - `http://localhost:8000/auth/callback/google`
     - `http://localhost:8000/auth/google/callback`
     - `http://localhost:5173/auth/callback`

5. Click **Create**

### 2.2 Copy Credentials
You'll see a dialog with:
- **Client ID**
- **Client Secret**

**IMPORTANT:** Copy these values securely!

## Step 3: Install Python Dependencies

```bash
cd backend

# Add to requirements.txt:
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.2.0
google-auth>=2.25.0
```

Then install:
```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

Create/update `.env` file in the `backend/` directory:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
```

**Example .env:**
```bash
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google
JWT_SECRET_KEY=my_super_secret_key_12345
```

## Step 5: Configure Frontend

Create/update `.env.local` file in `frontend/` directory:

```bash
VITE_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
VITE_API_URL=http://localhost:8000
```

**Example .env.local:**
```bash
VITE_GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
VITE_API_URL=http://localhost:8000
```

## Step 6: Start Services

### Terminal 1: Backend
```bash
cd backend
python main.py
```

Check health:
```bash
curl http://localhost:8000/health
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Open: http://localhost:5173

## Testing Google Login Locally

### Test 1: Get Login URL
```bash
curl http://localhost:8000/auth/google/login-url
```

Response:
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=..."
}
```

### Test 2: Frontend Login Flow
1. Open http://localhost:5173
2. Click "Sign in with Google" button
3. Select your Google account
4. You should be redirected to dashboard
5. Check browser console for tokens (DevTools → Console)

### Test 3: Verify User Created
```bash
sqlite3 aperta.db "SELECT id, email, username FROM users LIMIT 5;"
```

## File Structure

### Backend Files
- `backend/auth/google_oauth.py` - Google OAuth provider (NEW)
- `backend/api/routes/auth.py` - Auth endpoints (UPDATED)
- `backend/db/models_auth.py` - User model (EXISTING)
- `backend/auth/utils.py` - JWT utilities (EXISTING)

### Frontend Files
- `frontend/src/components/GoogleLogin.tsx` - Google login component (NEW)

## API Endpoints

### Get Google Login URL
```bash
GET /auth/google/login-url

Response:
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### Login with Google Token
```bash
POST /auth/google/login
Content-Type: application/json

{
  "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1In0..."
}

Response:
{
  "user": {
    "id": "user-id",
    "email": "user@gmail.com",
    "username": "username",
    "full_name": "Full Name",
    "is_active": true,
    "is_verified": true,
    "created_at": "2024-02-14T10:00:00"
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

## Troubleshooting

### Issue: "GOOGLE_CLIENT_ID not set"
**Solution:** Add `GOOGLE_CLIENT_ID` to `.env` file in backend directory

### Issue: "Token audience mismatch"
**Solution:** Make sure `GOOGLE_CLIENT_ID` in backend matches frontend `VITE_GOOGLE_CLIENT_ID`

### Issue: "Invalid redirect URI"
**Solution:** Add all your redirect URIs to Google Cloud Console:
- Go to Credentials
- Edit OAuth 2.0 Client ID
- Add your URIs to "Authorized redirect URIs"

### Issue: Google Login Button Not Showing
**Solution:**
1. Check browser console (F12) for errors
2. Verify `VITE_GOOGLE_CLIENT_ID` is set in frontend
3. Check that Google Sign-In script loaded:
   ```javascript
   console.log(window.google?.accounts?.id)  // Should not be undefined
   ```

### Issue: "Invalid Google token" Error
**Solution:**
1. Verify token was obtained from Google (check browser console)
2. Check that backend has correct GOOGLE_CLIENT_ID
3. Try clearing browser cache and restarting

### Issue: Tokens Not Saving to LocalStorage
**Solution:**
1. Check browser DevTools → Storage → Local Storage
2. Should have `access_token` and `refresh_token`
3. If not, check browser console for errors

## Security Notes

### Local Development Only
```bash
# .env (LOCAL - CHANGE IN PRODUCTION)
GOOGLE_CLIENT_ID=abc123...
GOOGLE_CLIENT_SECRET=secret123...
JWT_SECRET_KEY=local-secret-change-this
```

### Production Setup
For production, you'll need:
1. HTTPS URLs (change from http:// to https://)
2. Production domain in Google Cloud Console
3. Strong JWT_SECRET_KEY
4. Environment-specific .env files
5. Secrets manager (e.g., AWS Secrets Manager)

## Environment Switching

### Development (.env.development)
```bash
GOOGLE_CLIENT_ID=dev-client-id
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google
JWT_SECRET_KEY=dev-secret
```

### Production (.env.production)
```bash
GOOGLE_CLIENT_ID=prod-client-id
GOOGLE_REDIRECT_URI=https://api.aperta.app/auth/callback/google
JWT_SECRET_KEY=strong-production-secret
```

Load appropriate file:
```bash
# Development
export ENV=development
python main.py

# Production
export ENV=production
python main.py
```

## Next Steps

1. ✅ Create Google Cloud Project
2. ✅ Get OAuth credentials
3. ✅ Install dependencies
4. ✅ Configure environment
5. ✅ Start backend and frontend
6. ✅ Test login flow
7. Create better login UI (optional)
8. Add social sign-up benefits (optional)
9. Deploy to production (future)

## Support

If you encounter issues:

1. **Check logs:**
   ```bash
   # Backend
   tail -f backend.log

   # Frontend (Browser Console)
   F12 → Console
   ```

2. **Verify credentials:**
   ```bash
   # Check environment variables are loaded
   python -c "import os; print(os.getenv('GOOGLE_CLIENT_ID'))"
   ```

3. **Test API directly:**
   ```bash
   curl -X POST http://localhost:8000/auth/google/login \
     -H "Content-Type: application/json" \
     -d '{"token": "YOUR_GOOGLE_TOKEN"}'
   ```

## Files Modified/Created

### NEW Files
- `backend/auth/google_oauth.py` - Google OAuth provider
- `frontend/src/components/GoogleLogin.tsx` - Login component
- `GOOGLE_OAUTH_SETUP.md` - This guide

### MODIFIED Files
- `backend/api/routes/auth.py` - Added Google OAuth endpoints
- `backend/requirements.txt` - Added Google auth libraries
- `.env` - Added Google OAuth config

## Testing Checklist

- [ ] Google Cloud Project created
- [ ] OAuth credentials obtained
- [ ] Client ID and Secret added to .env
- [ ] Frontend VITE_GOOGLE_CLIENT_ID set
- [ ] Backend running without errors
- [ ] Frontend loading Google Sign-In button
- [ ] Can click button without errors
- [ ] Can select Google account
- [ ] Token sent to backend successfully
- [ ] User created in database
- [ ] Tokens stored in localStorage
- [ ] Redirected to dashboard

---

**Status:** ✅ Ready for local testing
**Last Updated:** February 14, 2025
