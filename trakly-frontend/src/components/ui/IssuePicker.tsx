import React, { useState, useEffect } from 'react';
import { IssueResponse } from '@/types';
import { issuesService } from '@/lib/services/issues.service';

interface IssuePickerProps {
  projectId: string;
  value?: string;
  onChange: (issueId: string | undefined) => void;
  label?: string;
  required?: boolean;
  placeholder?: string;
  excludeIssueId?: string; // Exclude current issue from list
  filterType?: string; // Filter by issue type (e.g., only show parent-eligible issues)
}

export const IssuePicker: React.FC<IssuePickerProps> = ({
  projectId,
  value,
  onChange,
  label = 'Parent Issue',
  required = false,
  placeholder = 'Select issue...',
  excludeIssueId,
  filterType,
}) => {
  const [issues, setIssues] = useState<IssueResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchIssues = async () => {
      try {
        setLoading(true);
        const response = await issuesService.listIssues({
          project_id: projectId,
          limit: 100,
        });
        let filtered = response.data;

        // Exclude current issue
        if (excludeIssueId) {
          filtered = filtered.filter((issue) => issue.id !== excludeIssueId);
        }

        // Filter by type (e.g., sub_tasks can't be parents)
        if (filterType) {
          filtered = filtered.filter((issue) => issue.issue_type !== 'sub_task');
        }

        setIssues(filtered);
      } catch (error) {
        console.error('Failed to fetch issues:', error);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchIssues();
    }
  }, [projectId, excludeIssueId, filterType]);

  const filteredIssues = searchQuery
    ? issues.filter(
        (issue) =>
          issue.issue_key.toLowerCase().includes(searchQuery.toLowerCase()) ||
          issue.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : issues;

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="space-y-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by key or title..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          disabled={loading}
        />
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value || undefined)}
          required={required}
          disabled={loading}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          size={5}
        >
          <option value="">{loading ? 'Loading...' : placeholder}</option>
          {filteredIssues.slice(0, 50).map((issue) => (
            <option key={issue.id} value={issue.id}>
              {issue.issue_key}: {issue.title}
            </option>
          ))}
        </select>
        {filteredIssues.length > 50 && (
          <p className="text-xs text-gray-500">
            Showing first 50 results. Use search to narrow down.
          </p>
        )}
      </div>
    </div>
  );
};
