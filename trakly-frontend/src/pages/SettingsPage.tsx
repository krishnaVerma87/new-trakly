// import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { isAdmin } from '@/lib/utils/roles';

// Tab components
import { UsersTab } from '@/components/settings/UsersTab';
import { RolesTab } from '@/components/settings/RolesTab';
import { WorkflowsTab } from '@/components/settings/WorkflowsTab';
import { OrganizationTab } from '@/components/settings/OrganizationTab';
import { IntegrationsTab } from '@/components/settings/IntegrationsTab';
import { ProfileTab } from '@/components/settings/ProfileTab';

interface TabConfig {
  id: string;
  label: string;
  icon: string;
  requiresAdmin: boolean;
  component: React.ComponentType | null;
}

const SettingsPage = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const adminUser = isAdmin(user);

  // Define all tabs
  const allTabs: TabConfig[] = [
    { id: 'users', label: 'Users', icon: '👥', requiresAdmin: true, component: UsersTab },
    { id: 'roles', label: 'Roles', icon: '🔐', requiresAdmin: true, component: RolesTab },
    { id: 'workflows', label: 'Workflows', icon: '📋', requiresAdmin: true, component: WorkflowsTab },
    { id: 'organization', label: 'Organization', icon: '🏢', requiresAdmin: true, component: OrganizationTab },
    { id: 'integrations', label: 'Integrations', icon: '🔌', requiresAdmin: true, component: IntegrationsTab },
    { id: 'profile', label: 'Profile', icon: '👤', requiresAdmin: false, component: ProfileTab },
    { id: 'preferences', label: 'Preferences', icon: '⚙️', requiresAdmin: false, component: null },
  ];

  // Filter tabs based on user role
  const availableTabs = allTabs.filter(tab => !tab.requiresAdmin || adminUser);

  // Get active tab from URL query param or default
  const defaultTab = adminUser ? 'users' : 'profile';
  const activeTabId = searchParams.get('tab') || defaultTab;
  const activeTab = availableTabs.find(t => t.id === activeTabId) || availableTabs[0];

  const setActiveTab = (tabId: string) => {
    setSearchParams({ tab: tabId });
  };

  const ActiveComponent = activeTab.component;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-600 mt-1">
          Manage your account, organization, and preferences
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {availableTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                border-b-2 py-4 px-1 text-sm font-medium transition-colors
                ${activeTab.id === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {ActiveComponent ? (
          <ActiveComponent />
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 text-6xl mb-4">{activeTab.icon}</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {activeTab.label}
            </h3>
            <p className="text-gray-500">
              This section is coming soon...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;
