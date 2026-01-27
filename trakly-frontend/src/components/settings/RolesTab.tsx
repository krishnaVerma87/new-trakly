import { useState, useEffect } from 'react';
import { RoleResponse } from '@/types';
import { rolesService } from '@/lib/services/roles.service';
import { RoleBadge } from './RoleBadge';
import { toast } from 'react-hot-toast';

export const RolesTab = () => {
    const [roles, setRoles] = useState<RoleResponse[]>([]);
    const [loading, setLoading] = useState(true);

    const loadRoles = async () => {
        try {
            setLoading(true);
            const response = await rolesService.listRoles();
            console.log('created role', response.data);
            setRoles(response.data || []);
        } catch (error) {
            console.error('Failed to load roles:', error);
            toast.error('Failed to load roles');
            setRoles([]); // Safety default
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadRoles();
    }, []);

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
                <h2 className="text-xl font-semibold text-gray-900">Roles & Permissions</h2>
                <p className="text-sm text-gray-600 mt-1">
                    System-defined roles available in your organization
                </p>
            </div>

            <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
                <ul className="divide-y divide-gray-200">
                    {roles.map((role) => (
                        <li key={role.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                            <div className="flex items-center gap-3">
                                <h3 className="text-sm font-medium text-gray-900">{role.name}</h3>
                                <RoleBadge role={role} />
                            </div>
                            {role.description && (
                                <p className="text-xs text-gray-500 mt-1">{role.description}</p>
                            )}
                        </li>
                    ))}
                    {roles.length === 0 && (
                        <li className="px-6 py-8 text-center text-gray-500 italic">
                            No roles found
                        </li>
                    )}
                </ul>
            </div>
        </div>
    );
};
