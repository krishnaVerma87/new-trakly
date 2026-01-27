import { useState, useEffect } from 'react';
import { UserWithRolesResponse } from '@/types';
import { usersService } from '@/lib/services/users.service';
import { UserAvatar } from '@/components/ui/UserAvatar';
import { RoleBadge } from './RoleBadge';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { InviteUserModal } from './InviteUserModal';
import { BulkInviteUsersModal } from './BulkInviteUsersModal';
import { EditUserModal } from './EditUserModal';
import { toast } from 'react-hot-toast';

export const UsersTab = () => {
  const [users, setUsers] = useState<UserWithRolesResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeOnly, setActiveOnly] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showBulkInviteModal, setShowBulkInviteModal] = useState(false);
  const [editingUser, setEditingUser] = useState<UserWithRolesResponse | null>(null);
  const [deactivatingUser, setDeactivatingUser] = useState<UserWithRolesResponse | null>(null);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await usersService.listUsers({ active_only: activeOnly });
      setUsers(response.data || []);
    } catch (error) {
      console.error('Failed to load users:', error);
      toast.error('Failed to load users');
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [activeOnly]);

  const handleToggleActive = async (user: UserWithRolesResponse) => {
    try {
      await usersService.updateUser(user.id, { is_active: !user.is_active });
      toast.success(user.is_active ? 'User deactivated' : 'User activated');
      loadUsers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update user');
    }
  };

  // Filter users by search query
  const filteredUsers = (users || []).filter(user => {
    const query = searchQuery.toLowerCase();
    return (
      user.full_name?.toLowerCase().includes(query) ||
      user.email?.toLowerCase().includes(query)
    );
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Users</h2>
          <p className="text-sm text-gray-600 mt-1">
            Manage users and their roles in your organization
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowBulkInviteModal(true)}
            className="px-4 py-2 bg-white text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50"
          >
            Bulk Invite
          </button>
          <button
            onClick={() => setShowInviteModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Invite User
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Active only</span>
        </label>
      </div>

      {/* Users Table */}
      {filteredUsers.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-gray-400 text-6xl mb-4">👥</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
          <p className="text-gray-500 mb-6">
            {searchQuery
              ? 'Try adjusting your search criteria'
              : 'Get started by inviting your first team member'}
          </p>
          {!searchQuery && (
            <button
              onClick={() => setShowInviteModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Invite User
            </button>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Roles
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <UserAvatar user={user} size="sm" />
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{user.email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {user.roles.map(role => (
                        <RoleBadge key={role.id} role={role} />
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                        }`}
                    >
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.last_login_at
                      ? new Date(user.last_login_at).toLocaleDateString()
                      : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => setEditingUser(user)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => setDeactivatingUser(user)}
                      className={user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}
                    >
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modals */}
      <InviteUserModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        onSuccess={loadUsers}
      />

      <BulkInviteUsersModal
        isOpen={showBulkInviteModal}
        onClose={() => setShowBulkInviteModal(false)}
        onSuccess={loadUsers}
      />

      {editingUser && (
        <EditUserModal
          isOpen={!!editingUser}
          onClose={() => setEditingUser(null)}
          onSuccess={loadUsers}
          user={editingUser}
        />
      )}

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={!!deactivatingUser}
        onClose={() => setDeactivatingUser(null)}
        onConfirm={() => {
          if (deactivatingUser) {
            handleToggleActive(deactivatingUser);
            setDeactivatingUser(null);
          }
        }}
        title={deactivatingUser?.is_active ? 'Deactivate User' : 'Activate User'}
        message={
          deactivatingUser?.is_active
            ? `Are you sure you want to deactivate ${deactivatingUser?.full_name}? They will no longer be able to access the system.`
            : `Are you sure you want to activate ${deactivatingUser?.full_name}? They will regain access to the system.`
        }
        confirmText={deactivatingUser?.is_active ? 'Deactivate' : 'Activate'}
        type={deactivatingUser?.is_active ? 'danger' : 'info'}
      />
    </div>
  );
};
