import React, { useState } from 'react';
import { sprintsService } from '@/lib/services/sprints.service';
import toast from 'react-hot-toast';

interface CreateSprintModalProps {
    isOpen: boolean;
    onClose: () => void;
    projectId: string;
    onSuccess: () => void;
}

export const CreateSprintModal: React.FC<CreateSprintModalProps> = ({
    isOpen,
    onClose,
    projectId,
    onSuccess
}) => {
    const [formData, setFormData] = useState({
        name: '',
        goal: '',
        start_date: '',
        end_date: '',
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await sprintsService.create({
                ...formData,
                project_id: projectId
            });
            toast.success('Sprint created successfully');
            setFormData({ name: '', goal: '', start_date: '', end_date: '' });
            onSuccess();
            onClose();
        } catch (error: any) {
            toast.error('Failed to create sprint');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
                <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

                <div className="relative bg-white rounded-lg max-w-md w-full p-6 shadow-xl transform transition-all">
                    <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">
                        Create Sprint
                    </h3>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Sprint Name
                            </label>
                            <input
                                name="name"
                                type="text"
                                required
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Sprint 1"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Goal (Optional)
                            </label>
                            <textarea
                                name="goal"
                                rows={2}
                                value={formData.goal}
                                onChange={handleChange}
                                placeholder="What is the goal for this sprint?"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Start Date
                                </label>
                                <input
                                    name="start_date"
                                    type="date"
                                    required
                                    value={formData.start_date}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    End Date
                                </label>
                                <input
                                    name="end_date"
                                    type="date"
                                    required
                                    value={formData.end_date}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                        </div>

                        <div className="mt-5 flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {loading ? 'Creating...' : 'Create Sprint'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
