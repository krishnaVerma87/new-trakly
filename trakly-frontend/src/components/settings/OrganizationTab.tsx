import { useState, useEffect, FormEvent } from 'react';
import { OrganizationResponse, OrganizationUpdate } from '@/types';
import { organizationsService } from '@/lib/services/organizations.service';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-hot-toast';

export const OrganizationTab = () => {
  const { user } = useAuth();
  const [org, setOrg] = useState<OrganizationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState<OrganizationUpdate>({
    name: '',
    description: '',
    is_active: true,
  });

  useEffect(() => {
    const loadOrganization = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const response = await organizationsService.getOrganization(user.organization_id);
        const orgData = response.data.data;
        setOrg(orgData);
        setFormData({
          name: orgData.name,
          description: orgData.description || '',
          is_active: orgData.is_active,
        });
      } catch (error) {
        console.error('Failed to load organization:', error);
        toast.error('Failed to load organization');
      } finally {
        setLoading(false);
      }
    };

    loadOrganization();
  }, [user]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!user || !org) return;

    if (!formData.name) {
      toast.error('Organization name is required');
      return;
    }

    try {
      setSaving(true);
      const response = await organizationsService.updateOrganization(user.organization_id, formData);
      const updatedOrg = response.data.data;
      setOrg(updatedOrg);
      toast.success('Organization updated successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update organization');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (org) {
      setFormData({
        name: org.name,
        description: org.description || '',
        is_active: org.is_active,
      });
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
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Organization Settings</h2>
        <p className="text-sm text-gray-600 mt-1">
          Manage your organization's information and settings
        </p>
      </div>

      <div className="bg-white rounded-lg shadow">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Organization Slug (readonly) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Organization Slug
            </label>
            <input
              type="text"
              value={org?.slug || ''}
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 cursor-not-allowed"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">
              This is your organization's unique identifier and cannot be changed
            </p>
          </div>

          {/* Organization Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Organization Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="My Organization"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Brief description of your organization..."
            />
          </div>

          {/* Active Status */}
          <div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Organization is active</span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-6">
              Inactive organizations cannot be accessed by any users
            </p>
          </div>

          {/* Metadata */}
          <div className="border-t border-gray-200 pt-4">
            <div className="text-sm text-gray-600 space-y-1">
              <p>
                <span className="font-medium">Created:</span>{' '}
                {org?.created_at ? new Date(org.created_at).toLocaleString() : 'N/A'}
              </p>
              <p>
                <span className="font-medium">Last Updated:</span>{' '}
                {org?.updated_at ? new Date(org.updated_at).toLocaleString() : 'N/A'}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              disabled={saving}
            >
              Reset
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
    </div>
  );
};
