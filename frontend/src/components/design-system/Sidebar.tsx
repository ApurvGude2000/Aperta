import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

const menuItems = [
  { icon: '🏠', label: 'Dashboard', path: '/dashboard' },
  { icon: '📅', label: 'Events', path: '/events' },
  { icon: '🧠', label: 'Knowledge Graph', path: '/knowledge-graph' },
  { icon: '💬', label: 'Conversations', path: '/old' },
  { icon: '📊', label: 'Analytics', path: '/analytics' },
  { icon: '⚙️', label: 'Settings', path: '/settings' },
];

export function Sidebar({ isOpen = true }: SidebarProps) {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard';
    }
    return location.pathname === path || (path !== '/' && location.pathname.startsWith(path));
  };

  return (
    <aside
      className={`
        fixed md:static left-0 top-16 h-screen
        w-60 bg-[#F5F7FA] border-r border-[#E5E7EB]
        transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        overflow-y-auto
      `}
    >
      <div className="p-6 space-y-2">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg
              transition-all duration-200
              ${
                isActive(item.path)
                  ? 'bg-white text-[#00C2FF] border-l-4 border-[#00C2FF] font-medium'
                  : 'text-[#6B7280] hover:bg-white'
              }
            `}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-sm">{item.label}</span>
          </Link>
        ))}
      </div>
    </aside>
  );
}
