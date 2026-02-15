import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Logo } from '../Logo';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  logoImageUrl?: string;
}

const menuItems = [
  { icon: '🏠', label: 'Dashboard', path: '/dashboard' },
  { icon: '📅', label: 'Events', path: '/events' },
  { icon: '🧠', label: 'Knowledge Graph', path: '/knowledge-graph' },
  { icon: '📄', label: 'Transcripts', path: '/transcripts' },
  { icon: '📊', label: 'Analytics', path: '/analytics' },
  { icon: '⚙️', label: 'Settings', path: '/settings' },
];

export function Sidebar({ isOpen = true, logoImageUrl }: SidebarProps) {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  return (
    <aside
      className={`
        fixed md:static left-0 top-16 h-screen
        w-60 bg-slate-800/50 border-r border-cyan-500/20 backdrop-blur-lg
        transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        overflow-y-auto
      `}
    >
      {/* Logo Section at Top */}
      <div className="p-6 border-b border-cyan-500/20 flex items-center gap-3">
        <Logo size="sm" glow={true} imageUrl={logoImageUrl} />
        <span className="text-white font-display font-bold text-sm">Agent-Echo</span>
      </div>

      {/* Menu Items */}
      <div className="p-6 space-y-2">
        {menuItems.map((item, idx) => (
          <Link
            key={item.path}
            to={item.path}
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg
              transition-all duration-200
              ${
                isActive(item.path)
                  ? 'bg-cyan-500/10 text-cyan-400 border-l-4 border-cyan-400 font-medium'
                  : 'text-gray-300 hover:bg-slate-700/50 hover:text-cyan-300'
              }
            `}
            style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.05}s both`}}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-sm">{item.label}</span>
          </Link>
        ))}
      </div>
    </aside>
  );
}
