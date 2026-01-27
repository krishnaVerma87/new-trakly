import { useState, useEffect, FormEvent } from 'react';
import { organizationsService } from '@/lib/services/organizations.service';
import { notificationsService } from '@/lib/services/notifications.service';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-hot-toast';

interface IntegrationSettings {
  slack_webhook_url?: string;
  slack_enabled?: boolean;
}

export const IntegrationsTab = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingSlack, setTestingSlack] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);
  const [testEmailAddress, setTestEmailAddress] = useState('');
  const [settings, setSettings] = useState<IntegrationSettings>({
    slack_webhook_url: '',
    slack_enabled: false,
  });

  useEffect(() => {
    const loadSettings = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const response = await organizationsService.getOrganization(user.organization_id);
        const orgData = response.data.data;

        // Parse settings JSON if it exists
        if (orgData.settings) {
          try {
            const parsedSettings = typeof orgData.settings === 'string'
              ? JSON.parse(orgData.settings)
              : orgData.settings;
            setSettings({
              slack_webhook_url: parsedSettings.slack_webhook_url || '',
              slack_enabled: parsedSettings.slack_enabled || false,
            });
          } catch (e) {
            console.error('Failed to parse settings:', e);
          }
        }
      } catch (error) {
        console.error('Failed to load organization:', error);
        toast.error('Failed to load integration settings');
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, [user]);

  const handleSaveSlack = async (e: FormEvent) => {
    e.preventDefault();

    if (!user) return;

    try {
      setSaving(true);

      // Validate webhook URL format
      if (settings.slack_enabled && settings.slack_webhook_url) {
        if (!settings.slack_webhook_url.startsWith('https://hooks.slack.com/')) {
          toast.error('Invalid Slack webhook URL. Must start with https://hooks.slack.com/');
          return;
        }
      }

      // Save settings to organization
      const settingsJson = JSON.stringify({
        slack_webhook_url: settings.slack_webhook_url,
        slack_enabled: settings.slack_enabled,
      });

      await organizationsService.updateOrganization(user.organization_id, {
        settings: settingsJson,
      } as any);

      toast.success('Slack integration settings saved');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save Slack settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestSlack = async () => {
    if (!settings.slack_webhook_url) {
      toast.error('Please enter a Slack webhook URL first');
      return;
    }

    try {
      setTestingSlack(true);
      await notificationsService.testSlackNotification(settings.slack_webhook_url);
      toast.success('Test notification sent to Slack! Check your channel.');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send test notification');
    } finally {
      setTestingSlack(false);
    }
  };

  const handleTestEmail = async () => {
    const emailToTest = testEmailAddress || user?.email;

    if (!emailToTest) {
      toast.error('Please enter an email address');
      return;
    }

    try {
      setTestingEmail(true);
      await notificationsService.testEmailNotification(emailToTest);
      toast.success(`Test email sent to ${emailToTest}! Check your inbox.`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send test email');
    } finally {
      setTestingEmail(false);
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
        <h2 className="text-xl font-semibold text-gray-900">Integrations</h2>
        <p className="text-sm text-gray-600 mt-1">
          Connect Trakly with external services for notifications and automation
        </p>
      </div>

      {/* Slack Integration */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">Slack</h3>
                <p className="text-sm text-gray-500">Send notifications to Slack channels</p>
              </div>
            </div>
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.slack_enabled}
                  onChange={(e) => setSettings({ ...settings, slack_enabled: e.target.checked })}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Enabled</span>
              </label>
            </div>
          </div>
        </div>

        <form onSubmit={handleSaveSlack} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Webhook URL
            </label>
            <input
              type="url"
              value={settings.slack_webhook_url}
              onChange={(e) => setSettings({ ...settings, slack_webhook_url: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
            />
            <p className="text-xs text-gray-500 mt-1">
              Create a webhook URL in your Slack workspace settings{' '}
              <a
                href="https://api.slack.com/messaging/webhooks"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                Learn more
              </a>
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-900 mb-2">How to set up Slack notifications:</h4>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Go to your Slack workspace settings</li>
              <li>Navigate to "Incoming Webhooks" under Apps & Integrations</li>
              <li>Create a new webhook and select the channel for notifications</li>
              <li>Copy the webhook URL and paste it above</li>
              <li>Enable the integration and save</li>
            </ol>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleTestSlack}
              className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-300 rounded-md hover:bg-blue-100 disabled:opacity-50"
              disabled={!settings.slack_webhook_url || testingSlack}
            >
              {testingSlack ? 'Sending Test...' : 'Send Test Notification'}
            </button>

            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>

      {/* Email Integration */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">Email Notifications</h3>
                <p className="text-sm text-gray-500">SMTP email notifications</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <span className="w-2 h-2 mr-1.5 rounded-full bg-green-400"></span>
                Configured
              </span>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900 font-medium mb-2">SMTP Configuration</p>
            <p className="text-sm text-blue-800">
              Email notifications are configured via environment variables. Contact your system administrator to update SMTP settings.
            </p>
            <div className="mt-3 space-y-1 text-xs text-blue-700">
              <p><strong>Configured via:</strong> .env file (EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, etc.)</p>
            </div>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Supported notification types:</p>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside ml-2">
              <li>Issue assignments</li>
              <li>Status changes</li>
              <li>Comments and mentions</li>
              <li>Sprint reminders</li>
              <li>Welcome emails for new users</li>
            </ul>
          </div>

          <div className="pt-4 border-t border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-2">Test Email Notification</p>
            <div className="flex items-center space-x-3">
              <input
                type="email"
                value={testEmailAddress}
                onChange={(e) => setTestEmailAddress(e.target.value)}
                placeholder={user?.email || "Enter email address"}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              />
              <button
                type="button"
                onClick={handleTestEmail}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-green-300"
                disabled={testingEmail}
              >
                {testingEmail ? 'Sending...' : 'Send Test Email'}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Leave empty to send to your email ({user?.email})
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
