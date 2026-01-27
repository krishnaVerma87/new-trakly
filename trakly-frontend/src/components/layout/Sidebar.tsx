import { NavLink, useParams, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { projectsService } from '@/lib/services/projects.service';
import { ProjectResponse } from '@/types';

const Sidebar = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const location = useLocation();
  const isProjectRoute = location.pathname.startsWith('/projects/') && !!projectId;

  const [pinnedProjects, setPinnedProjects] = useState<ProjectResponse[]>([]);

  useEffect(() => {

    const fetchPins = async () => {
      try {
        const response = await projectsService.listPinnedProjects();
        setPinnedProjects(response.data);
      } catch (error) {
        console.error('Failed to fetch pinned projects', error);
      }
    };


    fetchPins();

    // Re-fetch on certain events or use a simple event bus/state management
    const handleRefreshPins = () => fetchPins();
    window.addEventListener('refresh-pinned-projects', handleRefreshPins);
    return () => window.removeEventListener('refresh-pinned-projects', handleRefreshPins);
  }, []);

  const globalNavItems = [
    { to: '/dashboard', label: 'Dashboard', icon: '📊' },
    { to: '/projects', label: 'Projects', icon: '📁' },
    { to: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  const projectNavItems = [
    { to: `/projects/${projectId}/issues`, label: 'Tasks', icon: '✅' },
    { to: `/projects/${projectId}/sprints`, label: 'Sprints', icon: '🏃' },
    { to: `/projects/${projectId}/features`, label: 'Features', icon: '🚀' },
    { to: `/projects/${projectId}/wiki`, label: 'Wiki', icon: '📚' },
    { to: `/projects/${projectId}/settings`, label: 'Project Settings', icon: '⚙️' },
  ];

  return (
    <div className="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 overflow-y-auto">
      <nav className="p-4 space-y-6">
        {/* Global Nav */}
        <div className="space-y-1">
          {globalNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/projects' && isProjectRoute}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive && !isProjectRoute
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        {/* Pinned Projects */}
        {pinnedProjects.length > 0 && (
          <div className="space-y-1">
            <div className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Pinned Projects
            </div>
            {pinnedProjects.map((project) => (
              <NavLink
                key={project.id}
                to={`/projects/${project.id}/issues`}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive && projectId === project.id
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <span className="w-5 h-5 flex items-center justify-center bg-gray-100 text-[10px] font-bold rounded">
                  {project.key}
                </span>
                <span className="truncate">{project.name}</span>
              </NavLink>
            ))}
          </div>
        )}

        {/* Project Nav */}
        {isProjectRoute && (
          <div className="space-y-1 pt-4 border-t border-gray-100">
            <div className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Current Project
            </div>
            {projectNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        )}
      </nav>
    </div>
  );
};


export default Sidebar;
