import React, { useState, useEffect } from 'react';
import { UserResponse } from '@/types';
import { projectsService } from '@/lib/services/projects.service';

interface UserPickerProps {
  projectId: string;
  value?: string;
  onChange: (userId: string | undefined) => void;
  label?: string;
  required?: boolean;
  placeholder?: string;
}

export const UserPicker: React.FC<UserPickerProps> = ({
  projectId,
  value,
  onChange,
  label = 'Assignee',
  required = false,
  placeholder = 'Select assignee...',
}) => {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await projectsService.listProjectMembers(projectId);
        setUsers(response.data.map((member) => member.user!));
      } catch (error) {
        console.error('Failed to fetch project members:', error);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchUsers();
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
        {users.map((user) => (
          <option key={user.id} value={user.id}>
            {user.full_name} ({user.email})
          </option>
        ))}
      </select>
    </div>
  );
};
