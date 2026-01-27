import React from 'react';
import { Priority } from '@/types';

interface IssuePriorityBadgeProps {
  priority: Priority;
  className?: string;
}

export const IssuePriorityBadge: React.FC<IssuePriorityBadgeProps> = ({ priority, className = '' }) => {
  const getStyles = () => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getIcon = () => {
    switch (priority) {
      case 'critical':
        return '🔴';
      case 'high':
        return '🟠';
      case 'medium':
        return '🟡';
      case 'low':
        return '🟢';
      default:
        return '⚪';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStyles()} ${className}`}
    >
      <span className="mr-1">{getIcon()}</span>
      {priority.charAt(0).toUpperCase() + priority.slice(1)}
    </span>
  );
};
