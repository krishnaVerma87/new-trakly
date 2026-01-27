import { useState, FormEvent, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { usersService } from '@/lib/services/users.service';
import { rolesService } from '@/lib/services/roles.service';
import { toast } from 'react-hot-toast';
import { BulkUserInvite, RoleResponse, BulkUserInviteResult } from '@/types';

interface BulkInviteUsersModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface UserRow extends BulkUserInvite {
  id: string;
}

export const BulkInviteUsersModal: React.FC<BulkInviteUsersModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [users, setUsers] = useState<UserRow[]>([
    { id: crypto.randomUUID(), email: '', full_name: '', role_id: '' },
  ]);
  const [results, setResults] = useState<BulkUserInviteResult[]>([]);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadRoles();
    }
  }, [isOpen]);

  const loadRoles = async () => {
    try {
      const response = await rolesService.listRoles();
      setRoles(response.data || []);
    } catch (error) {
      toast.error('Failed to load roles');
    }
  };

  const addUserRow = () => {
    if (users.length >= 50) {
      toast.error('Maximum 50 users can be invited at once');
      return;
    }
    setUsers([...users, { id: crypto.randomUUID(), email: '', full_name: '', role_id: '' }]);
  };

  const removeUserRow = (id: string) => {
    if (users.length === 1) {
      toast.error('At least one user is required');
      return;
    }
    setUsers(users.filter(u => u.id !== id));
  };

  const updateUserRow = (id: string, field: keyof BulkUserInvite, value: string) => {
    setUsers(users.map(u => (u.id === id ? { ...u, [field]: value } : u)));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validation
    const invalidUsers = users.filter(u => !u.email || !u.full_name || !u.role_id);
    if (invalidUsers.length > 0) {
      toast.error('Please fill in all fields for each user');
      return;
    }

    // Check for duplicate emails
    const emails = users.map(u => u.email.toLowerCase());
    const duplicates = emails.filter((email, index) => emails.indexOf(email) !== index);
    if (duplicates.length > 0) {
      toast.error(`Duplicate email(s) found: ${duplicates.join(', ')}`);
      return;
    }

    try {
      setSubmitting(true);
      const response = await usersService.bulkInviteUsers({
        users: users.map(({ id, ...rest }) => rest),
      });

      setResults(response.data.results);
      setShowResults(true);

      if (response.data.successful > 0) {
        toast.success(
          `Successfully invited ${response.data.successful} user(s). ${
            response.data.failed > 0 ? `${response.data.failed} failed.` : ''
          }`
        );
        onSuccess();
      }

      if (response.data.failed === users.length) {
        toast.error('All user invitations failed');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to invite users');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setUsers([{ id: crypto.randomUUID(), email: '', full_name: '', role_id: '' }]);
    setResults([]);
    setShowResults(false);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Bulk Invite Users" size="xl">
      {!showResults ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="mb-4">
            <p className="text-sm text-gray-600">
              Invite up to 50 users at once. Temporary passwords will be auto-generated and sent via
              email.
            </p>
          </div>

          {/* Users Table */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Email
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Full Name
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Role
                    </th>
                    <th className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase w-20">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-3 py-2">
                        <input
                          type="email"
                          value={user.email}
                          onChange={(e) => updateUserRow(user.id, 'email', e.target.value)}
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          placeholder="user@example.com"
                          required
                        />
                      </td>
                      <td className="px-3 py-2">
                        <input
                          type="text"
                          value={user.full_name}
                          onChange={(e) => updateUserRow(user.id, 'full_name', e.target.value)}
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          placeholder="John Doe"
                          required
                        />
                      </td>
                      <td className="px-3 py-2">
                        <select
                          value={user.role_id}
                          onChange={(e) => updateUserRow(user.id, 'role_id', e.target.value)}
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          required
                        >
                          <option value="">Select role</option>
                          {roles.map((role) => (
                            <option key={role.id} value={role.id}>
                              {role.name}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="px-3 py-2 text-center">
                        <button
                          type="button"
                          onClick={() => removeUserRow(user.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                          disabled={users.length === 1}
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add More Button */}
          <button
            type="button"
            onClick={addUserRow}
            className="w-full py-2 border-2 border-dashed border-gray-300 rounded-md text-sm text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors"
            disabled={users.length >= 50}
          >
            + Add Another User {users.length >= 50 && '(Max 50 reached)'}
          </button>

          {/* Actions */}
          <div className="flex justify-between items-center pt-4 border-t">
            <div className="text-sm text-gray-600">
              {users.length} user{users.length !== 1 ? 's' : ''} to invite
            </div>
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handleClose}
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
                {submitting ? 'Inviting...' : `Invite ${users.length} User${users.length !== 1 ? 's' : ''}`}
              </button>
            </div>
          </div>
        </form>
      ) : (
        // Results View
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Invitation Results</h3>
            <p className="text-sm text-blue-700">
              {results.filter(r => r.success).length} successful,{' '}
              {results.filter(r => !r.success).length} failed
            </p>
          </div>

          <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Email
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Name
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((result, index) => (
                  <tr key={index}>
                    <td className="px-4 py-2">
                      {result.success ? (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          Success
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                          Failed
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm">{result.email}</td>
                    <td className="px-4 py-2 text-sm">{result.full_name}</td>
                    <td className="px-4 py-2 text-sm">
                      {result.success ? (
                        <span className="text-gray-600">
                          Password sent to email
                        </span>
                      ) : (
                        <span className="text-red-600">{result.error}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-end pt-4 border-t">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </Modal>
  );
};
