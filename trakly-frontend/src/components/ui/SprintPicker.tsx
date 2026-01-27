import React, { useState, useEffect } from 'react';
import { SprintResponse } from '@/types';
import { sprintsService } from '@/lib/services/sprints.service';

interface SprintPickerProps {
  projectId: string;
  value?: string;
  onChange: (sprintId: string | undefined) => void;
  label?: string;
  required?: boolean;
  placeholder?: string;
}

export const SprintPicker: React.FC<SprintPickerProps> = ({
  projectId,
  value,
  onChange,
  label = 'Sprint',
  required = false,
  placeholder = 'Select sprint...',
}) => {
  const [sprints, setSprints] = useState<SprintResponse[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSprints = async () => {
      try {
        setLoading(true);
        const response = await sprintsService.list(projectId);
        // Sort by status (active first, then planned, then completed)
        const sorted = response.data.sort((a, b) => {
          const statusOrder: Record<string, number> = { active: 0, planned: 1, completed: 2 };
          return statusOrder[a.status] - statusOrder[b.status];
        });
        setSprints(sorted);
      } catch (error) {
        console.error('Failed to fetch sprints:', error);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchSprints();
    }
  }, [projectId]);

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value || undefined)}
        required={required}
        disabled={loading}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <option value="">{loading ? 'Loading...' : placeholder}</option>
        {sprints.map((sprint) => (
          <option key={sprint.id} value={sprint.id}>
            {sprint.name}
            {sprint.status === 'active' && ' (Active)'}
            {sprint.goal && ` - ${sprint.goal}`}
          </option>
        ))}
      </select>
    </div>
  );
};
