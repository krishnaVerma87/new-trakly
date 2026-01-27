import React, { useState, useEffect } from 'react';
import { ChecklistResponse, ChecklistItemResponse } from '@/types';
import { issuesService } from '@/lib/services/issues.service';
import toast from 'react-hot-toast';

import { ChecklistItemDrawer } from './ChecklistItemDrawer';

interface IssueChecklistProps {
    issueId: string;
    projectId: string;
    initialChecklists?: ChecklistResponse[];
}

export const IssueChecklist: React.FC<IssueChecklistProps> = ({ issueId, projectId, initialChecklists = [] }) => {
    const [checklists, setChecklists] = useState<ChecklistResponse[]>(initialChecklists);
    const [newGroupName, setNewGroupName] = useState('');
    const [isAddingGroup, setIsAddingGroup] = useState(false);
    const [loading, setLoading] = useState(false);

    // Drawer state
    const [selectedItem, setSelectedItem] = useState<{ item: ChecklistItemResponse; checklistId: string } | null>(null);

    useEffect(() => {
        setChecklists(initialChecklists);
    }, [initialChecklists]);

    const handleAddGroup = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newGroupName.trim()) return;

        try {
            setLoading(true);
            const res = await issuesService.createChecklist(issueId, {
                name: newGroupName,
                position: checklists.length,
            });
            setChecklists([...checklists, { ...res.data, items: [] }]);
            setNewGroupName('');
            setIsAddingGroup(false);
            toast.success('Checklist group created');
        } catch (error) {
            toast.error('Failed to create group');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteGroup = async (checklistId: string) => {
        if (!confirm('Delete this entire checklist group and all its items?')) return;

        try {
            await issuesService.deleteChecklist(issueId, checklistId);
            setChecklists(checklists.filter((c) => c.id !== checklistId));
            toast.success('Group deleted');
        } catch (error) {
            toast.error('Failed to delete group');
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">Checklists</h3>
                <button
                    onClick={() => setIsAddingGroup(true)}
                    className="text-xs font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1 transition-colors"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add Checklist
                </button>
            </div>

            {isAddingGroup && (
                <form onSubmit={handleAddGroup} className="flex gap-2">
                    <input
                        type="text"
                        value={newGroupName}
                        onChange={(e) => setNewGroupName(e.target.value)}
                        placeholder="Checklist name (e.g. QA, Design...)"
                        autoFocus
                        className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white shadow-sm"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                        Add
                    </button>
                    <button
                        type="button"
                        onClick={() => setIsAddingGroup(false)}
                        className="px-4 py-2 text-gray-600 text-sm font-medium rounded-md hover:bg-gray-100 transition-colors"
                    >
                        Cancel
                    </button>
                </form>
            )}

            {checklists.length === 0 && !isAddingGroup && (
                <div className="text-center py-6 bg-gray-50 rounded-lg border border-dashed border-gray-200">
                    <p className="text-sm text-gray-500 italic">No checklists added yet.</p>
                </div>
            )}

            <div className="space-y-10">
                {checklists.map((checklist) => (
                    <ChecklistGroup
                        key={checklist.id}
                        issueId={issueId}
                        checklist={checklist}
                        onDelete={() => handleDeleteGroup(checklist.id)}
                        onItemClick={(item) => setSelectedItem({ item, checklistId: checklist.id })}
                    />

                ))}
            </div>

            {selectedItem && (
                <ChecklistItemDrawer
                    isOpen={!!selectedItem}
                    onClose={() => setSelectedItem(null)}
                    issueId={issueId}
                    projectId={projectId}
                    checklistId={selectedItem.checklistId}
                    item={selectedItem.item}
                    onUpdate={(updatedItem) => {
                        setChecklists(prev => prev.map(c => {
                            if (c.id === selectedItem.checklistId) {
                                return { ...c, items: c.items.map(i => i.id === updatedItem.id ? updatedItem : i) };
                            }
                            return c;
                        }));
                        setSelectedItem({ ...selectedItem, item: updatedItem });
                    }}
                />
            )}
        </div>
    );
};

interface ChecklistGroupProps {
    issueId: string;
    checklist: ChecklistResponse;
    onDelete: () => void;
    onItemClick: (item: ChecklistItemResponse) => void;
}

const ChecklistGroup: React.FC<ChecklistGroupProps> = ({ issueId, checklist, onDelete, onItemClick }) => {
    const [items, setItems] = useState<ChecklistItemResponse[]>(checklist.items || []);
    const [newItemText, setNewItemText] = useState('');
    const [loading, setLoading] = useState(false);
    const [isEditingName, setIsEditingName] = useState(false);
    const [groupName, setGroupName] = useState(checklist.name);

    // Calculate progress
    const completedCount = items.filter((i) => i.is_completed).length;
    const totalCount = items.length;
    const progress = totalCount === 0 ? 0 : Math.round((completedCount / totalCount) * 100);

    const handleAddItem = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newItemText.trim()) return;

        try {
            setLoading(true);
            const res = await issuesService.addChecklistItem(issueId, checklist.id, {
                content: newItemText,
                position: items.length,
            });
            setItems([...items, res.data]);
            setNewItemText('');
        } catch (error) {
            toast.error('Failed to add item');
        } finally {
            setLoading(false);
        }
    };

    const handleToggleItem = async (itemId: string, completed: boolean) => {
        const prevItems = [...items];
        setItems(items.map((i) => (i.id === itemId ? { ...i, is_completed: completed } : i)));

        try {
            await issuesService.updateChecklistItem(issueId, checklist.id, itemId, {
                is_completed: completed,
            });
        } catch (error) {
            setItems(prevItems);
            toast.error('Failed to update status');
        }
    };

    const handleDeleteItem = async (itemId: string) => {

        const prevItems = [...items];
        setItems(items.filter((i) => i.id !== itemId));

        try {
            await issuesService.deleteChecklistItem(issueId, checklist.id, itemId);
        } catch (error) {
            setItems(prevItems);
            toast.error('Failed to delete item');
        }
    };

    const handleRenameGroup = async () => {
        if (!groupName.trim() || groupName === checklist.name) {
            setGroupName(checklist.name);
            setIsEditingName(false);
            return;
        }

        try {
            await issuesService.updateChecklist(issueId, checklist.id, { name: groupName });
            setIsEditingName(false);
            toast.success('Checklist renamed');
        } catch (error) {
            setGroupName(checklist.name);
            setIsEditingName(false);
            toast.error('Failed to rename checklist');
        }
    };

    return (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                    {isEditingName ? (
                        <input
                            type="text"
                            value={groupName}
                            onChange={(e) => setGroupName(e.target.value)}
                            onBlur={handleRenameGroup}
                            onKeyDown={(e) => e.key === 'Enter' && handleRenameGroup()}
                            autoFocus
                            className="text-sm font-semibold text-gray-900 border-b border-blue-500 focus:outline-none bg-transparent"
                        />
                    ) : (
                        <h4
                            onClick={() => setIsEditingName(true)}
                            className="text-sm font-semibold text-gray-900 hover:text-blue-600 cursor-pointer"
                        >
                            {groupName}
                        </h4>
                    )}
                    <span className="text-xs text-gray-400 font-medium px-2 py-0.5 bg-gray-100 rounded-full">
                        {completedCount}/{totalCount}
                    </span>
                </div>
                <button
                    onClick={onDelete}
                    className="text-gray-400 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-all"
                    title="Delete checklist group"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                    </svg>
                </button>
            </div>

            <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                <div
                    className={`h-full transition-all duration-500 ease-out ${progress === 100 ? 'bg-green-500' : 'bg-blue-600'}`}
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            <div className="space-y-3">
                {items.map((item) => (
                    <ChecklistItemRow
                        key={item.id}
                        item={item}
                        onToggle={(completed) => handleToggleItem(item.id, completed)}
                        onDelete={() => handleDeleteItem(item.id)}
                        onClick={() => onItemClick(item)}
                    />
                ))}

            </div>

            <form onSubmit={handleAddItem} className="pl-7">
                <input
                    type="text"
                    value={newItemText}
                    onChange={(e) => setNewItemText(e.target.value)}
                    placeholder="Add an item..."
                    className="w-full px-0 py-1 text-sm border-0 border-b border-transparent focus:border-gray-200 focus:ring-0 bg-transparent placeholder-gray-400 hover:placeholder-gray-500 transition-all italic hover:not-italic"
                    disabled={loading}
                />
            </form>
        </div>
    );
};

