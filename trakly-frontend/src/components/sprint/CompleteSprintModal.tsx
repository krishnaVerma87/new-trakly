import React, { useState, useEffect } from 'react';
import { SprintResponse, SprintStats } from '@/types';
import apiClient from '@/lib/api';
import toast from 'react-hot-toast';

interface CompleteSprintModalProps {
    isOpen: boolean;
    onClose: () => void;
    sprint: SprintResponse;
    projectId: string;
    onSuccess: () => void;
}

export const CompleteSprintModal: React.FC<CompleteSprintModalProps> = ({
    isOpen,
    onClose,
    sprint,

    onSuccess
}) => {
    const [stats, setStats] = useState<SprintStats | null>(null);
    const [loading, setLoading] = useState(false);
    const [action, setAction] = useState<'backlog' | 'new_sprint'>('backlog');
    // In a real app, we'd fetch future sprints to populate a dropdown for 'new_sprint'

    useEffect(() => {
        if (isOpen && sprint.id) {
            fetchStats();
        }
    }, [isOpen, sprint.id]);

    const fetchStats = async () => {
        try {
            const res = await apiClient.get(`/sprints/${sprint.id}/stats`);
            setStats(res.data);
        } catch (error) {
            console.error("Failed to fetch sprint stats");
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await apiClient.post(`/sprints/${sprint.id}/complete`, {
                move_issues_to: action,
                // new_sprint_id: ... if we implemented the dropdown
            });
            toast.success('Sprint completed!');
            onSuccess();
            onClose();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to complete sprint');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
                <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

                <div className="relative bg-white rounded-lg max-w-md w-full p-6 shadow-xl transform transition-all">
                    <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">
                        Complete Sprint: {sprint.name}
                    </h3>

                    {stats && (
                        <div className="bg-gray-50 p-4 rounded-md mb-6 flex gap-8 text-center">
                            <div>
                                <div className="text-2xl font-bold text-green-600">{stats.completed_issues}</div>
                                <div className="text-xs text-gray-500 uppercase tracking-wide">Completed</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-orange-500">{stats.incomplete_issues}</div>
                                <div className="text-xs text-gray-500 uppercase tracking-wide">Incomplete</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-gray-700">{stats.total_issues}</div>
                                <div className="text-xs text-gray-500 uppercase tracking-wide">Total</div>
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Move incomplete issues to:
                            </label>
                            <div className="space-y-2">
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        name="move_action"
                                        value="backlog"
                                        checked={action === 'backlog'}
                                        onChange={() => setAction('backlog')}
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                    />
                                    <span className="ml-2 text-sm text-gray-700">Backlog</span>
                                </label>
                                {/* Placeholder for 'New Sprint' option - blocked on fetching future sprints logic */}
                                <label className="flex items-center opacity-50 cursor-not-allowed" title="Create a new sprint first">
                                    <input
                                        type="radio"
                                        name="move_action"
                                        value="new_sprint"
                                        disabled
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                    />
                                    <span className="ml-2 text-sm text-gray-700">New Sprint (Coming Soon)</span>
                                </label>
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
                                {loading ? 'Completing...' : 'Complete Sprint'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
