import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '@/lib/services/dashboard.service';
import { DeveloperDashboardData } from '@/types';
import { IssueTypeIcon } from '@/components/issue/IssueTypeIcon';
import { IssuePriorityBadge } from '@/components/issue/IssuePriorityBadge';
import { IssueStatusBadge } from '@/components/issue/IssueStatusBadge';
import toast from 'react-hot-toast';

export const DeveloperDashboard = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<DeveloperDashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await dashboardService.getDeveloperDashboard();
      setData(response.data);
    } catch (error: any) {
      toast.error('Failed to load dashboard');
      console.error('Error loading developer dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Your assigned tasks and progress</p>
        </div>
      </div>

      {/* Priority Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-gray-400">
          <div className="text-sm font-medium text-gray-600">Total Assigned</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {data.my_issues.total}
          </div>
          <div className="text-xs text-gray-500 mt-1">Active tasks</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <div className="text-sm font-medium text-gray-600">Critical Priority</div>
          <div className="text-3xl font-bold text-red-600 mt-2">
            {data.my_issues.critical_count}
          </div>
          <div className="text-xs text-gray-500 mt-1">Urgent attention needed</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
          <div className="text-sm font-medium text-gray-600">High Priority</div>
          <div className="text-3xl font-bold text-orange-600 mt-2">
            {data.my_issues.high_count}
          </div>
          <div className="text-xs text-gray-500 mt-1">Important tasks</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="text-sm font-medium text-gray-600">Time Tracked</div>
          <div className="text-3xl font-bold text-blue-600 mt-2">
            {data.time_tracking.total_spent_hours}h
          </div>
          <div className="text-xs text-gray-500 mt-1">
            of {data.time_tracking.total_estimated_hours}h estimated
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Priority */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Tasks by Priority</h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {Object.entries(data.my_issues.by_priority).map(([priority, count]) => (
                <div key={priority} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <IssuePriorityBadge priority={priority} />
                  </div>
                  <span className="text-2xl font-bold text-gray-900">{count}</span>
                </div>
              ))}
              {Object.keys(data.my_issues.by_priority).length === 0 && (
                <p className="text-gray-400 text-center py-4">No tasks assigned</p>
              )}
            </div>
          </div>
        </div>

        {/* By Status */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Tasks by Status</h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {Object.entries(data.my_issues.by_status).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <IssueStatusBadge status={status} />
                  <span className="text-2xl font-bold text-gray-900">{count}</span>
                </div>
              ))}
              {Object.keys(data.my_issues.by_status).length === 0 && (
                <p className="text-gray-400 text-center py-4">No tasks assigned</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* My Recent Tasks */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">My Assigned Tasks</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Key
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Project
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.recent_assigned.map((issue) => (
                <tr
                  key={issue.id}
                  onClick={() => {
                    // Extract project ID from issue key (assuming format like PROJ-123)
                    const match = issue.issue_key.match(/^([A-Z]+)-\d+$/);
                    if (match) {
                      // You'll need to navigate properly - this is a placeholder
                      navigate(`/projects/${issue.project_name}/issues/${issue.issue_key}`);
                    }
                  }}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-mono font-medium text-blue-600">
                      {issue.issue_key}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-md truncate">{issue.title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <IssueTypeIcon type={issue.issue_type} className="w-4 h-4" />
                      <span className="text-sm text-gray-500 capitalize">
                        {issue.issue_type.replace('_', ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <IssuePriorityBadge priority={issue.priority} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <IssueStatusBadge status={issue.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {issue.project_name || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.recent_assigned.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              No tasks assigned to you yet
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
