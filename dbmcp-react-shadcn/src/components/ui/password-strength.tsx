import React from 'react';

export type PasswordStrength = 'weak' | 'fair' | 'good' | 'strong';

interface PasswordStrengthIndicatorProps {
  password: string;
  className?: string;
}

export function PasswordStrengthIndicator({ password, className = '' }: PasswordStrengthIndicatorProps) {
  const getPasswordStrength = (password: string): PasswordStrength => {
    if (password.length < 6) return 'weak';
    
    let score = 0;
    
    // Length contribution
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    
    // Character variety contribution
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    // Determine strength level
    if (score <= 2) return 'weak';
    if (score <= 3) return 'fair';
    if (score <= 4) return 'good';
    return 'strong';
  };

  const getStrengthConfig = (strength: PasswordStrength) => {
    const configs = {
      weak: {
        width: '25%',
        color: 'bg-red-500',
        text: 'Weak password - Add more characters and complexity',
        textColor: 'text-red-600'
      },
      fair: {
        width: '50%',
        color: 'bg-orange-500',
        text: 'Fair password - Add more complexity',
        textColor: 'text-orange-600'
      },
      good: {
        width: '75%',
        color: 'bg-yellow-500',
        text: 'Good password - Consider adding special characters',
        textColor: 'text-yellow-600'
      },
      strong: {
        width: '100%',
        color: 'bg-green-500',
        text: 'Strong password - Excellent!',
        textColor: 'text-green-600'
      }
    };
    return configs[strength];
  };

  if (password.length === 0) {
    return (
      <div className={`mt-2 ${className}`}>
        <div className="h-1 bg-gray-200 rounded-full">
          <div className="h-1 bg-gray-300 rounded-full transition-all duration-300" style={{ width: '0%' }} />
        </div>
        <p className="text-xs text-gray-500 mt-1">Password strength will appear here</p>
      </div>
    );
  }

  const strength = getPasswordStrength(password);
  const config = getStrengthConfig(strength);

  return (
    <div className={`mt-2 ${className}`}>
      <div className="h-1 bg-gray-200 rounded-full">
        <div 
          className={`h-1 rounded-full transition-all duration-300 ${config.color}`}
          style={{ width: config.width }}
        />
      </div>
      <p className={`text-xs mt-1 ${config.textColor}`}>
        {config.text}
      </p>
    </div>
  );
}
