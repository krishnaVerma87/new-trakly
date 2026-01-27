import React, { useState } from 'react';
import { projectsService } from '@/lib/services/projects.service';
import { Modal } from '@/components/ui/Modal';
import { ProjectCreate } from '@/types';
import { useAuth } from '@/contexts/AuthContext';
import toast from 'react-hot-toast';

interface CreateProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
    isOpen,
    onClose,
    onSuccess,
}) => {
    const { user } = useAuth();
    const [formData, setFormData] = useState<ProjectCreate>({
        name: '',
        key: '',
        description: '',
        organization_id: user?.organization_id || '',
    });
    const [submitting, setSubmitting] = useState(false);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const { name, value } = e.target;

        // Auto-generate key from name if key is empty or hasn't been manually edited
        if (name === 'name' && (!formData.key || formData.key.length < 2)) {
            const suggestedKey = value
                .toUpperCase()
                .replace(/[^A-Z0-9]/g, '')
                .slice(0, 4);

            setFormData((prev) => ({
                ...prev,
                name: value,
                key: suggestedKey,
            }));
        } else {
            setFormData((prev) => ({ ...prev, [name]: value }));
        }
    };

    const handleKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 10);
        setFormData((prev) => ({ ...prev, key: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.name || !formData.key) {
            toast.error('Name and Key are required');
            return;
        }

        try {
            setSubmitting(true);
            await projectsService.createProject(formData);
            toast.success('Project created successfully');
            onSuccess();
            onClose();
            // Reset form
            setFormData({
                name: '',
                key: '',
                description: '',
                organization_id: user?.organization_id || ''
            });
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create project');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Create New Project">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                        Project Name <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        required
                        value={formData.name}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Mobile App"
                        autoFocus
                    />
                </div>

                <div>
                    <label htmlFor="key" className="block text-sm font-medium text-gray-700 mb-1">
                        Project Key <span className="text-red-500">*</span>
                        <span className="text-xs text-gray-500 font-normal ml-2">
                            (Unique prefix for issues, e.g. MOB-123)
                        </span>
                    </label>
                    <input
                        type="text"
                        id="key"
                        name="key"
                        required
                        maxLength={10}
                        value={formData.key}
                        onChange={handleKeyChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase font-mono"
                        placeholder="MOB"
                    />
                </div>

                <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                    </label>
                    <textarea
                        id="description"
                        name="description"
                        rows={3}
                        value={formData.description || ''}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Brief description of the project..."
                    />
                </div>

                <div className="flex justify-end gap-3 pt-4">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={submitting}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {submitting ? 'Creating...' : 'Create Project'}
                    </button>
                </div>
            </form>
        </Modal>
    );
};
