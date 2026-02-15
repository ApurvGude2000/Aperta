import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface NavigationProps {
  showAuth?: boolean;
  isAuthenticated?: boolean;
  onLogout?: () => void;
}

export function Navigation({ showAuth = true, isAuthenticated = false, onLogout }: NavigationProps) {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const navLinks = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/events', label: 'Events', icon: '📅' },
    { path: '/knowledge-graph', label: 'Knowledge Graph', icon: '🧠' },
    { path: '/transcripts', label: 'Transcripts', icon: '📄' },
    { path: '/analytics', label: 'Analytics', icon: '📊' },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-[#E5E7EB] shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 font-display font-bold text-2xl">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] flex items-center justify-center text-white">
              🤖
            </div>
            <span className="text-[#121417]">Agent-Echo</span>
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
                      ? 'text-[#1F3C88] border-[#00C2FF]'
                      : 'text-[#6B7280] border-transparent hover:text-[#1F3C88]'
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
                  className="text-sm font-medium text-[#1F3C88] hover:text-[#00C2FF] transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] text-white text-sm font-medium rounded-lg hover:shadow-lg transition-all"
                >
                  Sign Up
                </Link>
              </>
            ) : isAuthenticated ? (
              <>
                <button
                  onClick={onLogout}
                  className="text-sm font-medium text-[#6B7280] hover:text-[#1F3C88] transition-colors"
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
