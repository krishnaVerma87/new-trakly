import React, { useState } from 'react';

import { IssueTypeIcon } from '@/components/issue/IssueTypeIcon';
import { IssueStatusBadge } from '@/components/issue/IssueStatusBadge';

interface LinkedIssue {
    id: string;
    issue_key: string;
    title: string;
    issue_type: string; // 'bug' | 'task' ...
    status: string;
    link_type: string; // 'blocks', 'duplicates', etc.
}

interface IssueLinksProps {
    issueId: string;
    projectId: string;
    links: LinkedIssue[]; // Pass from parent for now
}

export const IssueLinks: React.FC<IssueLinksProps> = ({ links = [] }) => {
    const [isAdding, setIsAdding] = useState(false);

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-50 to-white px-5 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                    <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    Linked Tasks
                </h3>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="text-xs font-medium text-blue-600 hover:text-blue-800"
                >
                    + Add Link
                </button>
            </div>

            {isAdding && (
                <div className="p-4 bg-gray-50 border-b border-gray-200">
                    <p className="text-xs text-gray-500 italic">Link search implementation coming soon...</p>
                </div>
            )}

            <div className="divide-y divide-gray-100">
                {links.length === 0 ? (
                    <div className="p-4 text-center text-sm text-gray-400 italic">
                        No linked tasks
                    </div>
                ) : (
                    links.map((link) => (
                        <div key={link.id} className="p-3 hover:bg-gray-50 transition-colors flex items-center justify-between group">
                            <div className="flex items-center gap-3">
                                <div className="bg-gray-100 px-2 py-1 rounded text-xs font-medium text-gray-600 w-24 text-center">
                                    {link.link_type.replace('_', ' ')}
                                </div>
                                <IssueTypeIcon type={link.issue_type as any} className="w-4 h-4" />
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-medium text-blue-600 hover:underline cursor-pointer">
                                            {link.issue_key}
                                        </span>
                                        <span className="text-xs text-gray-500 line-clamp-1">{link.title}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <IssueStatusBadge status={link.status as any} />
                                <button className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
