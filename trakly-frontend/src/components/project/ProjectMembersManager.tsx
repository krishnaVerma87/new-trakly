import React, { useState, useEffect } from 'react';
import { projectsService } from '@/lib/services/projects.service';
import { usersService } from '@/lib/services/users.service';
import { ProjectMemberResponse, UserWithRolesResponse, ProjectMemberCreate } from '@/types';
import toast from 'react-hot-toast';

interface ProjectMembersManagerProps {
    projectId: string;
}

const MEMBER_ROLES = [
    { value: 'admin', label: 'Admin', description: 'Full access to project settings and members' },
    { value: 'member', label: 'Member', description: 'Create and manage issues' },
    { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
];

export const ProjectMembersManager: React.FC<ProjectMembersManagerProps> = ({ projectId }) => {
    const [members, setMembers] = useState<ProjectMemberResponse[]>([]);
    const [allUsers, setAllUsers] = useState<UserWithRolesResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAdding, setIsAdding] = useState(false);
    const [selectedUserId, setSelectedUserId] = useState('');
    const [selectedRole, setSelectedRole] = useState('member');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadData();
    }, [projectId]);

    const loadData = async () => {
        try {
            setLoading(true);
            const [membersRes, usersRes] = await Promise.all([
                projectsService.listProjectMembers(projectId),
                usersService.listUsers(),
            ]);
            setMembers(membersRes.data);
            setAllUsers(usersRes.data);
        } catch (error) {
            toast.error('Failed to load members');
        } finally {
            setLoading(false);
        }
    };

    const handleAddMember = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!selectedUserId) {
            toast.error('Please select a user');
            return;
        }

        // Check if user is already a member
        if (members.some(m => m.user_id === selectedUserId)) {
            toast.error('User is already a project member');
            return;
        }

        try {
            setSubmitting(true);
            const data: ProjectMemberCreate = {
                user_id: selectedUserId,
                role: selectedRole,
            };
            await projectsService.addProjectMember(projectId, data);
            toast.success('Member added successfully');
            setSelectedUserId('');
            setSelectedRole('member');
            setIsAdding(false);
            loadData();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to add member');
        } finally {
            setSubmitting(false);
        }
    };

    const handleRemoveMember = async (userId: string) => {
        if (!confirm('Are you sure you want to remove this member from the project?')) {
            return;
        }

        try {
            await projectsService.removeProjectMember(projectId, userId);
            toast.success('Member removed successfully');
            loadData();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to remove member');
        }
    };

    const handleCancel = () => {
        setIsAdding(false);
        setSelectedUserId('');
        setSelectedRole('developer');
    };

    // Get users who are not already members
    const availableUsers = allUsers.filter(
        user => !members.some(m => m.user_id === user.id)
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-semibold text-gray-900">Project Members</h3>
                    <p className="text-sm text-gray-500 mt-1">
                        Manage who has access to this project and their roles
                    </p>
                </div>
                {!isAdding && (
                    <button
                        onClick={() => setIsAdding(true)}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Add Member
                    </button>
                )}
            </div>

            {/* Add Member Form */}
            {isAdding && (
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <form onSubmit={handleAddMember} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="user" className="block text-sm font-medium text-gray-700 mb-1">
                                    Select User <span className="text-red-500">*</span>
                                </label>
                                <select
                                    id="user"
                                    required
                                    value={selectedUserId}
                                    onChange={(e) => setSelectedUserId(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Choose a user...</option>
                                    {availableUsers.map((user) => (
                                        <option key={user.id} value={user.id}>
                                            {user.full_name} ({user.email})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
                                    Role <span className="text-red-500">*</span>
                                </label>
                                <select
                                    id="role"
                                    required
                                    value={selectedRole}
                                    onChange={(e) => setSelectedRole(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    {MEMBER_ROLES.map((role) => (
                                        <option key={role.value} value={role.value}>
                                            {role.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {selectedRole && (
                            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                                <p className="text-sm text-blue-800">
                                    <span className="font-semibold">
                                        {MEMBER_ROLES.find(r => r.value === selectedRole)?.label}:
                                    </span>{' '}
                                    {MEMBER_ROLES.find(r => r.value === selectedRole)?.description}
                                </p>
                            </div>
                        )}

                        <div className="flex items-center justify-end gap-3 pt-2">
                            <button
                                type="button"
                                onClick={handleCancel}
                                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={submitting}
                                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {submitting ? 'Adding...' : 'Add Member'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Members List */}
            {members.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                    <div className="w-16 h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                    </div>
                    <p className="text-gray-500 mb-4">No members yet</p>
                    <p className="text-sm text-gray-400">
                        Add team members to collaborate on this project
                    </p>
                </div>
            ) : (
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Member
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Role
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Added
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {members.map((member) => (
                                <tr key={member.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                                                <span className="text-blue-700 font-medium text-sm">
                                                    {member.user?.full_name?.[0]?.toUpperCase() || 'U'}
                                                </span>
                                            </div>
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {member.user?.full_name || 'Unknown User'}
                                                </div>
                                                <div className="text-sm text-gray-500">
                                                    {member.user?.email}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                                            {member.role}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(member.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            onClick={() => handleRemoveMember(member.user_id)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            Remove
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
