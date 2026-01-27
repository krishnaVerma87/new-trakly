import { useState, useEffect, FormEvent } from 'react';
import { Modal } from '@/components/ui/Modal';
import { RolePicker } from '@/components/ui/RolePicker';
import { usersService } from '@/lib/services/users.service';
import { UserWithRolesResponse } from '@/types';
import { toast } from 'react-hot-toast';
import { TIMEZONES } from '@/lib/utils/timezones';

interface EditUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  user: UserWithRolesResponse;
}

export const EditUserModal: React.FC<EditUserModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  user,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [showPasswordSection, setShowPasswordSection] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user.full_name,
    email: user.email,
    role_ids: user.roles.map(r => r.id),
    timezone: user.timezone,
    is_active: user.is_active,
    password: '',
  });

  // Update form data when user prop changes
  useEffect(() => {
    setFormData({
      full_name: user.full_name,
      email: user.email,
      role_ids: user.roles.map(r => r.id),
      timezone: user.timezone,
      is_active: user.is_active,
      password: '',
    });
    setShowPasswordSection(false);
  }, [user]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.full_name) {
      toast.error('Full name is required');
      return;
    }

    if (formData.role_ids.length === 0) {
      toast.error('Please select at least one role');
      return;
    }

    if (showPasswordSection && formData.password && formData.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    try {
      setSubmitting(true);

      // Only include password if it's being changed
      const updateData: any = {
        full_name: formData.full_name,
        role_ids: formData.role_ids,
        timezone: formData.timezone,
        is_active: formData.is_active,
      };

      if (showPasswordSection && formData.password) {
        updateData.password = formData.password;
      }

      await usersService.updateUser(user.id, updateData);
      toast.success('User updated successfully');
      onSuccess();
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update user');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit User">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Full Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Full Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        {/* Email (readonly) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={formData.email}
            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 cursor-not-allowed"
            disabled
          />
          <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
        </div>

        {/* Roles */}
        <RolePicker
          selectedRoleIds={formData.role_ids}
          onChange={(role_ids) => setFormData({ ...formData, role_ids })}
          required
        />

        {/* Timezone */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Timezone
          </label>
          <select
            value={formData.timezone}
            onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {TIMEZONES.map((tz) => (
              <option key={tz.value} value={tz.value}>
                {tz.label}
              </option>
            ))}
          </select>
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
            <span className="text-sm text-gray-700">Active</span>
          </label>
          <p className="text-xs text-gray-500 mt-1">Inactive users cannot access the system</p>
        </div>

        {/* Password Section */}
        <div className="border-t border-gray-200 pt-4">
          <button
            type="button"
            onClick={() => setShowPasswordSection(!showPasswordSection)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {showPasswordSection ? '- Hide password section' : '+ Change password'}
          </button>

          {showPasswordSection && (
            <div className="mt-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Min 8 characters"
                minLength={8}
              />
              <p className="text-xs text-gray-500 mt-1">Leave blank to keep current password</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
            disabled={submitting}
          >
            {submitting ? 'Updating...' : 'Update User'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
