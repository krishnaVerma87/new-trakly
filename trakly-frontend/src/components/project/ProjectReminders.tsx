import React, { useEffect, useState } from 'react';
import { remindersService } from '@/lib/services/reminders.service';
import { ReminderRuleResponse } from '@/types';

import toast from 'react-hot-toast';

interface ProjectRemindersProps {
    projectId: string;
}

export const ProjectReminders: React.FC<ProjectRemindersProps> = ({ projectId }) => {
    const [rules, setRules] = useState<ReminderRuleResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);

    // Form state
    const [name, setName] = useState('');
    const [days, setDays] = useState(3);
    const [selectedSprint, setSelectedSprint] = useState<string>('current');
    const [selectedPriorities, setSelectedPriorities] = useState<string[]>(['high', 'critical']);
    const [selectedStatuses, setSelectedStatuses] = useState<string[]>(['new', 'in_progress']);

    useEffect(() => {
        loadRules();
    }, [projectId]);

    const loadRules = async () => {
        try {
            setLoading(true);
            const response = await remindersService.listRules(projectId, true);
            setRules(response.data);
        } catch (error) {
            toast.error('Failed to load reminder rules');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateRule = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await remindersService.createRule({
                project_id: projectId,
                name,
                conditions: {
                    days_without_update: days,
                    sprint: selectedSprint,
                    priority: selectedPriorities.length > 0 ? selectedPriorities : undefined,
                    status: selectedStatuses.length > 0 ? selectedStatuses : undefined,
                },
                notification_title: `Reminder: {issue_key} is stale`,
                notification_message: `Issue {issue_key} ("{issue_title}") has had no updates for {days} days.`,
                is_enabled: true,
            });
            toast.success('Reminder rule created');
            setShowCreate(false);
            setName('');
            setSelectedSprint('current');
            setSelectedPriorities(['high', 'critical']);
            setSelectedStatuses(['new', 'in_progress']);
            loadRules();
        } catch (error) {
            toast.error('Failed to create rule');
        }
    };

    const handleToggleRule = async (ruleId: string, enabled: boolean) => {
        try {
            await remindersService.updateRule(ruleId, { is_enabled: enabled });
            loadRules();
            toast.success(enabled ? 'Rule enabled' : 'Rule disabled');
        } catch (error) {
            toast.error('Failed to update rule');
        }
    };

    const handleDeleteRule = async (ruleId: string) => {
        if (!confirm('Are you sure you want to delete this rule?')) return;
        try {
            await remindersService.deleteRule(ruleId);
            loadRules();
            toast.success('Rule deleted');
        } catch (error) {
            toast.error('Failed to delete rule');
        }
    };

    if (loading) return <div className="p-4">Loading rules...</div>;

    return (
        <div className="space-y-6 p-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-xl font-bold text-gray-900">Task Tracking & Reminders</h2>
                    <p className="text-sm text-gray-500 mt-1">Configure automated reminders for stale or high-priority tasks.</p>
                </div>
                <button
                    onClick={() => setShowCreate(!showCreate)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                    {showCreate ? 'Cancel' : 'New Rule'}
                </button>
            </div>

            {showCreate && (
                <form onSubmit={handleCreateRule} className="bg-gray-50 p-6 rounded-lg border border-gray-200 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Rule Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g., Stale High Priority Issues"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Days without update</label>
                            <input
                                type="number"
                                value={days}
                                onChange={(e) => setDays(parseInt(e.target.value))}
                                min="1"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Sprint Filter</label>
                            <select
                                value={selectedSprint}
                                onChange={(e) => setSelectedSprint(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="current">Current Sprint</option>
                                <option value="next">Next Sprint</option>
                                <option value="any">Any Sprint</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex gap-8">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Statuses to track</label>
                            <div className="space-y-2">
                                {['new', 'in_progress', 'review'].map(status => (
                                    <label key={status} className="flex items-center gap-2 text-sm capitalize">
                                        <input
                                            type="checkbox"
                                            checked={selectedStatuses.includes(status)}
                                            onChange={(e) => {
                                                if (e.target.checked) setSelectedStatuses([...selectedStatuses, status]);
                                                else setSelectedStatuses(selectedStatuses.filter(s => s !== status));
                                            }}
                                            className="rounded border-gray-300 text-blue-600"
                                        />
                                        {status.replace('_', ' ')}
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Priorities to track</label>
                            <div className="space-y-2">
                                {['critical', 'high', 'medium', 'low'].map(priority => (
                                    <label key={priority} className="flex items-center gap-2 text-sm capitalize">
                                        <input
                                            type="checkbox"
                                            checked={selectedPriorities.includes(priority)}
                                            onChange={(e) => {
                                                if (e.target.checked) setSelectedPriorities([...selectedPriorities, priority]);
                                                else setSelectedPriorities(selectedPriorities.filter(p => p !== priority));
                                            }}
                                            className="rounded border-gray-300 text-blue-600"
                                        />
                                        {priority}
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition-colors"
                    >
                        Create Rule
                    </button>
                </form>
            )}

            <div className="space-y-4">
                {rules.length === 0 ? (
                    <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                        <p className="text-gray-500">No reminder rules configured for this project.</p>
                    </div>
                ) : (
                    rules.map((rule) => (
                        <div key={rule.id} className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex justify-between items-start">
                            <div className="space-y-2">
                                <div className="flex items-center gap-3">
                                    <h3 className="font-bold text-gray-900">{rule.name}</h3>
                                    {!rule.is_enabled && (
                                        <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-[10px] uppercase font-bold rounded">Disabled</span>
                                    )}
                                </div>
                                <div className="text-sm text-gray-600">
                                    Notify if no update in <span className="font-semibold text-gray-900">{rule.conditions.days_without_update} days</span>
                                    {rule.conditions.sprint && ` • Sprint: ${rule.conditions.sprint}`}
                                    {rule.conditions.status && rule.conditions.status.length > 0 && ` • Status: ${rule.conditions.status.join(', ')}`}
                                    {rule.conditions.priority && rule.conditions.priority.length > 0 && ` • Priority: ${rule.conditions.priority.join(', ')}`}
                                </div>
                                <div className="text-[10px] text-gray-400">
                                    Last ran: {rule.last_executed_at ? new Date(rule.last_executed_at).toLocaleString() : 'Never'}
                                </div>
                            </div>

                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => handleToggleRule(rule.id, !rule.is_enabled)}
                                    className={`text-sm font-medium ${rule.is_enabled ? 'text-orange-600 hover:text-orange-700' : 'text-green-600 hover:text-green-700'}`}
                                >
                                    {rule.is_enabled ? 'Disable' : 'Enable'}
                                </button>
                                <button
                                    onClick={() => handleDeleteRule(rule.id)}
                                    className="text-sm font-medium text-red-600 hover:text-red-700"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
