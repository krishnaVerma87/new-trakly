import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { issuesService } from '@/lib/services/issues.service';
import { projectsService } from '@/lib/services/projects.service';
import { usersService } from '@/lib/services/users.service';

import { IssueResponse, IssueStatus, Priority, UserWithRolesResponse } from '@/types';
import { IssueTypeIcon } from '@/components/issue/IssueTypeIcon';
import { IssueStatusBadge } from '@/components/issue/IssueStatusBadge';
import { IssuePriorityBadge } from '@/components/issue/IssuePriorityBadge';
import { IssueSeverityBadge } from '@/components/issue/IssueSeverityBadge';
import { IssueAttachments } from '@/components/issue/IssueAttachments';
import { IssueLinks } from '@/components/issue/IssueLinks';
import { IssueChecklist } from '@/components/issue/IssueChecklist';
import { IssueActivity } from '@/components/issue/IssueActivity';
import { TimeTracker } from '@/components/time-tracking/TimeTracker';
import { EditIssueDrawer } from '@/components/issue/EditIssueDrawer';
import { CreateIssueDrawer } from '@/components/issue/CreateIssueDrawer';
import toast from 'react-hot-toast';

export const IssueDetailPage: React.FC = () => {
  const { projectId, issueKey } = useParams<{ projectId: string; issueKey: string }>();
  const navigate = useNavigate();

  const [issue, setIssue] = useState<IssueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingStatus, setEditingStatus] = useState(false);
  const [editingPriority, setEditingPriority] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [assignee, setAssignee] = useState<UserWithRolesResponse | null>(null);
  const [reporter, setReporter] = useState<UserWithRolesResponse | null>(null);

  useEffect(() => {
    loadIssue();
    checkPinStatus();
  }, [issueKey, projectId]);

  useEffect(() => {
    if (issue) {
      loadUserDetails();
    }
  }, [issue]);

  const checkPinStatus = async () => {
    if (!projectId) return;
    try {
      const response = await projectsService.listPinnedProjects();
      const pinned = response.data.some(p => p.id === projectId);
      setIsPinned(pinned);
    } catch (error) {
      console.error('Failed to check pin status', error);
    }
  };

  const togglePin = async () => {
    if (!projectId) return;
    try {
      if (isPinned) {
        await projectsService.unpinProject(projectId);
        toast.success('Project unpinned');
      } else {
        await projectsService.pinProject(projectId);
        toast.success('Project pinned');
      }
      setIsPinned(!isPinned);
      // Trigger sidebar refresh
      window.dispatchEvent(new CustomEvent('refresh-pinned-projects'));
    } catch (error) {
      toast.error('Failed to update project pin');
    }
  };

  const loadUserDetails = async () => {
    if (!issue) return;

    try {
      // Load assignee if assigned
      if (issue.assignee_id) {
        const assigneeResponse = await usersService.getUser(issue.assignee_id);
        setAssignee(assigneeResponse.data);
      } else {
        setAssignee(null);
      }

      // Load reporter
      if (issue.reporter_id) {
        const reporterResponse = await usersService.getUser(issue.reporter_id);
        setReporter(reporterResponse.data);
      }
    } catch (error) {
      console.error('Failed to load user details:', error);
    }
  };

  const loadIssue = async () => {
    if (!issueKey) return;

    try {
      setLoading(true);
      const response = await issuesService.getIssueByKey(issueKey);
      setIssue(response.data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load task');
      navigate(`/projects/${projectId}/issues`);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (newStatus: IssueStatus) => {
    if (!issue) return;
    try {
      const response = await issuesService.updateIssue(issue.id, { status: newStatus });
      setIssue(response.data);
      setEditingStatus(false);
      toast.success('Status updated');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update status');
    }
  };

  const handleUpdatePriority = async (newPriority: Priority) => {
    if (!issue) return;
    try {
      const response = await issuesService.updateIssue(issue.id, { priority: newPriority });
      setIssue(response.data);
      setEditingPriority(false);
      toast.success('Priority updated');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update priority');
    }
  };

  const handleDeleteIssue = async () => {
    if (!issue) return;
    if (!confirm(`Are you sure you want to delete ${issue.issue_key}?`)) return;

    try {
      await issuesService.deleteIssue(issue.id);
      toast.success('Task deleted');
      navigate(`/projects/${projectId}/issues`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete task');
    }
  };

  const prepareCloneData = () => {
    if (!issue) return undefined;

    return {
      project_id: issue.project_id,
      issue_type: issue.issue_type,
      priority: issue.priority,
      title: issue.title,
      description: issue.description,
      label_ids: issue.labels?.map(l => l.id) || [],
      sprint_id: issue.sprint_id,
      assignee_id: issue.assignee_id,
      component_id: issue.component_id,
      feature_id: issue.feature_id,
      severity: issue.severity,
      affected_version: issue.affected_version,
      repro_steps: issue.repro_steps,
      story_points: issue.story_points,
      time_estimate_minutes: issue.time_estimate_minutes,
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!issue) return null;

  const isBug = issue.issue_type === 'bug';

  return (
    <div className="min-h-screen bg-white">
      {/* Header / Breadcrumbs */}
      <div className="border-b border-gray-200 px-8 py-4 bg-white sticky top-16 z-10 flex justify-between items-center">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span className="hover:text-blue-600 cursor-pointer" onClick={() => navigate(`/projects/${projectId}/issues`)}>
            Tasks
          </span>
          <span>/</span>
          <span className="font-medium text-gray-900">{issue.issue_key}</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowEditModal(true)}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            title="Edit Task"
          >
            <svg className="w-4 h-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit
          </button>
          <button
            onClick={() => setShowCloneModal(true)}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            title="Clone Task"
          >
            <svg className="w-4 h-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Clone
          </button>
          <button
            onClick={togglePin}
            className={`p-2 rounded-md transition-colors ${isPinned ? 'text-yellow-500 hover:bg-yellow-50' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'}`}
            title={isPinned ? "Unpin Project" : "Pin Project"}
          >
            <svg className="w-5 h-5" fill={isPinned ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.382-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>
          <button
            onClick={handleDeleteIssue}
            className="text-gray-400 hover:text-red-600 p-2 rounded-md hover:bg-red-50 transition-colors"
            title="Delete Task"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-8">
        {/* Title Area */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <IssueTypeIcon type={issue.issue_type} className="w-5 h-5" />
            <h1 className="text-2xl font-bold text-gray-900 leading-tight">{issue.title}</h1>
          </div>
          <div className="flex items-center gap-4">
            {editingStatus ? (
              <select
                value={issue.status}
                onChange={(e) => handleUpdateStatus(e.target.value as IssueStatus)}
                onBlur={() => setEditingStatus(false)}
                autoFocus
                className="px-2 py-1 text-sm border-gray-300 rounded"
              >
                <option value="new">New</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
              </select>
            ) : (
              <div onClick={() => setEditingStatus(true)} className="cursor-pointer hover:opacity-80">
                <IssueStatusBadge status={issue.status} />
              </div>
            )}

            {editingPriority ? (
              <select
                value={issue.priority}
                onChange={(e) => handleUpdatePriority(e.target.value as Priority)}
                onBlur={() => setEditingPriority(false)}
                autoFocus
                className="px-2 py-1 text-sm border-gray-300 rounded"
              >
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            ) : (
              <div onClick={() => setEditingPriority(true)} className="cursor-pointer hover:opacity-80">
                <IssuePriorityBadge priority={issue.priority} />
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-12 gap-12">
          {/* Left Column (Content) */}
          <div className="col-span-8 space-y-10">
            {/* Description */}
            <section>
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-3">Description</h3>
              <div className="prose prose-sm max-w-none text-gray-800 bg-gray-50 rounded-lg p-5 border border-transparent hover:border-gray-300 hover:bg-white transition-all cursor-pointer group">
                {issue.description ? (
                  <div dangerouslySetInnerHTML={{ __html: issue.description }} />
                ) : (
                  <span className="text-gray-400 italic">Add a description...</span>
                )}
                <div className="hidden group-hover:block absolute top-2 right-2 text-xs text-gray-400 bg-white px-2 py-1 rounded shadow-sm border">Click to edit</div>
              </div>
            </section>

            {/* Bug Specifics */}
            {isBug && issue.repro_steps && (
              <section>
                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-3">Reproduction Steps</h3>
                <div className="prose prose-sm max-w-none text-gray-700 bg-gray-50 rounded-lg p-5">
                  <div dangerouslySetInnerHTML={{ __html: issue.repro_steps }} />
                </div>
              </section>
            )}

            {/* Checklist */}
            <section className="pt-8 border-t border-gray-100">
              <IssueChecklist
                issueId={issue.id}
                projectId={issue.project_id}
                initialChecklists={issue.checklists || []}
              />
            </section>

            {/* Attachments */}
            <section>
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-3">Attachments</h3>
              <IssueAttachments issueId={issue.id} projectId={projectId!} />
            </section>

            {/* Time Tracking */}
            <section className="pt-8 border-t border-gray-100">
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">Time Tracking</h3>
              <TimeTracker issueId={issue.id} />
            </section>

            {/* Activity & Comments */}
            <section className="pt-8 border-t border-gray-100">
              <IssueActivity issueId={issue.id} />
            </section>
          </div>

          {/* Right Column (Sidebar) */}
          <div className="col-span-4 space-y-8">
            {/* Time Tracking Summary */}
            <div className="bg-blue-50 bg-opacity-50 rounded-lg border border-blue-100 p-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Estimated Time</h4>
                  <p className="text-lg font-bold text-gray-900">
                    {issue.time_estimate_minutes ? `${Math.floor(issue.time_estimate_minutes / 60)}h ${issue.time_estimate_minutes % 60}m` : 'Not set'}
                  </p>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Tracked Time</h4>
                  <p className="text-lg font-bold text-blue-600">
                    {issue.time_spent_minutes ? `${Math.floor(issue.time_spent_minutes / 60)}h ${issue.time_spent_minutes % 60}m` : '0h 0m'}
                  </p>
                </div>
              </div>
            </div>

            {/* Details Side Panel */}
            <div className="bg-gray-50 bg-opacity-50 rounded-lg border border-gray-100 p-5 space-y-5">
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-gray-500 uppercase">Assignee</h4>
                <div className="flex items-center gap-2 py-1 hover:bg-gray-100 rounded px-1 -ml-1 cursor-pointer transition-colors">
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-xs font-medium text-blue-700">
                    {assignee ? assignee.full_name[0].toUpperCase() : '?'}
                  </div>
                  <span className="text-sm text-gray-900">{assignee?.full_name || 'Unassigned'}</span>
                </div>
              </div>

              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-gray-500 uppercase">Reporter</h4>
                <div className="flex items-center gap-2 py-1 px-1 -ml-1">
                  <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-600">
                    {reporter ? reporter.full_name[0].toUpperCase() : '?'}
                  </div>
                  <span className="text-sm text-gray-900">{reporter?.full_name || 'Unknown'}</span>
                </div>
              </div>

              {isBug && (
                <div className="space-y-1">
                  <h4 className="text-xs font-semibold text-gray-500 uppercase">Severity</h4>
                  <div className="py-1">
                    <IssueSeverityBadge severity={issue.severity || 'major'} />
                  </div>
                </div>
              )}

              <div className="border-t border-gray-200 pt-4 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Created</span>
                  <span className="text-gray-900">{new Date(issue.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Updated</span>
                  <span className="text-gray-900">{new Date(issue.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {/* Links */}
            <IssueLinks issueId={issue.id} projectId={projectId!} links={[]} />
          </div>
        </div>
      </div>

      {/* Edit Issue Drawer */}
      {showEditModal && (
        <EditIssueDrawer
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          issue={issue}
          onSuccess={(updatedIssue) => {
            setIssue(updatedIssue);
            setShowEditModal(false);
          }}
        />
      )}

      {/* Clone Issue Drawer */}
      <CreateIssueDrawer
        isOpen={showCloneModal}
        onClose={() => setShowCloneModal(false)}
        projectId={projectId!}
        cloneData={prepareCloneData()}
        onSuccess={() => {
          setShowCloneModal(false);
          toast.success('Task cloned successfully');
          navigate(`/projects/${projectId}/issues`);
        }}
      />
    </div>
  );
};
