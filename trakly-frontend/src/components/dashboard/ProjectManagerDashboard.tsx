import { useEffect, useState } from 'react';
import { dashboardService } from '@/lib/services/dashboard.service';
import { ProjectManagerDashboardData } from '@/types';
import toast from 'react-hot-toast';

export const ProjectManagerDashboard = () => {
  const [data, setData] = useState<ProjectManagerDashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await dashboardService.getProjectManagerDashboard();
      setData(response.data);
    } catch (error: any) {
      toast.error('Failed to load dashboard');
      console.error('Error loading project manager dashboard:', error);
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
          <h1 className="text-3xl font-bold text-gray-900">Project Manager Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Team overview and sprint progress</p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="text-sm font-medium text-gray-600">Active Sprints</div>
          <div className="text-3xl font-bold text-blue-600 mt-2">
            {data.summary.active_sprint_count}
          </div>
          <div className="text-xs text-gray-500 mt-1">Currently running</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="text-sm font-medium text-gray-600">Team Members</div>
          <div className="text-3xl font-bold text-green-600 mt-2">
            {data.summary.team_members}
          </div>
          <div className="text-xs text-gray-500 mt-1">Active contributors</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
          <div className="text-sm font-medium text-gray-600">Pending Issues</div>
          <div className="text-3xl font-bold text-yellow-600 mt-2">
            {data.pending_issues}
          </div>
          <div className="text-xs text-gray-500 mt-1">Unassigned tasks</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <div className="text-sm font-medium text-gray-600">Blocked Issues</div>
          <div className="text-3xl font-bold text-red-600 mt-2">
            {data.blocked_issues}
          </div>
          <div className="text-xs text-gray-500 mt-1">Needs attention</div>
        </div>
      </div>

      {/* Active Sprints */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Active Sprints</h2>
        </div>
        <div className="p-6">
          {data.active_sprints.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              No active sprints at the moment
            </div>
          ) : (
            <div className="space-y-4">
              {data.active_sprints.map((sprint) => (
                <div
                  key={sprint.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => {
                    // Navigate to sprint board - you'll need to get the project ID
                    // navigate(`/projects/${projectId}/sprints/${sprint.id}/board`);
                  }}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{sprint.name}</h3>
                      {sprint.goal && (
                        <p className="text-sm text-gray-600 mt-1">{sprint.goal}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(sprint.start_date).toLocaleDateString()} -{' '}
                        {new Date(sprint.end_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">
                        {sprint.progress_percentage}%
                      </div>
                      <div className="text-xs text-gray-500">Complete</div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-3">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full transition-all"
                        style={{ width: `${sprint.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Issue Counts */}
                  <div className="flex items-center gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Total: </span>
                      <span className="font-semibold text-gray-900">{sprint.total_issues}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Completed: </span>
                      <span className="font-semibold text-green-600">{sprint.completed_issues}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Remaining: </span>
                      <span className="font-semibold text-orange-600">
                        {sprint.total_issues - sprint.completed_issues}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Team Workload */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Team Workload</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Team Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Active Issues
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Workload
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.team_workload.map((member) => {
                // Determine workload level
                let workloadClass = 'bg-green-100 text-green-800';
                let workloadText = 'Light';
                if (member.active_issues > 10) {
                  workloadClass = 'bg-red-100 text-red-800';
                  workloadText = 'Heavy';
                } else if (member.active_issues > 5) {
                  workloadClass = 'bg-yellow-100 text-yellow-800';
                  workloadText = 'Medium';
                }

                return (
                  <tr key={member.user_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-semibold text-sm">
                            {member.user_name
                              .split(' ')
                              .map((n) => n[0])
                              .join('')
                              .toUpperCase()
                              .slice(0, 2)}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{member.user_name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-2xl font-bold text-gray-900">{member.active_issues}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${workloadClass}`}>
                        {workloadText}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {data.team_workload.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              No team members with active tasks
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
