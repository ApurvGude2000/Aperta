import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: React.ReactNode;
  isLoading?: boolean;
  icon?: React.ReactNode;
}

const variantStyles = {
  primary: 'bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] text-white hover:shadow-lg hover:scale-105 active:scale-100',
  secondary: 'bg-transparent border-2 border-[#1F3C88] text-[#1F3C88] hover:bg-[#1F3C88] hover:text-white',
  ghost: 'bg-transparent text-[#6B7280] hover:bg-[#F5F7FA]',
};

const sizeStyles = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-6 py-3 text-base',
  lg: 'px-8 py-4 text-lg',
};

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  isLoading,
  icon,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`
        inline-flex items-center gap-2 rounded-lg font-medium
        transition-all duration-300 ease-in-out
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="animate-spin">⌛</span>
      ) : icon ? (
        icon
      ) : null}
      {children}
    </button>
  );
}
