import React from 'react';
import { IssueResponse } from '@/types';
import { IssueTypeIcon } from '@/components/issue/IssueTypeIcon';
import { IssuePriorityBadge } from '@/components/issue/IssuePriorityBadge';

interface IssueCardProps {
    issue: IssueResponse;
    onClick?: () => void;
    className?: string; // Allow passing extra classes like drag styles
    style?: React.CSSProperties; // Allow passing drag styles
}

export const IssueCard: React.FC<IssueCardProps> = ({ issue, onClick, className, style }) => {
    return (
        <div
            onClick={onClick}
            className={`
        bg-white p-4 rounded-lg shadow-sm border border-gray-200 
        hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group
        ${className || ''}
      `}
            style={style}
        >
            <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-mono text-gray-500 group-hover:text-blue-600 transition-colors">
                    {issue.issue_key}
                </span>
                <IssuePriorityBadge priority={issue.priority} />
            </div>

            <h4 className="text-sm font-medium text-gray-900 mb-3 line-clamp-2 leading-relaxed">
                {issue.title}
            </h4>

            <div className="flex items-center justify-between mt-auto pt-2 border-t border-gray-50">
                <IssueTypeIcon type={issue.issue_type} className="w-4 h-4 text-gray-400" />

                <div className="flex items-center gap-2">
                    {/* Assignee Avatar */}
                    {issue.assignee_id ? (
                        <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-xs text-blue-700 font-medium">
                            {issue.assignee_id[0]?.toUpperCase()}
                        </div>
                    ) : (
                        <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center border border-gray-200 border-dashed">
                            <span className="text-gray-400 text-[10px]">+</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
