import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
}

export function Card({ children, className = '', hoverable = false, onClick }: CardProps) {
  return (
    <div
      className={`
        bg-white rounded-xl border border-[#E5E7EB] p-6 shadow-sm
        transition-all duration-300
        ${hoverable ? 'hover:shadow-lg hover:border-[#00C2FF] hover:scale-105 cursor-pointer' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick?: () => void;
}

export function FeatureCard({ icon, title, description, onClick }: FeatureCardProps) {
  return (
    <Card hoverable onClick={onClick} className="text-center">
      <div className="flex justify-center mb-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] flex items-center justify-center text-2xl">
          {icon}
        </div>
      </div>
      <h3 className="text-xl font-bold text-[#121417] mb-2">{title}</h3>
      <p className="text-sm text-[#6B7280]">{description}</p>
    </Card>
  );
}
