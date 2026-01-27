import React, { useState, useEffect } from 'react';
import { featuresService } from '@/lib/services/features.service';
import { FeatureCreate } from '@/types';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import { UserPicker } from '@/components/ui/UserPicker';
import { ComponentPicker } from '@/components/ui/ComponentPicker';
import toast from 'react-hot-toast';

interface CreateFeatureModalProps {
    isOpen: boolean;
    onClose: () => void;
    projectId: string;
    onSuccess: () => void;
}

export const CreateFeatureModal: React.FC<CreateFeatureModalProps> = ({
    isOpen,
    onClose,
    projectId,
    onSuccess,
}) => {
    const [formData, setFormData] = useState<Partial<FeatureCreate>>({
        project_id: projectId,
        priority: 'medium',
        title: '',
        description: '',
    });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setFormData({
                project_id: projectId,
                priority: 'medium',
                title: '',
                description: '',
            });
        }
    }, [isOpen, projectId]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.title) {
            toast.error('Title is required');
            return;
        }

        try {
            setSubmitting(true);
            await featuresService.createFeature(formData as FeatureCreate);
            toast.success('Feature created successfully');
            onSuccess();
            onClose();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create feature');
        } finally {
            setSubmitting(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
                <div
                    className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
                    onClick={onClose}
                ></div>

                <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

                <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
                    <form onSubmit={handleSubmit}>
                        <div className="bg-white px-6 pt-5 pb-4">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-lg font-semibold text-gray-900">Create New Feature</h3>
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="text-gray-400 hover:text-gray-500"
                                >
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                                        Title <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        id="title"
                                        name="title"
                                        required
                                        autoFocus
                                        value={formData.title}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="Feature name"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                                            Priority
                                        </label>
                                        <select
                                            id="priority"
                                            name="priority"
                                            value={formData.priority}
                                            onChange={handleInputChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="critical">Critical</option>
                                            <option value="high">High</option>
                                            <option value="medium">Medium</option>
                                            <option value="low">Low</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label htmlFor="target_release" className="block text-sm font-medium text-gray-700 mb-1">
                                            Target Release
                                        </label>
                                        <input
                                            type="text"
                                            id="target_release"
                                            name="target_release"
                                            value={formData.target_release || ''}
                                            onChange={handleInputChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g. v1.2.0"
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <UserPicker
                                        projectId={projectId}
                                        value={formData.owner_user_id}
                                        onChange={(userId) => setFormData(prev => ({ ...prev, owner_user_id: userId }))}
                                        label="Owner"
                                    />

                                    <ComponentPicker
                                        projectId={projectId}
                                        value={formData.component_id}
                                        onChange={(id) => setFormData(prev => ({ ...prev, component_id: id }))}
                                        label="Component"
                                    />
                                </div>

                                <div>
                                    <label htmlFor="target_date" className="block text-sm font-medium text-gray-700 mb-1">
                                        Target Date
                                    </label>
                                    <input
                                        type="date"
                                        id="target_date"
                                        name="target_date"
                                        value={formData.target_date || ''}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <RichTextEditor
                                        content={formData.description || ''}
                                        onChange={(content) => setFormData(prev => ({ ...prev, description: content }))}
                                        placeholder="Describe the feature..."
                                        minHeight="200px"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-50 px-6 py-4 flex items-center justify-end gap-3">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={submitting}
                                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {submitting ? 'Creating...' : 'Create Feature'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
