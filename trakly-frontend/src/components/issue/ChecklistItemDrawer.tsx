import React, { useState, useEffect } from 'react';
import { ChecklistItemResponse, ChecklistItemUpdate } from '@/types';
import { issuesService } from '@/lib/services/issues.service';
import { Drawer } from '@/components/ui/Drawer';
import { UserPicker } from '@/components/ui/UserPicker';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import toast from 'react-hot-toast';

interface ChecklistItemDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    issueId: string;
    checklistId: string;
    item: ChecklistItemResponse;
    projectId: string;
    onUpdate: (updatedItem: ChecklistItemResponse) => void;
}

export const ChecklistItemDrawer: React.FC<ChecklistItemDrawerProps> = ({
    isOpen,
    onClose,
    issueId,
    checklistId,
    item,
    projectId,
    onUpdate,
}) => {
    const [content, setContent] = useState(item.content);
    const [description, setDescription] = useState(item.description || '');
    const [assigneeId, setAssigneeId] = useState(item.assignee_id || '');
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        setContent(item.content);
        setDescription(item.description || '');
        setAssigneeId(item.assignee_id || '');
    }, [item]);

    const handleUpdate = async (updates: Partial<ChecklistItemUpdate>) => {
        try {
            setSaving(true);
            const res = await issuesService.updateChecklistItem(issueId, checklistId, item.id, updates);
            onUpdate(res.data);
            if (updates.content) setContent(res.data.content);
            if (updates.description !== undefined) setDescription(res.data.description || '');
            if (updates.assignee_id !== undefined) setAssigneeId(res.data.assignee_id || '');
        } catch (error) {
            toast.error('Failed to update item');
        } finally {
            setSaving(false);
        }
    };

    return (
        <Drawer isOpen={isOpen} onClose={onClose} title="Item Details" size="lg">
            <div className="flex flex-col h-full bg-white">
                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    {/* Title / Content */}
                    <div className="space-y-1">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Item Name</label>
                        <input
                            type="text"
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            onBlur={() => content !== item.content && handleUpdate({ content })}
                            className="w-full text-xl font-bold text-gray-900 border-none px-0 focus:ring-0 placeholder-gray-400"
                            placeholder="What needs to be done?"
                        />
                    </div>

                    {/* Status & Assignment */}
                    <div className="grid grid-cols-2 gap-8 py-4 border-y border-gray-50">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Workflow Status</label>
                            <select
                                value={item.status}
                                onChange={(e) => handleUpdate({ status: e.target.value as any })}
                                disabled={item.status === 'qa_checked'}
                                className={`w-full px-3 py-2 border border-gray-200 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    item.status === 'qa_checked' ? 'bg-gray-50 cursor-not-allowed opacity-75' : ''
                                }`}
                            >
                                <option value="pending" className="text-gray-700">⏸️ Pending</option>
                                <option value="in_progress" className="text-blue-700">🔄 In Progress</option>
                                <option value="dev_done" className="text-purple-700">✅ Dev Done</option>
                                <option value="qa_checked" className="text-green-700">🎯 QA Checked (Locked)</option>
                            </select>
                            {item.status === 'qa_checked' && (
                                <p className="text-[10px] text-amber-600 flex items-center gap-1 mt-1">
                                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                                    </svg>
                                    Locked after QA approval
                                </p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <UserPicker
                                projectId={projectId}
                                value={assigneeId}
                                onChange={(id) => id !== item.assignee_id && handleUpdate({ assignee_id: id })}
                                label="Assignee"
                                placeholder={item.status === 'qa_checked' ? 'Locked' : 'Unassigned'}
                            />
                        </div>
                    </div>

                    {/* Description */}
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Description</label>
                            {saving && <span className="text-[10px] text-blue-500 animate-pulse font-medium">Auto-saving...</span>}
                        </div>
                        <RichTextEditor
                            content={description}
                            onChange={(newDesc) => setDescription(newDesc)}
                            onBlur={() => description !== (item.description || '') && handleUpdate({ description })}
                            placeholder="Add detailed instructions, bug details, or Acceptance Criteria..."
                            minHeight="300px"
                        />
                    </div>
                </div>

                {/* Footer with Save Button */}
                <div className="border-t border-gray-100 bg-white">
                    <div className="p-4 flex items-center justify-between">
                        <div className="flex flex-col text-[10px] text-gray-400">
                            <span>Created {new Date(item.created_at).toLocaleString()}</span>
                            <span>Updated {new Date(item.updated_at).toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-3">
                            {saving && (
                                <span className="text-xs text-blue-600 flex items-center gap-2">
                                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Saving...
                                </span>
                            )}
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                            >
                                Done
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </Drawer>
    );
};
