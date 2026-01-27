import React, { useState, useEffect } from 'react';
import { LabelResponse } from '@/types';
import apiClient from '@/lib/api';
import toast from 'react-hot-toast';

interface LabelPickerProps {
  projectId: string;
  value: string[];
  onChange: (labelIds: string[]) => void;
  label?: string;
}

const PRESET_COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#14B8A6', // teal
  '#6366F1', // indigo
];

export const LabelPicker: React.FC<LabelPickerProps> = ({
  projectId,
  value,
  onChange,
  label = 'Labels',
}) => {
  const [labels, setLabels] = useState<LabelResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newLabelName, setNewLabelName] = useState('');
  const [newLabelColor, setNewLabelColor] = useState(PRESET_COLORS[0]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const fetchLabels = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get<LabelResponse[]>(
          `/projects/${projectId}/labels`
        );
        setLabels(response.data);
      } catch (error) {
        console.error('Failed to fetch labels:', error);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchLabels();
    }
  }, [projectId]);

  const toggleLabel = (labelId: string) => {
    if (value.includes(labelId)) {
      onChange(value.filter((id) => id !== labelId));
    } else {
      onChange([...value, labelId]);
    }
  };

  const handleCreateLabel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLabelName.trim()) {
      toast.error('Label name is required');
      return;
    }

    try {
      setCreating(true);
      const response = await apiClient.post<LabelResponse>(
        `/projects/${projectId}/labels`,
        {
          name: newLabelName.trim(),
          color: newLabelColor,
        }
      );

      const newLabel = response.data;
      setLabels([...labels, newLabel]);
      onChange([...value, newLabel.id]);
      setNewLabelName('');
      setNewLabelColor(PRESET_COLORS[0]);
      setShowCreateForm(false);
      toast.success('Label created successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create label');
    } finally {
      setCreating(false);
    }
  };

  const selectedLabels = labels.filter((label) => value.includes(label.id));

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        <button
          type="button"
          onClick={() => setShowDropdown(!showDropdown)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-left bg-white"
        >
          {loading ? (
            'Loading...'
          ) : selectedLabels.length > 0 ? (
            <div className="flex flex-wrap gap-1">
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
            </div>
          ) : (
            <span className="text-gray-500">Select labels...</span>
          )}
        </button>

        {showDropdown && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => {
                setShowDropdown(false);
                setShowCreateForm(false);
              }}
            />
            <div className="absolute z-20 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-80 overflow-hidden flex flex-col">
              {/* Create New Label Form */}
              {showCreateForm ? (
                <form onSubmit={handleCreateLabel} className="p-3 border-b border-gray-200">
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={newLabelName}
                      onChange={(e) => setNewLabelName(e.target.value)}
                      placeholder="Label name..."
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      autoFocus
                    />
                    <div className="flex gap-1 flex-wrap">
                      {PRESET_COLORS.map((color) => (
                        <button
                          key={color}
                          type="button"
                          onClick={() => setNewLabelColor(color)}
                          className={`w-6 h-6 rounded border-2 ${
                            newLabelColor === color ? 'border-gray-900' : 'border-transparent'
                          }`}
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="submit"
                        disabled={creating}
                        className="flex-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                      >
                        {creating ? 'Creating...' : 'Create'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowCreateForm(false);
                          setNewLabelName('');
                        }}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </form>
              ) : (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowCreateForm(true);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 border-b border-gray-200 flex items-center gap-2 font-medium"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create new label
                </button>
              )}

              {/* Existing Labels List */}
              <div className="overflow-y-auto flex-1">
                {labels.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-gray-500">
                    No labels yet. Create one above.
                  </div>
                ) : (
                  labels.map((label) => {
                    const isSelected = value.includes(label.id);
                    return (
                      <button
                        key={label.id}
                        type="button"
                        onClick={() => toggleLabel(label.id)}
                        className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => {}}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                        />
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
                    );
                  })
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
