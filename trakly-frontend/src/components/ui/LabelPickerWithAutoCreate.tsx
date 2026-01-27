import React, { useState, useEffect, useRef } from 'react';
import { LabelResponse } from '@/types';
import apiClient from '@/lib/api';

interface LabelPickerWithAutoCreateProps {
  projectId: string;
  value: string[];
  onChange: (labelIds: string[]) => void;
  onPendingLabelsChange?: (pendingLabels: string[]) => void;
  label?: string;
}

// Preset colors for label creation (currently unused, reserved for future use)
// const PRESET_COLORS = [
//   '#3B82F6', // blue
//   '#10B981', // green
//   '#F59E0B', // amber
//   '#EF4444', // red
//   '#8B5CF6', // purple
//   '#EC4899', // pink
//   '#14B8A6', // teal
//   '#6366F1', // indigo
// ];

export const LabelPickerWithAutoCreate: React.FC<LabelPickerWithAutoCreateProps> = ({
  projectId,
  value,
  onChange,
  onPendingLabelsChange,
  label = 'Labels',
}) => {
  const [labels, setLabels] = useState<LabelResponse[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [pendingLabels, setPendingLabels] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchLabels = async () => {
      try {
        const response = await apiClient.get<LabelResponse[]>(
          `/projects/${projectId}/labels`
        );
        setLabels(response.data);
      } catch (error) {
        console.error('Failed to fetch labels:', error);
      }
    };

    if (projectId) {
      fetchLabels();
    }
  }, [projectId]);

  useEffect(() => {
    if (onPendingLabelsChange) {
      onPendingLabelsChange(pendingLabels);
    }
  }, [pendingLabels, onPendingLabelsChange]);

  const toggleLabel = (labelId: string) => {
    if (value.includes(labelId)) {
      onChange(value.filter((id) => id !== labelId));
    } else {
      onChange([...value, labelId]);
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const labelName = inputValue.trim();
      if (labelName) {
        // Check if label already exists
        const existingLabel = labels.find(
          (l) => l.name.toLowerCase() === labelName.toLowerCase()
        );

        if (existingLabel) {
          // Select existing label
          if (!value.includes(existingLabel.id)) {
            onChange([...value, existingLabel.id]);
          }
        } else {
          // Add to pending labels if not already there
          if (!pendingLabels.includes(labelName)) {
            setPendingLabels([...pendingLabels, labelName]);
          }
        }
        setInputValue('');
      }
    } else if (e.key === 'Backspace' && inputValue === '' && pendingLabels.length > 0) {
      // Remove last pending label on backspace when input is empty
      setPendingLabels(pendingLabels.slice(0, -1));
    }
  };

  const removePendingLabel = (labelName: string) => {
    setPendingLabels(pendingLabels.filter((l) => l !== labelName));
  };

  const selectedLabels = labels.filter((label) => value.includes(label.id));

  const filteredLabels = labels.filter(
    (label) =>
      !value.includes(label.id) &&
      label.name.toLowerCase().includes(inputValue.toLowerCase())
  );

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        <div
          className="w-full min-h-[42px] px-3 py-2 border border-gray-300 rounded-md focus-within:ring-2 focus-within:ring-blue-500 bg-white cursor-text"
          onClick={() => {
            inputRef.current?.focus();
            setShowDropdown(true);
          }}
        >
          <div className="flex flex-wrap gap-1 items-center">
            {/* Selected existing labels */}
            {selectedLabels.map((label) => (
              <span
                key={label.id}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                style={{
                  backgroundColor: label.color + '20',
                  color: label.color,
                  border: `1px solid ${label.color}`,
                }}
              >
                {label.name}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleLabel(label.id);
                  }}
                  className="ml-1 hover:text-red-600"
                >
                  ×
                </button>
              </span>
            ))}

            {/* Pending labels (to be created) */}
            {pendingLabels.map((labelName) => (
              <span
                key={labelName}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-dashed border-gray-400"
              >
                {labelName} (new)
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removePendingLabel(labelName);
                  }}
                  className="ml-1 hover:text-red-600"
                >
                  ×
                </button>
              </span>
            ))}

            {/* Input field */}
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleInputKeyDown}
              onFocus={() => setShowDropdown(true)}
              placeholder={
                selectedLabels.length === 0 && pendingLabels.length === 0
                  ? 'Type label name and press Enter...'
                  : ''
              }
              className="flex-1 min-w-[120px] outline-none text-sm bg-transparent"
            />
          </div>
        </div>

        {/* Dropdown suggestions */}
        {showDropdown && (inputValue || filteredLabels.length > 0) && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setShowDropdown(false)}
            />
            <div className="absolute z-20 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
              {filteredLabels.length > 0 ? (
                filteredLabels.map((label) => (
                  <button
                    key={label.id}
                    type="button"
                    onClick={() => {
                      toggleLabel(label.id);
                      setInputValue('');
                      setShowDropdown(false);
                    }}
                    className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                  >
                    <span
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                      style={{
                        backgroundColor: label.color + '20',
                        color: label.color,
                        border: `1px solid ${label.color}`,
                      }}
                    >
                      {label.name}
                    </span>
                    {label.description && (
                      <span className="text-xs text-gray-500 truncate">
                        {label.description}
                      </span>
                    )}
                  </button>
                ))
              ) : inputValue ? (
                <div className="px-3 py-2 text-sm text-gray-500">
                  Press Enter to create "{inputValue}"
                </div>
              ) : null}
            </div>
          </>
        )}
      </div>
      <p className="text-xs text-gray-500 mt-1">
        Type label names and press Enter. New labels will be created automatically.
      </p>
    </div>
  );
};
