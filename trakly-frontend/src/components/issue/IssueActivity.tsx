import React, { useEffect, useState } from 'react';
import { UserAvatar } from '@/components/ui/UserAvatar';
import { ActivityItem } from '@/types';
import { activityService } from '@/lib/services/activity.service';
import { formatDistanceToNow } from 'date-fns';

interface IssueActivityProps {
    issueId: string;
}

export const IssueActivity: React.FC<IssueActivityProps> = ({ issueId }) => {
    const [activities, setActivities] = useState<ActivityItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadActivities();
    }, [issueId]);

    const loadActivities = async () => {
        try {
            setLoading(true);
            const response = await activityService.getEntityActivities('issue', issueId);
            setActivities(response.data);
        } catch (error) {
            console.error('Error loading activities:', error);
            // Fall back to mock data for now
            const mockActivities: ActivityItem[] = [
                {
                    id: '1',
                    issue_id: issueId,
                    user_id: 'user-1',
                    user: {
                        id: 'user-1',
                        full_name: 'Sarah Engineer',
                        email: 'sarah@trakly.com',
                        organization_id: 'org-1',
                        is_active: true,
                        timezone: 'UTC',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString()
                    },
                    action_type: 'commented',
                    details: 'I think we should prioritize this for the next sprint.',
                    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() // 2 hours ago
                },
                {
                    id: '2',
                    issue_id: issueId,
                    user_id: 'user-2',
                    user: {
                        id: 'user-2',
                        full_name: 'Alex Manager',
                        email: 'alex@trakly.com',
                        organization_id: 'org-1',
                        is_active: true,
                        timezone: 'UTC',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString()
                    },
                    action_type: 'status_changed',
                    field_name: 'Status',
                    from_value: 'New',
                    to_value: 'In Progress',
                    created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString() // 5 hours ago
                },
                {
                    id: '3',
                    issue_id: issueId,
                    user_id: 'system',
                    user: {
                        id: 'system',
                        full_name: 'System',
                        email: 'system@trakly.com',
                        organization_id: 'org-1',
                        is_active: true,
                        timezone: 'UTC',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString()
                    },
                    action_type: 'created',
                    details: 'created this task',
                    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() // 1 day ago
                }
            ];
            setActivities(mockActivities);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4 text-center text-xs text-gray-500">Loading activity...</div>;

    return (
        <div className="space-y-6">
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider border-b border-gray-100 pb-2">
                Activity Stream
            </h3>

            <div className="flow-root">
                <ul className="-mb-8">
                    {activities.map((activity, activityIdx) => {
                        const isComment = activity.action_type === 'commented';

                        return (
                            <li key={activity.id}>
                                <div className="relative pb-8">
                                    {activityIdx !== activities.length - 1 ? (
                                        <span
                                            className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                                            aria-hidden="true"
                                        />
                                    ) : null}

                                    <div className="relative flex space-x-3">
                                        <div>
                                            {activity.user.full_name === 'System' ? (
                                                <span className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center ring-8 ring-white">
                                                    <svg className="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                    </svg>
                                                </span>
                                            ) : (
                                                <UserAvatar user={activity.user} className="h-8 w-8 ring-8 ring-white" />
                                            )}
                                        </div>

                                        <div className="min-w-0 flex-1 pt-1.5">
                                            <div className="flex justify-between items-center mb-1">
                                                <p className="text-sm font-medium text-gray-900">
                                                    {activity.user.full_name}
                                                </p>
                                                <span className="text-xs text-gray-500 whitespace-nowrap">
                                                    {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
                                                </span>
                                            </div>

                                            {isComment ? (
                                                <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-800 border border-gray-200 mt-1">
                                                    {activity.details}
                                                </div>
                                            ) : (
                                                <p className="text-sm text-gray-600">
                                                    {activity.action_type === 'status_changed' ? (
                                                        <>
                                                            changed status from <span className="font-medium text-gray-900">{activity.from_value}</span> to <span className="font-medium text-gray-900">{activity.to_value}</span>
                                                        </>
                                                    ) : activity.action_type === 'created' ? (
                                                        <span>created this task</span>
                                                    ) : (
                                                        <span>{activity.details}</span>
                                                    )}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </li>
                        );
                    })}
                </ul>
            </div>
        </div>
    );
};
