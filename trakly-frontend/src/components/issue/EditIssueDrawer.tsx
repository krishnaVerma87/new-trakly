import React, { useState, useEffect } from 'react';
import { issuesService } from '@/lib/services/issues.service';
import { IssueResponse, IssueUpdate } from '@/types';
import { Drawer } from '@/components/ui/Drawer';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import { UserPicker } from '@/components/ui/UserPicker';
import { ComponentPicker } from '@/components/ui/ComponentPicker';
import { LabelPicker } from '@/components/ui/LabelPicker';
import { SprintPicker } from '@/components/ui/SprintPicker';
import toast from 'react-hot-toast';

interface EditIssueDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    issue: IssueResponse;
    onSuccess: (updated: IssueResponse) => void;
}

export const EditIssueDrawer: React.FC<EditIssueDrawerProps> = ({
    isOpen,
    onClose,
    issue,
    onSuccess,
}) => {
    const [formData, setFormData] = useState<Partial<IssueUpdate>>({});
    const [submitting, setSubmitting] = useState(false);

    // Initialize form data when issue changes or drawer opens
    useEffect(() => {
        if (isOpen && issue) {
            // Extract label IDs from labels array
            const labelIds = issue.labels?.map(label => label.id) || [];

            setFormData({
                title: issue.title,
                description: issue.description || '',
                issue_type: issue.issue_type,
                status: issue.status,
                priority: issue.priority,
                assignee_id: issue.assignee_id || undefined,
                component_id: issue.component_id || undefined,
                sprint_id: issue.sprint_id || undefined,
                label_ids: labelIds,
                severity: issue.severity || 'major',
                repro_steps: issue.repro_steps || '',
                environment: issue.environment || '',
                affected_version: issue.affected_version || '',
                story_points: issue.story_points,
                time_estimate_minutes: issue.time_estimate_minutes,
            });
        }
    }, [isOpen, issue]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const { name, value, type } = e.target;

        if (type === 'number') {
            setFormData((prev) => ({ ...prev, [name]: value ? parseInt(value) : undefined }));
        } else {
            setFormData((prev) => ({ ...prev, [name]: value }));
        }
    };

    const handleRichTextChange = (field: string, content: string) => {
        setFormData((prev) => ({ ...prev, [field]: content }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.title) {
            toast.error('Title is required');
            return;
        }

        try {
            setSubmitting(true);

            // Prepare update data
            const updateData: IssueUpdate = {
                title: formData.title,
                description: formData.description || undefined,
                issue_type: formData.issue_type,
                status: formData.status,
                priority: formData.priority,
                assignee_id: formData.assignee_id || null,
                component_id: formData.component_id || null,
                sprint_id: formData.sprint_id || null,
                label_ids: formData.label_ids,
                story_points: formData.story_points,
                time_estimate_minutes: formData.time_estimate_minutes,
            };

            // Add bug-specific fields if it's a bug
            if (formData.issue_type === 'bug') {
                updateData.severity = formData.severity;
                updateData.repro_steps = formData.repro_steps || undefined;
                updateData.environment = formData.environment || undefined;
                updateData.affected_version = formData.affected_version || undefined;
            }

            const response = await issuesService.updateIssue(issue.id, updateData);
            toast.success('Task updated successfully');
            onSuccess(response.data);
            onClose();
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to update task';
            toast.error(message);
        } finally {
            setSubmitting(false);
        }
    };

    const isBug = formData.issue_type === 'bug';

    return (
        <Drawer isOpen={isOpen} onClose={onClose} title={`Edit ${issue.issue_key}`} size="xl">
            <form onSubmit={handleSubmit} className="flex flex-col h-full">
                <div className="flex-1 overflow-y-auto p-6 space-y-6">

                    {/* Main Inputs */}
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
                                value={formData.title || ''}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Summary of the work"
                            />
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <label htmlFor="issue_type" className="block text-sm font-medium text-gray-700 mb-1">
                                    Type
                                </label>
                                <select
                                    id="issue_type"
                                    name="issue_type"
                                    value={formData.issue_type}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="task">Task</option>
                                    <option value="bug">Bug</option>
                                    <option value="story">Story</option>
                                    <option value="improvement">Improvement</option>
                                    <option value="sub_task">Sub-task</option>
                                </select>
                            </div>
                            <div>
                                <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                                    Status
                                </label>
                                <select
                                    id="status"
                                    name="status"
                                    value={formData.status}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="new">New</option>
                                    <option value="in_progress">In Progress</option>
                                    <option value="review">Review</option>
                                    <option value="done">Done</option>
                                    <option value="closed">Closed</option>
                                    <option value="wont_fix">Won't Fix</option>
                                </select>
                            </div>
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
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Description
                            </label>
                            <RichTextEditor
                                content={formData.description || ''}
                                onChange={(content) => handleRichTextChange('description', content)}
                                placeholder="Detailed description..."
                                minHeight="200px"
                            />
                        </div>
                    </div>

                    {/* Details Grid */}
                    <div className="border-t border-gray-100 pt-6">
                        <h3 className="text-sm font-medium text-gray-900 mb-4 uppercase tracking-wide">Details</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <UserPicker
                                projectId={issue.project_id}
                                value={formData.assignee_id ?? undefined}
                                onChange={(userId) => setFormData(prev => ({ ...prev, assignee_id: userId }))}
                                label="Assignee"
                            />

                            <ComponentPicker
                                projectId={issue.project_id}
                                value={formData.component_id ?? undefined}
                                onChange={(id) => setFormData(prev => ({ ...prev, component_id: id }))}
                                label="Component"
                            />

                            <SprintPicker
                                projectId={issue.project_id}
                                value={formData.sprint_id ?? undefined}
                                onChange={(id) => setFormData(prev => ({ ...prev, sprint_id: id }))}
                                label="Sprint"
                            />

                            <div className="col-span-2">
                                <LabelPicker
                                    projectId={issue.project_id}
                                    value={formData.label_ids || []}
                                    onChange={(ids) => setFormData(prev => ({ ...prev, label_ids: ids }))}
                                    label="Labels"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Bug Specifics */}
                    {isBug && (
                        <div className="border-t border-gray-100 pt-6 space-y-4">
                            <h3 className="text-sm font-medium text-red-700 mb-2 uppercase tracking-wide">Bug Verification</h3>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Reproduction Steps</label>
                                <RichTextEditor
                                    content={formData.repro_steps || ''}
                                    onChange={(c) => handleRichTextChange('repro_steps', c)}
                                    minHeight="100px"
                                    placeholder="Steps to reproduce the bug..."
                                />
                            </div>

                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                                    <select
                                        name="severity"
                                        value={formData.severity || 'major'}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    >
                                        <option value="blocker">Blocker</option>
                                        <option value="critical">Critical</option>
                                        <option value="major">Major</option>
                                        <option value="minor">Minor</option>
                                        <option value="trivial">Trivial</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Environment</label>
                                    <input
                                        type="text"
                                        name="environment"
                                        value={formData.environment || ''}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                        placeholder="e.g. Chrome 120, macOS 14.2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Found In Version</label>
                                    <input
                                        type="text"
                                        name="affected_version"
                                        value={formData.affected_version || ''}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                        placeholder="e.g. 1.2.0"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Planning */}
                    <div className="border-t border-gray-100 pt-6">
                        <h3 className="text-sm font-medium text-gray-900 mb-4 uppercase tracking-wide">Planning</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Story Points</label>
                                <input
                                    type="number"
                                    name="story_points"
                                    value={formData.story_points || ''}
                                    onChange={handleInputChange}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Estimate (Hours)</label>
                                <input
                                    type="number"
                                    step="0.5"
                                    name="time_estimate_minutes"
                                    value={formData.time_estimate_minutes ? formData.time_estimate_minutes / 60 : ''}
                                    onChange={(e) => {
                                        const val = parseFloat(e.target.value);
                                        setFormData(prev => ({ ...prev, time_estimate_minutes: val ? Math.round(val * 60) : undefined }));
                                    }}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                        </div>
                    </div>

                </div>

                {/* Footer Actions */}
                <div className="border-t border-gray-200 p-4 bg-gray-50 flex items-center justify-end gap-3 sticky bottom-0">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 shadow-sm transition-all"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={submitting}
                        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:shadow-none"
                    >
                        {submitting ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </form>
        </Drawer>
    );
};
