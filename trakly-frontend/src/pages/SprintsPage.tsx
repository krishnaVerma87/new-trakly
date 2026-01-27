import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { sprintsService } from '@/lib/services/sprints.service';
import { issuesService } from '@/lib/services/issues.service';
import { SprintWithIssuesResponse, IssueResponse } from '@/types';
import { IssueCard } from '@/components/issue/IssueCard';
import { CreateSprintModal } from '@/components/sprint/CreateSprintModal';
import { StartSprintModal } from '@/components/sprint/StartSprintModal';
import { CompleteSprintModal } from '@/components/sprint/CompleteSprintModal';
import { SprintStats } from '@/components/sprint/SprintStats';
import { IssueTypeIcon } from '@/components/issue/IssueTypeIcon';
import { IssueStatusBadge } from '@/components/issue/IssueStatusBadge';
import { IssuePriorityBadge } from '@/components/issue/IssuePriorityBadge';
import toast from 'react-hot-toast';

export const SprintsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [sprints, setSprints] = useState<SprintWithIssuesResponse[]>([]);
  const [backlogIssues, setBacklogIssues] = useState<IssueResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [showAllSprints, setShowAllSprints] = useState(false);
  const [showBacklog, setShowBacklog] = useState(true);
  const [selectedIssues, setSelectedIssues] = useState<Set<string>>(new Set());
  const [movingIssues, setMovingIssues] = useState(false);

  // Lifecycle Modals
  const [startSprintData, setStartSprintData] = useState<any | null>(null);
  const [completeSprintData, setCompleteSprintData] = useState<any | null>(null);

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    await Promise.all([loadSprints(), loadBacklog()]);
  };

  const loadSprints = async () => {
    try {
      setLoading(true);
      if (projectId) {
        const response = await sprintsService.list(projectId, false); // Don't include completed sprints by default
        setSprints(response.data as any);
      }
    } catch (error) {
      toast.error('Failed to load sprints');
    } finally {
      setLoading(false);
    }
  };

  const loadBacklog = async () => {
    try {
      if (projectId) {
        const response = await issuesService.listIssues({
          project_id: projectId,
          include_backlog: true,
        });
        setBacklogIssues(response.data);
      }
    } catch (error) {
      console.error('Failed to load backlog:', error);
    }
  };

  const toggleIssueSelection = (issueId: string) => {
    const newSelection = new Set(selectedIssues);
    if (newSelection.has(issueId)) {
      newSelection.delete(issueId);
    } else {
      newSelection.add(issueId);
    }
    setSelectedIssues(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedIssues.size === backlogIssues.length) {
      setSelectedIssues(new Set());
    } else {
      setSelectedIssues(new Set(backlogIssues.map(i => i.id)));
    }
  };

  const moveIssuesToSprint = async (sprintId: string) => {
    if (selectedIssues.size === 0) {
      toast.error('Please select at least one task');
      return;
    }

    try {
      setMovingIssues(true);

      // Update each selected issue
      await Promise.all(
        Array.from(selectedIssues).map(issueId =>
          issuesService.updateIssue(issueId, { sprint_id: sprintId })
        )
      );

      toast.success(`Moved ${selectedIssues.size} task(s) to sprint`);
      setSelectedIssues(new Set());
      await loadData(); // Reload both sprints and backlog
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to move tasks');
    } finally {
      setMovingIssues(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Separate active sprint from others
  const activeSprint = sprints.find(s => s.status === 'active');
  const otherSprints = sprints.filter(s => s.status !== 'active');

  const renderSprintCard = (sprint: SprintWithIssuesResponse, isActive: boolean = false) => (
    <div
      key={sprint.id}
      className={`bg-gray-50 rounded-xl border cursor-pointer transition-all ${
        isActive
          ? 'border-blue-400 ring-4 ring-blue-100 shadow-lg'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
      }`}
      onClick={() => navigate(`/projects/${projectId}/sprints/${sprint.id}/board`)}
    >
      {/* Sprint Header */}
      <div className="p-4 border-b border-gray-200 bg-white rounded-t-xl flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className={`${isActive ? 'text-xl' : 'text-lg'} font-bold text-gray-900`}>{sprint.name}</h3>
            {sprint.status === 'active' && (
              <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-bold uppercase tracking-wide">
                Active
              </span>
            )}
            {sprint.status === 'planned' && (
              <span className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full font-semibold uppercase tracking-wide">
                Planned
              </span>
            )}
            <span className="text-sm text-gray-500 font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">
              {sprint.issue_count || 0} tasks
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1 flex gap-4">
            <span>{sprint.start_date} - {sprint.end_date}</span>
            {sprint.goal && <span className="truncate max-w-md">Goal: {sprint.goal}</span>}
          </div>
        </div>

        <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
          {sprint.status === 'planned' && (
            <button
              onClick={() => setStartSprintData(sprint)}
              className="text-sm bg-blue-50 text-blue-600 px-3 py-1.5 rounded-md hover:bg-blue-100 font-medium transition-colors"
            >
              Start Sprint
            </button>
          )}
          {sprint.status === 'active' && (
            <button
              onClick={() => setCompleteSprintData(sprint)}
              className="text-sm bg-green-50 text-green-700 px-3 py-1.5 rounded-md hover:bg-green-100 font-medium transition-colors"
            >
              Complete Sprint
            </button>
          )}
        </div>
      </div>

      {/* Active Sprint Stats */}
      {sprint.status === 'active' && (
        <div className="p-4 bg-white border-b border-gray-100">
          <SprintStats sprintId={sprint.id} />
        </div>
      )}

      {/* Tasks List (simplified for this view) */}
      <div className="p-4">
        {(sprint.issues || []).length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-lg">
            No tasks in this sprint. Drag tasks from backlog (coming soon).
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {(sprint.issues || []).map(issue => (
              <IssueCard key={issue.id} issue={issue} />
            ))}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 px-6 pt-6 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sprints & Backlog</h1>
          <p className="text-sm text-gray-500 mt-1">Plan and manage your work iterations</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Create Sprint
          </button>
        </div>
      </div>

      {/* Sprints List */}
      <div className="flex-1 overflow-x-auto overflow-y-auto px-6 pb-6 space-y-6">
        {sprints.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="w-16 h-16 mb-4 rounded-full bg-gray-100 flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No sprints yet</h3>
            <p className="text-sm text-gray-500 mb-4">Create your first sprint to start planning your work iterations</p>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create First Sprint
            </button>
          </div>
        ) : (
          <>
            {/* Active Sprint - Prominent at Top */}
            {activeSprint && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                    <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Active Sprint
                  </h2>
                </div>
                {renderSprintCard(activeSprint, true)}
              </div>
            )}

            {/* Backlog Section */}
            <div className="border-t border-gray-200 pt-6">
              <button
                onClick={() => setShowBacklog(!showBacklog)}
                className="flex items-center justify-between w-full mb-4 text-left group"
              >
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                  <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  Backlog ({backlogIssues.length} tasks)
                </h2>
                <span className={`transition-transform ${showBacklog ? 'rotate-180' : ''}`}>
                  <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </span>
              </button>

              {showBacklog && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
                  {/* Backlog Actions Bar */}
                  {backlogIssues.length > 0 && (
                    <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedIssues.size === backlogIssues.length && backlogIssues.length > 0}
                            onChange={toggleSelectAll}
                            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700">
                            {selectedIssues.size > 0 ? `${selectedIssues.size} selected` : 'Select all'}
                          </span>
                        </label>

                        {selectedIssues.size > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-500">Move to:</span>
                            <select
                              onChange={(e) => {
                                if (e.target.value) {
                                  moveIssuesToSprint(e.target.value);
                                  e.target.value = '';
                                }
                              }}
                              disabled={movingIssues}
                              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                            >
                              <option value="">Select Sprint...</option>
                              {sprints.map(sprint => (
                                <option key={sprint.id} value={sprint.id}>
                                  {sprint.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => setSelectedIssues(new Set())}
                        className="text-sm text-gray-500 hover:text-gray-700"
                      >
                        Clear selection
                      </button>
                    </div>
                  )}

                  {/* Backlog Tasks List */}
                  <div className="p-4">
                    {backlogIssues.length === 0 ? (
                      <div className="text-center py-12 text-gray-400">
                        <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <p className="text-sm">No tasks in backlog</p>
                        <p className="text-xs text-gray-400 mt-1">All tasks are assigned to sprints</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {backlogIssues.map(issue => (
                          <div
                            key={issue.id}
                            className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${
                              selectedIssues.has(issue.id)
                                ? 'bg-blue-50 border-blue-200'
                                : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={selectedIssues.has(issue.id)}
                              onChange={() => toggleIssueSelection(issue.id)}
                              className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <div
                              className="flex-1 cursor-pointer"
                              onClick={() => navigate(`/projects/${projectId}/issues/${issue.issue_key}`)}
                            >
                              <div className="flex items-start gap-2">
                                <IssueTypeIcon type={issue.issue_type} />
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium text-gray-900">{issue.title}</span>
                                  </div>
                                  <div className="flex items-center gap-2 mt-1">
                                    <span className="text-xs text-gray-500 font-mono">{issue.issue_key}</span>
                                    <IssueStatusBadge status={issue.status} />
                                    <IssuePriorityBadge priority={issue.priority} />
                                    {issue.assignee && (
                                      <span className="text-xs text-gray-500">
                                        {issue.assignee.full_name}
                                      </span>
                                    )}
                                    {issue.labels && issue.labels.length > 0 && (
                                      <div className="flex gap-1">
                                        {issue.labels.map(label => (
                                          <span
                                            key={label.id}
                                            className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium"
                                            style={{
                                              backgroundColor: label.color + '20',
                                              color: label.color,
                                              border: `1px solid ${label.color}`,
                                            }}
                                          >
                                            {label.name}
                                          </span>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Other Sprints - Collapsible */}
            {otherSprints.length > 0 && (
              <div className="border-t border-gray-200 pt-6">
                <button
                  onClick={() => setShowAllSprints(!showAllSprints)}
                  className="flex items-center justify-between w-full mb-4 text-left group"
                >
                  <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                    <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                    Other Sprints ({otherSprints.length})
                  </h2>
                  <span className={`transition-transform ${showAllSprints ? 'rotate-180' : ''}`}>
                    <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </span>
                </button>

                {showAllSprints && (
                  <div className="space-y-4">
                    {otherSprints.map(sprint => renderSprintCard(sprint, false))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <CreateSprintModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        projectId={projectId!}
        onSuccess={loadSprints}
      />

      {startSprintData && (
        <StartSprintModal
          isOpen={!!startSprintData}
          onClose={() => setStartSprintData(null)}
          sprint={startSprintData}
          onSuccess={loadSprints}
        />
      )}

      {completeSprintData && (
        <CompleteSprintModal
          isOpen={!!completeSprintData}
          onClose={() => setCompleteSprintData(null)}
          projectId={projectId!}
          sprint={completeSprintData}
          onSuccess={loadSprints}
        />
      )}
    </div>
  );
};
