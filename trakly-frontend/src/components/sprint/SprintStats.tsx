import React, { useEffect, useState } from 'react';
import { SprintStats as SprintStatsType } from '@/types';
import apiClient from '@/lib/api';

interface SprintStatsProps {
    sprintId: string;
}

export const SprintStats: React.FC<SprintStatsProps> = ({ sprintId }) => {
    const [stats, setStats] = useState<SprintStatsType | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await apiClient.get<SprintStatsType>(`/sprints/${sprintId}/stats`);
                setStats(res.data);
            } catch (error) {
                console.error("Failed to load stats");
            } finally {
                setLoading(false);
            }
        };

        if (sprintId) {
            fetchStats();
        }
    }, [sprintId]);

    if (loading) return <div className="text-xs text-gray-400">Loading stats...</div>;
    if (!stats) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* Status Breakdown */}
            <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Status Breakdown</h4>
                <div className="space-y-2">
                    {Object.entries(stats.by_status).map(([status, count]) => (
                        <div key={status} className="flex justify-between items-center text-sm">
                            <span className="capitalize text-gray-700">{status.replace('_', ' ')}</span>
                            <span className="font-medium bg-gray-100 px-2 py-0.5 rounded-full text-gray-600">{count as React.ReactNode}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Priority Breakdown */}
            <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Priority Breakdown</h4>
                <div className="space-y-2">
                    {Object.entries(stats.by_priority).map(([priority, count]) => (
                        <div key={priority} className="flex justify-between items-center text-sm">
                            <span className="capitalize text-gray-700">{priority}</span>
                            <span className="font-medium bg-gray-100 px-2 py-0.5 rounded-full text-gray-600">{count as React.ReactNode}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Assignee Breakdown */}
            <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Workload by User</h4>
                <div className="space-y-2">
                    {Object.entries(stats.by_assignee).map(([user, count]) => (
                        <div key={user} className="flex justify-between items-center text-sm">
                            <span className="truncate text-gray-700 max-w-[120px]" title={user}>{user}</span>
                            <span className="font-medium bg-gray-100 px-2 py-0.5 rounded-full text-gray-600">{count as React.ReactNode}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
