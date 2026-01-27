import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { issuesService } from '@/lib/services/issues.service';
import { sprintsService } from '@/lib/services/sprints.service';
import { IssueResponse, IssueFilterParams, IssueType, IssueStatus, Priority, SprintResponse } from '@/types';
import { IssueTypeIcon } from '@/components/issue/IssueTypeIcon';
import { IssueStatusBadge } from '@/components/issue/IssueStatusBadge';
import { IssuePriorityBadge } from '@/components/issue/IssuePriorityBadge';
import { CreateIssueDrawer } from '@/components/issue/CreateIssueDrawer';
import toast from 'react-hot-toast';

export const IssuesPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [issues, setIssues] = useState<IssueResponse[]>([]);
  const [sprints, setSprints] = useState<SprintResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDrawerOpen, setIsCreateDrawerOpen] = useState(false);
  const [filters, setFilters] = useState<IssueFilterParams>({
    project_id: projectId,
    status: searchParams.get('status') as IssueStatus | undefined,
    issue_type: searchParams.get('issue_type') as IssueType | undefined,
    priority: searchParams.get('priority') as Priority | undefined,
    search: searchParams.get('search') || undefined,
    sprint_id: searchParams.get('sprint_id') || undefined,
    include_backlog: searchParams.get('sprint_id') === 'backlog',
    exclude_completed_sprints: !searchParams.get('sprint_id') || searchParams.get('sprint_id') === 'active', // Default: show all active sprints + backlog
  });

  useEffect(() => {
    loadSprints();
  }, [projectId]);

  useEffect(() => {
    loadIssues();
  }, [filters]);

  const loadSprints = async () => {
    try {
      if (projectId) {
        const response = await sprintsService.list(projectId, false); // Don't include completed
        setSprints(response.data);
      }
    } catch (error: any) {
      console.error('Failed to load sprints:', error);
    }
  };

  const loadIssues = async () => {
    try {
      setLoading(true);
      const response = await issuesService.listIssues(filters);
      setIssues(response.data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: keyof IssueFilterParams, value: string | undefined) => {
    const newFilters: IssueFilterParams = { ...filters, [key]: value || undefined };

    // Special handling for sprint filter
    if (key === 'sprint_id') {
      if (value === 'active' || !value) {
        // All Active view (active/planned sprints + backlog)
        newFilters.sprint_id = undefined;
        newFilters.include_backlog = false;
        newFilters.exclude_completed_sprints = true;
      } else if (value === 'backlog') {
        // Backlog only view
        newFilters.sprint_id = undefined;
        newFilters.include_backlog = true;
        newFilters.exclude_completed_sprints = false;
      } else {
        // Specific sprint view
        newFilters.sprint_id = value;
        newFilters.include_backlog = false;
        newFilters.exclude_completed_sprints = false;
      }
    }

    setFilters(newFilters);

    // Update URL search params
    const newSearchParams = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v !== undefined && v !== null && k !== 'project_id' && k !== 'include_backlog' && k !== 'exclude_completed_sprints') {
        newSearchParams.set(k, String(v));
      }
    });
    setSearchParams(newSearchParams);
  };

  const handleCreateIssue = () => {
    setIsCreateDrawerOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Project Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => navigate(`/projects/${projectId}/issues`)}
            className="border-b-2 border-blue-500 py-4 px-1 text-sm font-medium text-blue-600"
          >
            Tasks
          </button>
          <button
            onClick={() => navigate(`/projects/${projectId}/sprints`)}
            className="border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
          >
            Sprints
          </button>
        </nav>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
          <p className="text-sm text-gray-600 mt-1">
            {issues.length} task{issues.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button
          onClick={handleCreateIssue}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Create Task
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <input
              type="text"
              placeholder="Search tasks..."
              value={filters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Sprint Filter */}
          <div>
            <select
              value={filters.exclude_completed_sprints ? 'active' : (filters.sprint_id || 'backlog')}
              onChange={(e) => handleFilterChange('sprint_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="active">All Active</option>
              <option value="backlog">Backlog Only</option>
              {sprints.map((sprint) => (
                <option key={sprint.id} value={sprint.id}>
                  {sprint.name} ({sprint.status})
                </option>
              ))}
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <select
              value={filters.issue_type || ''}
              onChange={(e) => handleFilterChange('issue_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="bug">Bug</option>
              <option value="task">Task</option>
              <option value="story">Story</option>
              <option value="improvement">Improvement</option>
              <option value="sub_task">Sub-task</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="new">New</option>
              <option value="in_progress">In Progress</option>
              <option value="review">Review</option>
              <option value="done">Done</option>
              <option value="closed">Closed</option>
              <option value="wont_fix">Won't Fix</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-4">
          {/* Priority Filter */}
          <div>
            <select
              value={filters.priority || ''}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Issues Table */}
      {issues.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
          <div className="mt-6">
            <button
              onClick={() => setIsCreateDrawerOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create Task
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assignee</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {issues.map((issue) => (
                <tr
                  key={issue.id}
                  onClick={() => navigate(`/projects/${projectId}/issues/${issue.issue_key}`)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                    {issue.issue_key}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="flex items-center gap-2">
                      <IssueTypeIcon type={issue.issue_type} className="w-4 h-4" />
                      {issue.title}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <IssueStatusBadge status={issue.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <IssuePriorityBadge priority={issue.priority} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {issue.assignee_id ? (
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-xs text-blue-700 font-medium">
                          {issue.assignee_id[0]}
                        </div>
                        {/* We rely on ID for now, ideally we fetch user name */}
                      </div>
                    ) : (
                      <span className="text-gray-400 italic">Unassigned</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <CreateIssueDrawer
        isOpen={isCreateDrawerOpen}
        onClose={() => setIsCreateDrawerOpen(false)}
        projectId={projectId!}
        onSuccess={() => {
          loadIssues();
          setIsCreateDrawerOpen(false);
        }}
      />
    </div>
  );
};
