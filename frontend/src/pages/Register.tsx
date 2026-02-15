import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/design-system/Button';
import { Card } from '../components/design-system/Card';
import { api } from '../api/client';

export function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    company: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.register(formData);

      // Store tokens in localStorage
      localStorage.setItem('auth_token', response.tokens.access_token);
      localStorage.setItem('refresh_token', response.tokens.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#F5F7FA] flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-3 font-display font-bold text-2xl">
            <img
              src="/TH_logo.png"
              alt="Aperta Logo"
              className="w-12 h-12 rounded-full object-cover"
            />
            <span className="text-[#121417]">Aperta</span>
          </Link>
        </div>

        <Card className="p-8">
          <h1 className="text-2xl font-bold text-[#121417] mb-2">Create your account</h1>
          <p className="text-[#6B7280] mb-6">Start networking smarter today</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-[#121417] mb-1">
                Email *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-[#E5E7EB] rounded-lg focus:ring-2 focus:ring-[#1F3C88] focus:border-transparent"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-[#121417] mb-1">
                Username *
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-[#E5E7EB] rounded-lg focus:ring-2 focus:ring-[#1F3C88] focus:border-transparent"
                placeholder="johndoe"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-[#121417] mb-1">
                Password *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-[#E5E7EB] rounded-lg focus:ring-2 focus:ring-[#1F3C88] focus:border-transparent"
                placeholder="••••••••"
                required
                minLength={6}
              />
              <p className="text-xs text-[#6B7280] mt-1">At least 6 characters</p>
            </div>

            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-[#121417] mb-1">
                Full Name
              </label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                value={formData.full_name}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-[#E5E7EB] rounded-lg focus:ring-2 focus:ring-[#1F3C88] focus:border-transparent"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="company" className="block text-sm font-medium text-[#121417] mb-1">
                Company
              </label>
              <input
                id="company"
                name="company"
                type="text"
                value={formData.company}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-[#E5E7EB] rounded-lg focus:ring-2 focus:ring-[#1F3C88] focus:border-transparent"
                placeholder="Acme Inc."
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Create account'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#6B7280]">
              Already have an account?{' '}
              <Link to="/login" className="text-[#1F3C88] font-medium hover:text-[#00C2FF]">
                Sign in
              </Link>
            </p>
          </div>
        </Card>

        <div className="mt-4 text-center">
          <Link to="/" className="text-sm text-[#6B7280] hover:text-[#1F3C88]">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
