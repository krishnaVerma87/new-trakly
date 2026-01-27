import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

interface NotificationPreference {
  notification_type: string;
  in_app_enabled: boolean;
  email_enabled: boolean;
  email_digest: boolean;
  slack_enabled: boolean;
}

const NOTIFICATION_TYPES = [
  { value: 'issue_assigned', label: 'Issue Assigned', description: 'When an issue is assigned to you' },
  { value: 'issue_updated', label: 'Issue Updated', description: 'When an issue you\'re watching is updated' },
  { value: 'issue_commented', label: 'New Comment', description: 'When someone comments on your issue' },
  { value: 'issue_mentioned', label: 'Mentioned', description: 'When you\'re mentioned in a comment' },
  { value: 'sprint_started', label: 'Sprint Started', description: 'When a sprint you\'re part of starts' },
  { value: 'sprint_ending', label: 'Sprint Ending', description: 'Reminder before sprint ends' },
];

export const NotificationPreferences = () => {
  const [preferences, setPreferences] = useState<Record<string, NotificationPreference>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // const response = await notificationService.getPreferences();
      // setPreferences(response.data);

      // For now, initialize with defaults
      const defaultPrefs: Record<string, NotificationPreference> = {};
      NOTIFICATION_TYPES.forEach(type => {
        defaultPrefs[type.value] = {
          notification_type: type.value,
          in_app_enabled: true,
          email_enabled: true,
          email_digest: false,
          slack_enabled: false,
        };
      });
      setPreferences(defaultPrefs);
    } catch (error: any) {
      toast.error('Failed to load notification preferences');
      console.error('Error loading preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (notificationType: string, channel: string) => {
    setPreferences(prev => ({
      ...prev,
      [notificationType]: {
        ...prev[notificationType],
        [`${channel}_enabled`]: !prev[notificationType]?.[`${channel}_enabled` as keyof NotificationPreference],
      },
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      // TODO: Replace with actual API call
      // await notificationService.updatePreferences(preferences);
      toast.success('Notification preferences saved');
    } catch (error: any) {
      toast.error('Failed to save preferences');
      console.error('Error saving preferences:', error);
    } finally {
      setSaving(false);
    }
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
      <div>
        <h2 className="text-xl font-bold text-gray-900">Notification Preferences</h2>
        <p className="text-sm text-gray-500 mt-1">
          Manage how and when you receive notifications
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notification Type
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  In-App
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Slack
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {NOTIFICATION_TYPES.map((type) => {
                const pref = preferences[type.value];
                return (
                  <tr key={type.value} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{type.label}</div>
                        <div className="text-sm text-gray-500">{type.description}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <input
                        type="checkbox"
                        checked={pref?.in_app_enabled || false}
                        onChange={() => handleToggle(type.value, 'in_app')}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </td>
                    <td className="px-6 py-4 text-center">
                      <input
                        type="checkbox"
                        checked={pref?.email_enabled || false}
                        onChange={() => handleToggle(type.value, 'email')}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </td>
                    <td className="px-6 py-4 text-center">
                      <input
                        type="checkbox"
                        checked={pref?.slack_enabled || false}
                        onChange={() => handleToggle(type.value, 'slack')}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-blue-900">Email Digest</h3>
          <p className="text-sm text-blue-700 mt-1">
            Receive a daily summary of notifications instead of individual emails
          </p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            className="sr-only peer"
            onChange={() => {
              // Toggle email digest for all notification types
              setPreferences(prev => {
                const updated = { ...prev };
                Object.keys(updated).forEach(key => {
                  updated[key] = {
                    ...updated[key],
                    email_digest: !updated[key].email_digest,
                  };
                });
                return updated;
              });
            }}
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary"
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
};
