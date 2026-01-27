import { useState, FormEvent, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { issuesService } from '@/lib/services/issues.service';
import { usersService } from '@/lib/services/users.service';
import { sprintsService } from '@/lib/services/sprints.service';
import { toast } from 'react-hot-toast';
import {
  IssueResponse,
  IssueUpdate,
  IssueType,
  IssueStatus,
  Priority,
  Severity,
  UserWithRolesResponse,
  SprintResponse,
} from '@/types';

interface EditIssueModalProps {
  isOpen: boolean;
  onClose: () => void;
  issue: IssueResponse;
  onSuccess: (updated: IssueResponse) => void;
}

export const EditIssueModal: React.FC<EditIssueModalProps> = ({
  isOpen,
  onClose,
  issue,
  onSuccess,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [users, setUsers] = useState<UserWithRolesResponse[]>([]);
  const [sprints, setSprints] = useState<SprintResponse[]>([]);

  // Form fields
  const [title, setTitle] = useState(issue.title);
  const [description, setDescription] = useState(issue.description || '');
  const [issueType, setIssueType] = useState<IssueType>(issue.issue_type);
  const [status, setStatus] = useState<IssueStatus>(issue.status);
  const [priority, setPriority] = useState<Priority>(issue.priority);
  const [severity, setSeverity] = useState<Severity>(issue.severity || 'major');
  const [assigneeId, setAssigneeId] = useState(issue.assignee_id || '');
  const [sprintId, setSprintId] = useState(issue.sprint_id || '');
  const [reproSteps, setReproSteps] = useState(issue.repro_steps || '');
  const [environment, setEnvironment] = useState(issue.environment || '');

  useEffect(() => {
    if (isOpen) {
      loadUsers();
      loadSprints();
    }
  }, [isOpen]);

  const loadUsers = async () => {
    try {
      const response = await usersService.listUsers();
      setUsers(response.data || []);
    } catch (error) {
      toast.error('Failed to load users');
    }
  };

  const loadSprints = async () => {
    try {
      const response = await sprintsService.list(issue.project_id, false); // Don't include completed
      setSprints(response.data || []);
    } catch (error) {
      console.error('Failed to load sprints:', error);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('Title is required');
      return;
    }

    const updateData: IssueUpdate = {
      title: title.trim(),
      description: description.trim() || undefined,
      issue_type: issueType,
      status,
      priority,
      assignee_id: assigneeId || null,
      sprint_id: sprintId || null,
    };

    // Add bug-specific fields if it's a bug
    if (issueType === 'bug') {
      updateData.severity = severity;
      updateData.repro_steps = reproSteps.trim() || undefined;
      updateData.environment = environment.trim() || undefined;
    }

    try {
      setSubmitting(true);
      const response = await issuesService.updateIssue(issue.id, updateData);
      toast.success('Issue updated successfully');
      onSuccess(response.data);
      onClose();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update issue';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Edit ${issue.issue_key}`} size="xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Brief description of the task"
            required
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={4}
            placeholder="Detailed description..."
          />
        </div>

        {/* Row 1: Type, Status, Priority */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type <span className="text-red-500">*</span>
            </label>
            <select
              value={issueType}
              onChange={(e) => setIssueType(e.target.value as IssueType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="bug">Bug</option>
              <option value="task">Task</option>
              <option value="story">Story</option>
              <option value="improvement">Improvement</option>
              <option value="sub_task">Sub-task</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status <span className="text-red-500">*</span>
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as IssueStatus)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority <span className="text-red-500">*</span>
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>

        {/* Row 2: Assignee, Sprint, Severity (for bugs) */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assignee
            </label>
            <select
              value={assigneeId}
              onChange={(e) => setAssigneeId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Unassigned</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name} ({user.email})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sprint
            </label>
            <select
              value={sprintId}
              onChange={(e) => setSprintId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Backlog</option>
              {sprints.map((sprint) => (
                <option key={sprint.id} value={sprint.id}>
                  {sprint.name} ({sprint.status})
                </option>
              ))}
            </select>
          </div>

          {issueType === 'bug' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Severity
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value as Severity)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="blocker">Blocker</option>
                <option value="critical">Critical</option>
                <option value="major">Major</option>
                <option value="minor">Minor</option>
                <option value="trivial">Trivial</option>
              </select>
            </div>
          )}
        </div>

        {/* Bug-specific fields */}
        {issueType === 'bug' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reproduction Steps
              </label>
              <textarea
                value={reproSteps}
                onChange={(e) => setReproSteps(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Steps to reproduce the bug..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Environment
              </label>
              <input
                type="text"
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Chrome 120, macOS 14.2"
              />
            </div>
          </>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
            disabled={submitting}
          >
            {submitting ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
