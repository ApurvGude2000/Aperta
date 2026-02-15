/**
 * ABOUTME: Google OAuth login component
 * ABOUTME: Sign up/login users with their Google account
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

declare global {
  interface Window {
    google: any;
  }
}

interface GoogleLoginProps {
  onSuccess?: (token: string) => void;
  onError?: (error: string) => void;
  isLoading?: boolean;
}

export function GoogleLogin({
  onSuccess,
  onError,
  isLoading = false,
}: GoogleLoginProps) {
  const [googleReady, setGoogleReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Initialize Google Sign-In
  useEffect(() => {
    const initializeGoogle = async () => {
      // Load Google Sign-In script
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;

      script.onload = () => {
        if (window.google?.accounts?.id) {
          // Initialize Google Sign-In
          window.google.accounts.id.initialize({
            client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
            callback: handleCredentialResponse,
            auto_select: false,
          });

          setGoogleReady(true);
        }
      };

      document.body.appendChild(script);
    };

    initializeGoogle();
  }, []);

  const handleCredentialResponse = async (response: any) => {
    try {
      setError(null);

      const idToken = response.credential;

      // Send token to backend
      const res = await fetch('/api/auth/google/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: idToken }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Login failed');
      }

      const data = await res.json();

      // Store tokens
      localStorage.setItem('access_token', data.tokens.access_token);
      localStorage.setItem('refresh_token', data.tokens.refresh_token);

      // Call onSuccess callback
      if (onSuccess) {
        onSuccess(data.tokens.access_token);
      }

      // Redirect to dashboard
      navigate('/');
    } catch (err: any) {
      const message = err.message || 'Google login failed';
      setError(message);
      if (onError) {
        onError(message);
      }
      console.error('Google login error:', err);
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {googleReady && (
        <div
          id="google-signin-button"
          data-type="standard"
          data-size="large"
          data-theme="outline"
          data-text="signin_with"
          data-shape="rectangular"
          data-logo_alignment="left"
          style={{ display: 'flex', justifyContent: 'center' }}
        />
      )}

      {!googleReady && (
        <div className="flex items-center justify-center p-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {isLoading && (
        <div className="text-center text-gray-500">Logging in...</div>
      )}
    </div>
  );
}

export default GoogleLogin;
