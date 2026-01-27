import { RoleResponse } from '@/types';

interface RoleBadgeProps {
  role: RoleResponse;
}

export const RoleBadge: React.FC<RoleBadgeProps> = ({ role }) => {
  const getRoleColor = (roleName: string): string => {
    const roleColors: Record<string, string> = {
      'admin': 'bg-red-100 text-red-800',
      'org_admin': 'bg-red-100 text-red-800',
      'project_manager': 'bg-blue-100 text-blue-800',
      'developer': 'bg-green-100 text-green-800',
      'qa': 'bg-purple-100 text-purple-800',
      'viewer': 'bg-gray-100 text-gray-800',
    };
    return roleColors[roleName.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const formatRoleName = (name: string): string => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${getRoleColor(role.name)}`}>
      {formatRoleName(role.name)}
    </span>
  );
};
