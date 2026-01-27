import React, { useMemo } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { IssueResponse, WorkflowColumnResponse } from '@/types';
import { IssueTypeIcon } from '@/components/issue/IssueTypeIcon';
import { IssuePriorityBadge } from '@/components/issue/IssuePriorityBadge';

interface KanbanBoardProps {
    issues: IssueResponse[];
    columns?: WorkflowColumnResponse[];
    onUpdateStatus: (issueId: string, newColumnId: string) => void;
    onIssueClick: (issueId: string) => void;
}

// Fallback columns if no workflow template is configured
const DEFAULT_COLUMNS: WorkflowColumnResponse[] = [
    { id: 'default-todo', name: 'To Do', position: 0, template_id: '', created_at: '', updated_at: '' },
    { id: 'default-progress', name: 'In Progress', position: 1, template_id: '', created_at: '', updated_at: '' },
    { id: 'default-review', name: 'Review', position: 2, template_id: '', created_at: '', updated_at: '' },
    { id: 'default-done', name: 'Done', position: 3, template_id: '', created_at: '', updated_at: '' },
];

export const KanbanBoard: React.FC<KanbanBoardProps> = ({ issues, columns = DEFAULT_COLUMNS, onUpdateStatus, onIssueClick }) => {
    // Sort columns by position
    const sortedColumns = useMemo(() => {
        return [...columns].sort((a, b) => a.position - b.position);
    }, [columns]);

    // Group issues by workflow column
    const groupedIssues = useMemo(() => {
        const grouped: Record<string, IssueResponse[]> = {};

        // Initialize groups for all columns
        sortedColumns.forEach(col => {
            grouped[col.id] = [];
        });

        // Group issues by their workflow_column_id
        issues.forEach(issue => {
            const columnId = issue.workflow_column_id || sortedColumns[0]?.id;
            if (columnId && grouped[columnId]) {
                grouped[columnId].push(issue);
            }
        });

        return grouped;
    }, [issues, sortedColumns]);

    const onDragEnd = (result: DropResult) => {
        const { destination, source, draggableId } = result;

        if (!destination) return;

        if (
            destination.droppableId === source.droppableId &&
            destination.index === source.index
        ) {
            return;
        }

        const newColumnId = destination.droppableId;
        onUpdateStatus(draggableId, newColumnId);
    };

    return (
        <DragDropContext onDragEnd={onDragEnd}>
            <div className="flex h-full gap-6 overflow-x-auto pb-4">
                {sortedColumns.map(column => (
                    <div
                        key={column.id}
                        className="flex-shrink-0 w-80 flex flex-col bg-gray-50/50 rounded-xl border border-gray-100 max-h-full"
                        style={column.color ? { borderTopColor: column.color, borderTopWidth: '4px' } : undefined}
                    >
                        {/* Column Header */}
                        <div className="p-4 flex items-center justify-between border-b border-gray-100 bg-white/50 backdrop-blur-sm rounded-t-xl sticky top-0 z-10">
                            <div className="flex items-center gap-2">
                                <h3 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">
                                    {column.name}
                                </h3>
                                {column.wip_limit && (
                                    <span className="text-xs text-gray-500">
                                        (WIP: {column.wip_limit})
                                    </span>
                                )}
                            </div>
                            <span className="bg-gray-100 text-gray-600 text-xs font-medium px-2 py-0.5 rounded-full">
                                {groupedIssues[column.id]?.length || 0}
                            </span>
                        </div>

                        {/* Droppable Area */}
                        <Droppable droppableId={column.id}>
                            {(provided, snapshot) => (
                                <div
                                    {...provided.droppableProps}
                                    ref={provided.innerRef}
                                    className={`flex-1 p-3 overflow-y-auto space-y-3 min-h-[150px] transition-colors ${snapshot.isDraggingOver ? 'bg-blue-50/50' : ''
                                        }`}
                                >
                                    {groupedIssues[column.id]?.map((issue, index) => (
                                        <Draggable key={issue.id} draggableId={issue.id} index={index}>
                                            {(provided, snapshot) => (
                                                <div
                                                    ref={provided.innerRef}
                                                    {...provided.draggableProps}
                                                    {...provided.dragHandleProps}
                                                    onClick={() => onIssueClick(issue.issue_key)}
                                                    className={`
                            bg-white p-4 rounded-lg shadow-sm border border-gray-200 
                            hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group
                            ${snapshot.isDragging ? 'shadow-lg ring-2 ring-blue-400 rotate-2' : ''}
                          `}
                                                    style={provided.draggableProps.style}
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
                                                            {/* Assignee Avatar (Placeholder if relation missing in list view) */}
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
                                            )}
                                        </Draggable>
                                    ))}
                                    {provided.placeholder}
                                </div>
                            )}
                        </Droppable>
                    </div>
                ))}
            </div>
        </DragDropContext>
    );
};
