import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardService } from '@/lib/services/dashboard.service';
import { DashboardStats, RecentIssueResponse } from '@/types';
import { DeveloperDashboard } from '@/components/dashboard/DeveloperDashboard';
import { ProjectManagerDashboard } from '@/components/dashboard/ProjectManagerDashboard';

const DashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentIssues, setRecentIssues] = useState<RecentIssueResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, issuesRes] = await Promise.all([
          dashboardService.getStatistics(),
          dashboardService.getRecentIssues(10),
        ]);
        setStats(statsRes.data);
        setRecentIssues(issuesRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Determine which dashboard to show based on user roles
  const getUserPrimaryRole = (): string | null => {
    if (!user || !user.roles || user.roles.length === 0) {
      return null;
    }

    // Priority order: org_admin > project_manager > developer > reporter > viewer
    const rolePriority = ['org_admin', 'project_manager', 'developer', 'reporter', 'viewer'];

    for (const priority of rolePriority) {
      if (user.roles.some(role => role.name && role.name.toLowerCase() === priority)) {
        return priority;
      }
    }

    return user.roles[0]?.name?.toLowerCase() || null;
  };

  const primaryRole = getUserPrimaryRole();

  // Show role-specific dashboard
  if (primaryRole === 'developer') {
    return <DeveloperDashboard />;
  }

  if (primaryRole === 'project_manager' || primaryRole === 'org_admin') {
    return <ProjectManagerDashboard />;
  }

  // Default dashboard for reporter/viewer or unknown roles
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-6">
          <div className="text-sm font-medium text-gray-600">Total Projects</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {stats?.projects.total || 0}
          </div>
        </div>

        <div className="card p-6">
          <div className="text-sm font-medium text-gray-600">Total Tasks</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {stats?.issues.total || 0}
          </div>
        </div>

        <div className="card p-6">
          <div className="text-sm font-medium text-gray-600">Open Tasks</div>
          <div className="text-3xl font-bold text-primary-600 mt-2">
            {stats?.issues.open || 0}
          </div>
        </div>

        <div className="card p-6">
          <div className="text-sm font-medium text-gray-600">Total Features</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {stats?.features.total || 0}
          </div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Tasks</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Task Key
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assignee
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentIssues.map((issue) => (
                <tr key={issue.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">
                    {issue.issue_key}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{issue.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {issue.issue_type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="badge bg-blue-100 text-blue-800">
                      {issue.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {issue.assignee_name || 'Unassigned'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
