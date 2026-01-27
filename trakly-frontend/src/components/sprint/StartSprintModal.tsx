import React, { useState } from 'react';
import { format } from 'date-fns';
import { SprintResponse } from '@/types';
import apiClient from '@/lib/api';
import toast from 'react-hot-toast';

interface StartSprintModalProps {
    isOpen: boolean;
    onClose: () => void;
    sprint: SprintResponse;
    onSuccess: () => void;
}

export const StartSprintModal: React.FC<StartSprintModalProps> = ({
    isOpen,
    onClose,
    sprint,
    onSuccess
}) => {
    const [startDate, setStartDate] = useState(format(new Date(), 'yyyy-MM-dd'));
    const [endDate, setEndDate] = useState(format(new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd'));
    const [goal, setGoal] = useState(sprint.goal || '');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await apiClient.post(`/sprints/${sprint.id}/start`, {
                start_date: startDate,
                end_date: endDate,
                goal: goal,
            });
            toast.success('Sprint started successfully!');
            onSuccess();
            onClose();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to start sprint');
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
                        Start Sprint: {sprint.name}
                    </h3>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Sprint Goal
                            </label>
                            <textarea
                                value={goal}
                                onChange={(e) => setGoal(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                rows={3}
                                placeholder="What is the main objective of this sprint?"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Start Date
                                </label>
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    End Date
                                </label>
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                    required
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
                                {loading ? 'Starting...' : 'Start Sprint'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
