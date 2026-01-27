import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { sprintsService } from '@/lib/services/sprints.service';
import { issuesService } from '@/lib/services/issues.service';
import { projectsService } from '@/lib/services/projects.service';
import { SprintResponse, IssueResponse, WorkflowColumnResponse } from '@/types';
import { SprintStatusBadge } from '@/components/sprint/SprintStatusBadge';
import { KanbanBoard } from '@/components/issue/KanbanBoard';
import { CreateIssueDrawer } from '@/components/issue/CreateIssueDrawer';
import toast from 'react-hot-toast';

export const SprintBoardPage: React.FC = () => {
  const { projectId, sprintId } = useParams<{ projectId: string; sprintId: string }>();
  const navigate = useNavigate();

  const [sprint, setSprint] = useState<SprintResponse | null>(null);
  const [issues, setIssues] = useState<IssueResponse[]>([]);
  const [workflowColumns, setWorkflowColumns] = useState<WorkflowColumnResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDrawerOpen, setIsCreateDrawerOpen] = useState(false);

  useEffect(() => {
    loadSprintAndIssues();
  }, [sprintId]);

  const loadSprintAndIssues = async () => {
    if (!sprintId || !projectId) return;

    try {
      setLoading(true);

      // Fetch project with workflow template
      const projectResponse = await projectsService.getProject(projectId);

      // Extract workflow columns
      if (projectResponse.data.workflow_template?.columns) {
        setWorkflowColumns(projectResponse.data.workflow_template.columns);
      }

      // Fetch all sprints and find the one we need
      const sprintsResponse = await sprintsService.list(projectId, true);
      const foundSprint = sprintsResponse.data.find(s => s.id === sprintId);

      if (!foundSprint) {
        throw new Error('Sprint not found');
      }

      // Fetch issues filtered by sprint_id
      const issuesResponse = await issuesService.listIssues({
        project_id: projectId,
        sprint_id: sprintId
      });

      setSprint(foundSprint);
      setIssues(issuesResponse.data);
    } catch (error: any) {
      toast.error(error.message || 'Failed to load sprint');
      navigate(`/projects/${projectId}/sprints`);
    } finally {
      setLoading(false);
    }
  };

  const handleIssueClick = (issueKey: string) => {
    navigate(`/projects/${projectId}/issues/${issueKey}`);
  };

  const handleUpdateStatus = async (issueId: string, newColumnId: string) => {
    // Store the previous state for rollback
    const previousIssues = [...issues];

    // Optimistic update: Update UI immediately BEFORE API call
    setIssues(prevIssues =>
      prevIssues.map(issue =>
        issue.id === issueId ? { ...issue, workflow_column_id: newColumnId } : issue
      )
    );

    try {
      // Update the issue's workflow column
      await issuesService.updateIssue(issueId, { workflow_column_id: newColumnId });
      toast.success('Task moved successfully');
    } catch (error: any) {
      // Rollback on error: restore previous state
      setIssues(previousIssues);
      toast.error(error.message || 'Failed to move task');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!sprint) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Sprint not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sprint Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900">{sprint.name}</h1>
              <SprintStatusBadge status={sprint.status} />
            </div>
            <p className="text-sm text-gray-600 mb-3">
              {formatDate(sprint.start_date)} - {formatDate(sprint.end_date)}
            </p>
            {sprint.goal && (
              <p className="text-sm text-gray-700 mb-4">{sprint.goal}</p>
            )}
            <div className="flex items-center gap-6 text-sm">
              <div>
                <span className="text-gray-600">Total Tasks:</span>{' '}
                <span className="font-semibold text-gray-900">{sprint.issue_count}</span>
              </div>
              <div>
                <span className="text-gray-600">Completed:</span>{' '}
                <span className="font-semibold text-green-600">{sprint.completed_issue_count}</span>
              </div>
              <div>
                <span className="text-gray-600">Remaining:</span>{' '}
                <span className="font-semibold text-orange-600">
                  {sprint.issue_count - sprint.completed_issue_count}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsCreateDrawerOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Task
            </button>
            <button
              onClick={() => navigate(`/projects/${projectId}/sprints`)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              ← Back to Sprints
            </button>
          </div>
        </div>
      </div>

      {/* Kanban Board with Drag & Drop */}
      <div className="bg-white rounded-lg shadow p-6">
        <KanbanBoard
          issues={issues}
          columns={workflowColumns}
          onUpdateStatus={handleUpdateStatus}
          onIssueClick={handleIssueClick}
        />
      </div>

      {/* Create Task Drawer with Sprint pre-selected */}
      <CreateIssueDrawer
        isOpen={isCreateDrawerOpen}
        onClose={() => setIsCreateDrawerOpen(false)}
        projectId={projectId!}
        defaultSprintId={sprintId}
        onSuccess={() => {
          setIsCreateDrawerOpen(false);
          loadSprintAndIssues();
        }}
      />
    </div>
  );
};
