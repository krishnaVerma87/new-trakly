import React, { useState, useEffect } from 'react';
import { ComponentResponse } from '@/types';
import { projectsService } from '@/lib/services/projects.service';

interface ComponentPickerProps {
  projectId: string;
  value?: string;
  onChange: (componentId: string | undefined) => void;
  label?: string;
  required?: boolean;
  placeholder?: string;
}

export const ComponentPicker: React.FC<ComponentPickerProps> = ({
  projectId,
  value,
  onChange,
  label = 'Component',
  required = false,
  placeholder = 'Select component...',
}) => {
  const [components, setComponents] = useState<ComponentResponse[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        setLoading(true);
        const response = await projectsService.listComponents(projectId);
        setComponents(response.data);
      } catch (error) {
        console.error('Failed to fetch components:', error);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchComponents();
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
        {components.map((component) => (
          <option key={component.id} value={component.id}>
            {component.name}
            {component.description && ` - ${component.description}`}
          </option>
        ))}
      </select>
    </div>
  );
};
