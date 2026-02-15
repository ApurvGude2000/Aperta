import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Logo } from '../components/Logo';
import { Button } from '../components/design-system/Button';

export function Signup() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    setLoading(true);
    // Simulate signup
    setTimeout(() => {
      setLoading(false);
      navigate('/dashboard');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-40 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="lg" glow={true} />
          </div>
          <h1 className="font-display text-4xl font-bold text-white mb-2">Get Started</h1>
          <p className="text-slate-800">Join Agent-Echo today</p>
        </div>

        {/* Signup Card */}
        <div className="premium-card rounded-2xl p-12 border-2 border-cyan-500/20 backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name Field */}
            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg bg-slate-800/80 border border-cyan-500/40 text-white placeholder-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500  transition-all"
                placeholder="John Doe"
                required
              />
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg bg-slate-800/80 border border-cyan-500/40 text-white placeholder-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500  transition-all"
                placeholder="you@example.com"
                required
              />
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg bg-slate-800/80 border border-cyan-500/40 text-white placeholder-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500  transition-all"
                placeholder="••••••••"
                required
              />
            </div>

            {/* Confirm Password Field */}
            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg bg-slate-800/80 border border-cyan-500/40 text-white placeholder-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500  transition-all"
                placeholder="••••••••"
                required
              />
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="terms"
                className="mt-1 w-4 h-4 rounded border-gray-600 text-cyan-500 focus:ring-2 focus:ring-cyan-500"
                required
              />
              <label htmlFor="terms" className="text-sm text-black">
                I agree to the{' '}
                <Link to="#" className="text-cyan-400 hover:text-cyan-300">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="#" className="text-cyan-400 hover:text-cyan-300">
                  Privacy Policy
                </Link>
              </label>
            </div>

            {/* Sign Up Button */}
            <Button
              className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold py-3 shadow-lg shadow-cyan-500/50 transform hover:scale-105"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-slate-800/80 text-black">Or sign up with</span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="space-y-3">
            <button className="w-full px-4 py-3 rounded-lg border border-gray-600 text-black font-medium hover:bg-slate-700/50 transition-all flex items-center justify-center gap-2">
              <span>🔵</span> Google
            </button>
            <button className="w-full px-4 py-3 rounded-lg border border-gray-600 text-black font-medium hover:bg-slate-700/50 transition-all flex items-center justify-center gap-2">
              <span>🍎</span> Apple
            </button>
          </div>

          {/* Login Link */}
          <p className="text-center text-black mt-8">
            Already have an account?{' '}
            <Link to="/login" className="text-cyan-400 hover:text-cyan-300 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
