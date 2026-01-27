import React from 'react';
import { Severity } from '@/types';

interface IssueSeverityBadgeProps {
  severity: Severity;
  className?: string;
}

export const IssueSeverityBadge: React.FC<IssueSeverityBadgeProps> = ({ severity, className = '' }) => {
  const getStyles = () => {
    switch (severity) {
      case 'blocker':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'critical':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'major':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'minor':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'trivial':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStyles()} ${className}`}
    >
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </span>
  );
};
