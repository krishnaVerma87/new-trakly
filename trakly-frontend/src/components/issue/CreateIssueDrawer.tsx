import React, { useState, useEffect } from 'react';
import { issuesService } from '@/lib/services/issues.service';
import { IssueCreate, SimilarIssueResponse } from '@/types';
import { Drawer } from '@/components/ui/Drawer';
import { DuplicateWarning } from '@/components/issue/DuplicateWarning';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import { UserPicker } from '@/components/ui/UserPicker';
import { ComponentPicker } from '@/components/ui/ComponentPicker';
import { LabelPickerWithAutoCreate } from '@/components/ui/LabelPickerWithAutoCreate';
import { SprintPicker } from '@/components/ui/SprintPicker';
import { FeaturePicker } from '@/components/ui/FeaturePicker';
import { FileUpload } from '@/components/ui/FileUpload';
import apiClient from '@/lib/api';
import toast from 'react-hot-toast';

interface CreateIssueDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    projectId: string;
    onSuccess: () => void;
    defaultSprintId?: string;
    cloneData?: Partial<IssueCreate>;
}

export const CreateIssueDrawer: React.FC<CreateIssueDrawerProps> = ({
    isOpen,
    onClose,
    projectId,
    onSuccess,
    defaultSprintId,
    cloneData,
}) => {
    const [formData, setFormData] = useState<Partial<IssueCreate>>({
        project_id: projectId,
        issue_type: 'task',
        priority: 'medium',
        title: '',
        description: '',
        label_ids: [],
        sprint_id: defaultSprintId,
    });

    const [_files, setFiles] = useState<File[]>([]);
    const [similarIssues, setSimilarIssues] = useState<SimilarIssueResponse[]>([]);
    const [checkingDuplicates, setCheckingDuplicates] = useState(false);
    const [showDuplicateWarning, setShowDuplicateWarning] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [createAnother, setCreateAnother] = useState(false);
    const [watchIssue, setWatchIssue] = useState(true); // New feature: Watch by default
    const [pendingLabels, setPendingLabels] = useState<string[]>([]);

    // Reset form when drawer opens
    useEffect(() => {
        if (isOpen) {
            if (cloneData) {
                // Clone mode: pre-fill with cloneData
                setFormData({
                    project_id: projectId,
                    issue_type: cloneData.issue_type || 'task',
                    priority: cloneData.priority || 'medium',
                    title: cloneData.title ? `${cloneData.title} (Copy)` : '',
                    description: cloneData.description || '',
                    label_ids: cloneData.label_ids || [],
                    sprint_id: cloneData.sprint_id || defaultSprintId,
                    assignee_id: cloneData.assignee_id,
                    component_id: cloneData.component_id,
                    feature_id: cloneData.feature_id,
                    severity: cloneData.severity,
                    affected_version: cloneData.affected_version,
                    repro_steps: cloneData.repro_steps,
                    story_points: cloneData.story_points,
                    time_estimate_minutes: cloneData.time_estimate_minutes,
                });
            } else {
                // Create mode: empty form
                setFormData({
                    project_id: projectId,
                    issue_type: 'task',
                    priority: 'medium',
                    title: '',
                    description: '',
                    label_ids: [],
                    sprint_id: defaultSprintId,
                });
            }
            setFiles([]);
            setSimilarIssues([]);
            setShowDuplicateWarning(false);
            setCreateAnother(false);
            setPendingLabels([]);
        }
    }, [isOpen, projectId, defaultSprintId, cloneData]);

    // Debounced duplicate check
    useEffect(() => {
        const timer = setTimeout(() => {
            if (formData.title && formData.title.length > 3 && isOpen) {
                checkForDuplicates();
            }
        }, 1000);

        return () => clearTimeout(timer);
    }, [formData.title, isOpen]);

    const checkForDuplicates = async () => {
        if (!formData.title || !projectId) return;

        try {
            setCheckingDuplicates(true);
            const response = await issuesService.checkDuplicates({
                project_id: projectId,
                title: formData.title,
                description: typeof formData.description === 'string' ? formData.description : '',
            });

            const duplicates = response.data.similar_issues.filter(
                (issue) => issue.similarity_score >= 0.7
            );

            setSimilarIssues(duplicates);
            setShowDuplicateWarning(duplicates.length > 0);
        } catch (error: any) {
            console.error('Duplicate check failed:', error);
        } finally {
            setCheckingDuplicates(false);
        }
    };

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const { name, value, type } = e.target;

        if (type === 'checkbox') {
            const checked = (e.target as HTMLInputElement).checked;
            setFormData((prev) => ({ ...prev, [name]: checked }));
        } else if (type === 'number') {
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

        if (!formData.title || !formData.description) {
            toast.error('Title and description are required');
            return;
        }

        try {
            setSubmitting(true);

            // Create any pending labels first
            let finalLabelIds = formData.label_ids || [];
            if (pendingLabels.length > 0) {
                const PRESET_COLORS = [
                    '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
                    '#8B5CF6', '#EC4899', '#14B8A6', '#6366F1',
                ];

                const newLabelIds = await Promise.all(
                    pendingLabels.map(async (labelName, index) => {
                        try {
                            const response = await apiClient.post(`/projects/${projectId}/labels`, {
                                name: labelName,
                                color: PRESET_COLORS[index % PRESET_COLORS.length],
                            });
                            return response.data.id;
                        } catch (error) {
                            console.error(`Failed to create label: ${labelName}`, error);
                            return null;
                        }
                    })
                );

                // Filter out any failed label creations and add to existing labels
                finalLabelIds = [...finalLabelIds, ...newLabelIds.filter(id => id !== null)];
            }

            // Create issue with all label IDs (existing + newly created)
            await issuesService.createIssue({
                ...formData,
                label_ids: finalLabelIds,
            } as IssueCreate);

            toast.success('Task created successfully');
            onSuccess();

            if (createAnother) {
                // Reset form but keep some context if needed (removed for clean slate)
                setFormData({
                    project_id: projectId,
                    issue_type: formData.issue_type, // Keep type
                    priority: 'medium',
                    title: '',
                    description: '',
                    label_ids: [],
                });
                setFiles([]);
                setSimilarIssues([]);
                setShowDuplicateWarning(false);
                setPendingLabels([]);
                // Don't close drawer
            } else {
                onClose();
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create task');
        } finally {
            setSubmitting(false);
        }
    };

    const isBug = formData.issue_type === 'bug';

    return (
        <Drawer isOpen={isOpen} onClose={onClose} title={cloneData ? "Clone Task" : "Create New Task"} size="xl">
            <form onSubmit={handleSubmit} className="flex flex-col h-full">
                <div className="flex-1 overflow-y-auto p-6 space-y-6">

                    {/* Warning Area */}
                    {showDuplicateWarning && (
                        <DuplicateWarning
                            similarIssues={similarIssues}
                            onDismiss={() => setShowDuplicateWarning(false)}
                        />
                    )}

                    {/* Main Inputs */}
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                                Title <span className="text-red-500">*</span>
                            </label>
                            <div className="relative">
                                <input
                                    type="text"
                                    id="title"
                                    name="title"
                                    required
                                    autoFocus
                                    value={formData.title}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Summary of the work"
                                />
                                {checkingDuplicates && (
                                    <div className="absolute right-3 top-2.5">
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
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
                                Description <span className="text-red-500">*</span>
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
                                projectId={projectId}
                                value={formData.assignee_id}
                                onChange={(userId) => setFormData(prev => ({ ...prev, assignee_id: userId }))}
                                label="Assignee"
                            />

                            <ComponentPicker
                                projectId={projectId}
                                value={formData.component_id}
                                onChange={(id) => setFormData(prev => ({ ...prev, component_id: id }))}
                                label="Component"
                            />

                            <SprintPicker
                                projectId={projectId}
                                value={formData.sprint_id}
                                onChange={(id) => setFormData(prev => ({ ...prev, sprint_id: id }))}
                                label="Sprint"
                            />

                            <div className="col-span-2">
                                <LabelPickerWithAutoCreate
                                    projectId={projectId}
                                    value={formData.label_ids || []}
                                    onChange={(ids) => setFormData(prev => ({ ...prev, label_ids: ids }))}
                                    onPendingLabelsChange={setPendingLabels}
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
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
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
                                    </select>
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

                    {/* Collapsible Advanced: Relationships, Attachments */}
                    <div className="border-t border-gray-100 pt-6">
                        <details className="group">
                            <summary className="flex justify-between items-center font-medium cursor-pointer list-none text-gray-700">
                                <span className="flex items-center gap-2">
                                    <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                    </svg>
                                    Feature Link & Attachments
                                </span>
                                <span className="transition group-open:rotate-180">
                                    <svg fill="none" height="24" shapeRendering="geometricPrecision" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
                                </span>
                            </summary>
                            <div className="text-neutral-600 mt-3 group-open:animate-fadeIn grid grid-cols-1 gap-4">
                                <FeaturePicker
                                    projectId={projectId}
                                    value={formData.feature_id}
                                    onChange={(id) => setFormData(prev => ({ ...prev, feature_id: id }))}
                                    label="Link to Feature"
                                />

                                <FileUpload
                                    onFilesChange={setFiles}
                                    label="Attachments"
                                    maxFiles={5}
                                />
                            </div>
                        </details>
                    </div>

                </div>

                {/* Footer Actions */}
                <div className="border-t border-gray-200 p-4 bg-gray-50 flex items-center justify-between sticky bottom-0">
                    <div className="flex items-center gap-4">
                        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                checked={createAnother}
                                onChange={(e) => setCreateAnother(e.target.checked)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            Create another
                        </label>

                        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                checked={watchIssue}
                                onChange={(e) => setWatchIssue(e.target.checked)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            Watch
                        </label>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 shadow-sm transition-all"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={submitting || checkingDuplicates}
                            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:shadow-none"
                        >
                            {submitting ? 'Creating...' : 'Create'}
                        </button>
                    </div>
                </div>
            </form>
        </Drawer>
    );
};
