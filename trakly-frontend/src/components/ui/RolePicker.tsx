import { useState, useEffect } from 'react';
import { RoleResponse } from '@/types';
import { rolesService } from '@/lib/services/roles.service';
import { RoleBadge } from '@/components/settings/RoleBadge';

interface RolePickerProps {
  selectedRoleIds: string[];
  onChange: (roleIds: string[]) => void;
  label?: string;
  required?: boolean;
}

export const RolePicker: React.FC<RolePickerProps> = ({
  selectedRoleIds,
  onChange,
  label = 'Roles',
  required = false,
}) => {
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const loadRoles = async () => {
      try {
        const response = await rolesService.listRoles();
        setRoles(response.data || []);
      } catch (error) {
        console.error('Failed to load roles:', error);
        setRoles([]);
      } finally {
        setLoading(false);
      }
    };
    loadRoles();
  }, []);

  const toggleRole = (roleId: string) => {
    if (selectedRoleIds.includes(roleId)) {
      onChange(selectedRoleIds.filter(id => id !== roleId));
    } else {
      onChange([...selectedRoleIds, roleId]);
    }
  };

  const selectedRoles = (roles || []).filter(role => selectedRoleIds.includes(role.id));

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative">
        <button
          type="button"
          onClick={() => setShowDropdown(!showDropdown)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-left"
        >
          {loading ? (
            <span className="text-gray-400">Loading roles...</span>
          ) : selectedRoles.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {selectedRoles.map(role => (
                <RoleBadge key={role.id} role={role} />
              ))}
            </div>
          ) : (
            <span className="text-gray-400">Select roles...</span>
          )}
        </button>

        {showDropdown && !loading && (
          <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {roles.map((role) => (
              <label
                key={role.id}
                className="flex items-center px-3 py-2 hover:bg-gray-100 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedRoleIds.includes(role.id)}
                  onChange={() => toggleRole(role.id)}
                  className="mr-3 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <div className="flex-1">
                  <RoleBadge role={role} />
                  {role.description && (
                    <p className="text-xs text-gray-500 mt-1">{role.description}</p>
                  )}
                </div>
              </label>
            ))}
            {roles.length === 0 && (
              <div className="px-3 py-4 text-center text-sm text-gray-500">
                <p>No roles found.</p>
                <p className="text-xs mt-1">Create roles in Settings &gt; Roles.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  );
};
