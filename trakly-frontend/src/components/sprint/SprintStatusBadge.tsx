import React from 'react';
import { SprintStatus } from '@/types';

interface SprintStatusBadgeProps {
  status: SprintStatus;
  className?: string;
}

export const SprintStatusBadge: React.FC<SprintStatusBadgeProps> = ({ status, className = '' }) => {
  const getStyles = () => {
    switch (status) {
      case 'planned':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getLabel = () => {
    switch (status) {
      case 'planned':
        return 'Planned';
      case 'active':
        return 'Active';
      case 'completed':
        return 'Completed';
      default:
        return status;
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'planned':
        return '○';
      case 'active':
        return '●';
      case 'completed':
        return '✓';
      default:
        return '';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStyles()} ${className}`}
    >
      <span className="mr-1">{getIcon()}</span>
      {getLabel()}
    </span>
  );
};
