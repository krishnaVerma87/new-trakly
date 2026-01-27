import React from 'react';
import { SprintResponse } from '@/types';
import { SprintStatusBadge } from './SprintStatusBadge';
import { useNavigate } from 'react-router-dom';

interface SprintCardProps {
  sprint: SprintResponse;
  projectId: string;
  onEdit?: (sprint: SprintResponse) => void;
  onDelete?: (sprintId: string) => void;
}

export const SprintCard: React.FC<SprintCardProps> = ({
  sprint,
  projectId,
  onEdit,
  onDelete,
}) => {
  const navigate = useNavigate();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getProgressPercentage = () => {
    if (sprint.issue_count === 0) return 0;
    return Math.round((sprint.completed_issue_count / sprint.issue_count) * 100);
  };

  const handleCardClick = () => {
    navigate(`/projects/${projectId}/sprints/${sprint.id}/board`);
  };

  return (
    <div
      onClick={handleCardClick}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200"
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{sprint.name}</h3>
            <p className="text-sm text-gray-600">
              {formatDate(sprint.start_date)} - {formatDate(sprint.end_date)}
            </p>
          </div>
          <SprintStatusBadge status={sprint.status} />
        </div>

        {/* Goal */}
        {sprint.goal && (
          <p className="text-sm text-gray-700 mb-4 line-clamp-2">{sprint.goal}</p>
        )}

        {/* Progress */}
        <div className="mb-3">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-gray-600">Progress</span>
            <span className="font-medium text-gray-900">
              {sprint.completed_issue_count}/{sprint.issue_count} issues
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                sprint.status === 'completed'
                  ? 'bg-blue-600'
                  : sprint.status === 'active'
                  ? 'bg-green-600'
                  : 'bg-gray-400'
              }`}
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3 border-t">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit?.(sprint);
            }}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Edit
          </button>
          <span className="text-gray-300">|</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/projects/${projectId}/sprints/${sprint.id}/board`);
            }}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View Board
          </button>
          {sprint.status !== 'completed' && (
            <>
              <span className="text-gray-300">|</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete?.(sprint.id);
                }}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
              >
                Delete
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
