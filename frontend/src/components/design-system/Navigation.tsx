import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Logo } from '../Logo';

interface NavigationProps {
  showAuth?: boolean;
  isAuthenticated?: boolean;
  onLogout?: () => void;
  logoImageUrl?: string;
}

export function Navigation({ showAuth = true, isAuthenticated = false, onLogout, logoImageUrl }: NavigationProps) {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: '🏠' },
    { path: '/events', label: 'Events', icon: '📅' },
    { path: '/knowledge-graph', label: 'Knowledge Graph', icon: '🧠' },
    { path: '/transcripts', label: 'Transcripts', icon: '📄' },
    { path: '/analytics', label: 'Analytics', icon: '📊' },
  ];

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-lg bg-slate-900/50 border-b border-cyan-500/20">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo with Brand Name */}
          <Link to="/" className="flex items-center gap-3 font-display font-bold text-2xl hover:opacity-80 transition-opacity">
            <Logo size="md" glow={true} imageUrl={logoImageUrl} />
            <span className="text-white neon-text">Agent-Echo</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`
                  text-sm font-medium transition-colors
                  pb-2 border-b-2
                  ${
                    isActive(link.path)
                      ? 'text-cyan-400 border-cyan-400'
                      : 'text-gray-300 border-transparent hover:text-cyan-400'
                  }
                `}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Auth Section */}
          <div className="flex items-center gap-4">
            {showAuth && !isAuthenticated ? (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white text-sm font-bold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all transform hover:scale-105"
                >
                  Sign Up
                </Link>
              </>
            ) : isAuthenticated ? (
              <>
                <Link
                  to="/settings"
                  className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors"
                >
                  Settings
                </Link>
                <button
                  onClick={onLogout}
                  className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors"
                >
                  Logout
                </button>
              </>
            ) : null}
          </div>
        </div>
      </div>
    </nav>
  );
}
