import React from 'react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  glow?: boolean;
  onClick?: () => void;
  imageUrl?: string;
}

export function Logo({ size = 'md', glow = true, onClick, imageUrl }: LogoProps) {
  const sizeClasses = {
    sm: 'w-8 h-8 text-lg',
    md: 'w-10 h-10 text-2xl',
    lg: 'w-12 h-12 text-3xl',
  };

  const shadowClass = glow ? 'shadow-lg shadow-cyan-500/50' : '';

  // If an image URL is provided, use it
  if (imageUrl) {
    return (
      <button
        onClick={onClick}
        className={`rounded-full overflow-hidden flex items-center justify-center flex-shrink-0 transition-transform hover:scale-110 ${sizeClasses[size]} ${shadowClass}`}
      >
        <img src={imageUrl} alt="Agent-Echo Logo" className="w-full h-full object-cover" />
      </button>
    );
  }

  // Fallback: Gradient circle with emoji
  return (
    <button
      onClick={onClick}
      className={`rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center text-white font-bold transform transition-all hover:scale-110 ${sizeClasses[size]} ${shadowClass}`}
      title="Agent-Echo"
    >
      🤖
    </button>
  );
}