interface ChecklistItemRowProps {
    item: ChecklistItemResponse;
    onToggle: (completed: boolean) => void;
    onDelete: () => void;
    onClick: () => void;
}

const ChecklistItemRow: React.FC<ChecklistItemRowProps> = ({ item, onToggle, onDelete, onClick }) => {
    return (
        <div className="group border border-transparent hover:border-gray-100 hover:bg-white rounded-lg p-1 transition-all">
            <div className="flex items-center gap-3 px-2 py-1">
                <input
                    type="checkbox"
                    checked={item.is_completed}
                    onChange={(e) => onToggle(e.target.checked)}
                    className="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
                />
                <div className="flex-1 flex items-center justify-between gap-4 overflow-hidden">
                    <div
                        className={`flex-1 text-sm cursor-pointer truncate ${item.is_completed ? 'text-gray-400 line-through' : 'text-gray-700'
                            }`}
                        onClick={onClick}
                    >
                        {item.content}
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                        {/* Status Badge */}
                        {item.status && (
                            <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide ${
                                    item.status === 'pending'
                                        ? 'bg-gray-100 text-gray-600'
                                        : item.status === 'in_progress'
                                        ? 'bg-blue-100 text-blue-700'
                                        : item.status === 'dev_done'
                                        ? 'bg-purple-100 text-purple-700'
                                        : item.status === 'qa_checked'
                                        ? 'bg-green-100 text-green-700'
                                        : 'bg-gray-100 text-gray-600'
                                }`}
                                title={`Status: ${item.status.replace('_', ' ')}`}
                            >
                                {item.status === 'pending' && '⏸️'}
                                {item.status === 'in_progress' && '🔄'}
                                {item.status === 'dev_done' && '✅'}
                                {item.status === 'qa_checked' && '🎯'}
                            </span>
                        )}

                        {/* Display assignee if any */}
                        {item.assignee && (
                            <div
                                title={`Assigned to ${item.assignee.full_name}`}
                                className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-[10px] font-medium text-blue-700 border border-white"
                            >
                                {item.assignee.full_name.split(' ').map((n) => n[0]).join('')}
                            </div>
                        )}

                        {item.description && (
                            <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <title>Has description</title>
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        )}

                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                                onClick={onClick}
                                className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-blue-500 transition-colors"
                                title="Open details"
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                            </button>
                            <button
                                onClick={onDelete}
                                className="p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
