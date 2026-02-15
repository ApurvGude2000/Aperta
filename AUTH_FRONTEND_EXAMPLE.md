# Frontend Authentication Integration - Examples

This guide shows how to integrate the Aperta authentication system into your frontend.

---

## React Example

### 1. Login Component

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/auth/login', {
        email,
        password
      });

      // Save tokens to localStorage
      localStorage.setItem('access_token', response.data.tokens.access_token);
      localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));

      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Aperta Login</h1>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      <p>Don't have an account? <a href="/signup">Sign up</a></p>
    </div>
  );
}

export default LoginPage;
```

### 2. Signup Component

```jsx
function SignupPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [company, setCompany] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/auth/register', {
        email,
        username,
        password,
        full_name: fullName,
        company
      });

      // Save tokens and redirect
      localStorage.setItem('access_token', response.data.tokens.access_token);
      localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));

      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <h1>Create Account</h1>
      <form onSubmit={handleSignup}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password (min 6 chars)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
        />
        <input
          type="text"
          placeholder="Company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Creating account...' : 'Sign up'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      <p>Already have an account? <a href="/login">Login</a></p>
    </div>
  );
}

export default SignupPage;
```

### 3. Protected Route Component

```jsx
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return <Navigate to="/login" />;
  }

  return children;
}

export default ProtectedRoute;
```

### 4. API Client with Token

```jsx
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000'
});

// Add token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://localhost:8000/auth/refresh', {
          refresh_token: refreshToken
        });

        localStorage.setItem('access_token', response.data.access_token);
        originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;

        return apiClient(originalRequest);
      } catch (err) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### 5. Audio Upload with Auth

```jsx
import apiClient from './apiClient';

function AudioUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post('/audio/process', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResult(response.data);
      alert('Audio uploaded successfully!');
    } catch (error) {
      alert('Upload failed: ' + error.response?.data?.detail);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h2>Upload Audio</h2>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept="audio/*"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <button type="submit" disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      {result && (
        <div>
          <h3>Upload Result</h3>
          <p>Conversation ID: {result.conversation_id}</p>
          <p>Speakers: {result.transcript.speaker_count}</p>
          <textarea readOnly value={result.transcript.formatted_transcript} />
        </div>
      )}
    </div>
  );
}

export default AudioUpload;
```

---

## Vue.js Example

### 1. Login Component (Vue 3)

```vue
<template>
  <div class="login-container">
    <h1>Aperta Login</h1>
    <form @submit.prevent="handleLogin">
      <input
        v-model="email"
        type="email"
        placeholder="Email"
        required
      />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <button :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

export default {
  name: 'LoginPage',
  setup() {
    const email = ref('');
    const password = ref('');
    const error = ref('');
    const loading = ref(false);

    const handleLogin = async () => {
      loading.value = true;
      error.value = '';

      try {
        const response = await axios.post('http://localhost:8000/auth/login', {
          email: email.value,
          password: password.value
        });

        localStorage.setItem('access_token', response.data.tokens.access_token);
        localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));

        window.location.href = '/dashboard';
      } catch (err) {
        error.value = err.response?.data?.detail || 'Login failed';
      } finally {
        loading.value = false;
      }
    };

    return {
      email,
      password,
      error,
      loading,
      handleLogin
    };
  }
};
</script>
```

---

## Vanilla JavaScript Example

### 1. Simple Login Form

```html
<!DOCTYPE html>
<html>
<head>
  <title>Aperta Login</title>
  <style>
    .login-container {
      max-width: 400px;
      margin: 50px auto;
      padding: 20px;
      border: 1px solid #ccc;
    }
    input { width: 100%; margin: 10px 0; padding: 10px; }
    button { width: 100%; padding: 10px; cursor: pointer; }
    .error { color: red; }
  </style>
</head>
<body>
  <div class="login-container">
    <h1>Aperta Login</h1>
    <form id="loginForm">
      <input type="email" id="email" placeholder="Email" required />
      <input type="password" id="password" placeholder="Password" required />
      <button type="submit">Login</button>
      <p id="error" class="error"></p>
    </form>
  </div>

  <script>
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
      e.preventDefault();

      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const errorDiv = document.getElementById('error');

      try {
        const response = await fetch('http://localhost:8000/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail);
        }

        const data = await response.json();

        // Save tokens
        localStorage.setItem('access_token', data.tokens.access_token);
        localStorage.setItem('refresh_token', data.tokens.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        // Redirect
        window.location.href = '/dashboard';
      } catch (error) {
        errorDiv.textContent = `Login failed: ${error.message}`;
      }
    });
  </script>
</body>
</html>
```

### 2. Making API Requests with Token

```javascript
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('access_token');

  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };

  const response = await fetch(url, {
    ...options,
    headers
  });

  if (response.status === 401) {
    // Token expired, try refreshing
    const newToken = await refreshToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      return fetch(url, { ...options, headers });
    } else {
      // Redirect to login
      window.location.href = '/login';
    }
  }

  return response;
}

async function refreshToken() {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await fetch('http://localhost:8000/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      return data.access_token;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }

  return null;
}
```

---

## Testing with Postman

### 1. Create Environment Variables

In Postman:
- `base_url`: `http://localhost:8000`
- `access_token`: (will be filled after login)
- `refresh_token`: (will be filled after login)

### 2. Register Request

```
POST {{base_url}}/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "username": "testuser",
  "password": "TestPassword123!",
  "full_name": "Test User",
  "company": "Test Corp"
}
```

**Test script** (saves tokens):
```javascript
if (pm.response.code === 201) {
  pm.environment.set("access_token", pm.response.json().tokens.access_token);
  pm.environment.set("refresh_token", pm.response.json().tokens.refresh_token);
}
```

### 3. Login Request

```
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "TestPassword123!"
}
```

### 4. Protected Request (with Token)

```
GET {{base_url}}/auth/me
Authorization: Bearer {{access_token}}
```

### 5. Upload Audio (with Auth)

```
POST {{base_url}}/audio/process
Authorization: Bearer {{access_token}}

(form-data)
file: <select your audio file>
```

---

## Common Issues

### "Invalid authorization header format"
Make sure you're sending: `Authorization: Bearer <token>`
Not: `Authorization: <token>`

### "Token expired"
Use the refresh token endpoint to get a new access token.

### "Email already registered"
The email is already in use. Try signing up with a different email.

### "Password must be at least 6 characters"
Increase your password length.

---

## Summary

✅ Authentication is now ready for frontend integration
✅ JWT tokens handle all authentication
✅ Examples for React, Vue, and Vanilla JS
✅ Ready for production with proper secret key

**Next:** Build your login/signup UI using these examples!
