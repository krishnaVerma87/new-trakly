import React, { useState, useEffect } from 'react';
import { projectsService } from '@/lib/services/projects.service';
import { ComponentResponse, ComponentCreate } from '@/types';
import { UserPicker } from '@/components/ui/UserPicker';
import toast from 'react-hot-toast';

interface ComponentsManagerProps {
    projectId: string;
}

export const ComponentsManager: React.FC<ComponentsManagerProps> = ({ projectId }) => {
    const [components, setComponents] = useState<ComponentResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCreating, setIsCreating] = useState(false);
    const [formData, setFormData] = useState<ComponentCreate>({
        name: '',
        description: '',
        lead_user_id: undefined,
    });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadComponents();
    }, [projectId]);

    const loadComponents = async () => {
        try {
            setLoading(true);
            const response = await projectsService.listComponents(projectId);
            setComponents(response.data);
        } catch (error) {
            toast.error('Failed to load components');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.name.trim()) {
            toast.error('Component name is required');
            return;
        }

        try {
            setSubmitting(true);
            await projectsService.createComponent(projectId, formData);
            toast.success('Component created successfully');
            setFormData({ name: '', description: '', lead_user_id: undefined });
            setIsCreating(false);
            loadComponents();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create component');
        } finally {
            setSubmitting(false);
        }
    };

    const handleCancel = () => {
        setIsCreating(false);
        setFormData({ name: '', description: '', lead_user_id: undefined });
    };

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
                    <h3 className="text-lg font-semibold text-gray-900">Components</h3>
                    <p className="text-sm text-gray-500 mt-1">
                        Organize your project by architectural components (Frontend, Backend, API, etc.)
                    </p>
                </div>
                {!isCreating && (
                    <button
                        onClick={() => setIsCreating(true)}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Add Component
                    </button>
                )}
            </div>

            {/* Create Form */}
            {isCreating && (
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                                Component Name <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                id="name"
                                required
                                autoFocus
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="e.g. Frontend, Backend, API, Mobile"
                            />
                        </div>

                        <div>
                            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                                Description
                            </label>
                            <textarea
                                id="description"
                                rows={2}
                                value={formData.description || ''}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Brief description of this component"
                            />
                        </div>

                        <UserPicker
                            projectId={projectId}
                            value={formData.lead_user_id}
                            onChange={(userId) => setFormData({ ...formData, lead_user_id: userId })}
                            label="Component Lead"
                            placeholder="Select a team lead (optional)"
                        />

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
                                {submitting ? 'Creating...' : 'Create Component'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Components List */}
            {components.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                    <div className="w-16 h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                    </div>
                    <p className="text-gray-500 mb-4">No components yet</p>
                    <p className="text-sm text-gray-400">
                        Create components to organize tasks and features by system architecture
                    </p>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {components.map((component) => (
                        <div
                            key={component.id}
                            className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex-1">
                                    <h4 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                                        <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                        </svg>
                                        {component.name}
                                    </h4>
                                    {component.description && (
                                        <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                                            {component.description}
                                        </p>
                                    )}
                                </div>
                            </div>

                            {/* Lead user display - uncomment when backend provides lead user data
                            {component.lead_user_id && (
                                <div className="flex items-center gap-2 text-sm text-gray-600 mt-3 pt-3 border-t border-gray-100">
                                    <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                    <span className="font-medium">Lead:</span>
                                    <span>{component.lead_user_id}</span>
                                </div>
                            )} */}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
