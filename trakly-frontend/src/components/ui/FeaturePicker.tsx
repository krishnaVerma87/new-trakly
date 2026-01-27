import React, { useState, useEffect } from 'react';
import { FeatureResponse } from '@/types';
import { featuresService } from '@/lib/services/features.service';

interface FeaturePickerProps {
  projectId: string;
  value?: string;
  onChange: (featureId: string | undefined) => void;
  label?: string;
  required?: boolean;
  placeholder?: string;
}

export const FeaturePicker: React.FC<FeaturePickerProps> = ({
  projectId,
  value,
  onChange,
  label = 'Feature',
  required = false,
  placeholder = 'Select feature...',
}) => {
  const [features, setFeatures] = useState<FeatureResponse[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchFeatures = async () => {
      try {
        setLoading(true);
        const response = await featuresService.listFeatures({ project_id: projectId });
        setFeatures(response.data);
      } catch (error) {
        console.error('Failed to fetch features:', error);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchFeatures();
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
        {features.map((feature) => (
          <option key={feature.id} value={feature.id}>
            {feature.feature_key}: {feature.title}
          </option>
        ))}
      </select>
    </div>
  );
};
