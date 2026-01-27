import React, { useState } from 'react';

import { useNavigate, useParams } from 'react-router-dom';
import { issuesService } from '@/lib/services/issues.service';
import { IssueCreate, SimilarIssueResponse } from '@/types';
import { DuplicateWarning } from '@/components/issue/DuplicateWarning';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import { UserPicker } from '@/components/ui/UserPicker';
import { ComponentPicker } from '@/components/ui/ComponentPicker';
import { LabelPicker } from '@/components/ui/LabelPicker';
import { SprintPicker } from '@/components/ui/SprintPicker';
import { FeaturePicker } from '@/components/ui/FeaturePicker';
import { IssuePicker } from '@/components/ui/IssuePicker';
import { FileUpload } from '@/components/ui/FileUpload';
import toast from 'react-hot-toast';

export const CreateIssuePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [formData, setFormData] = useState<Partial<IssueCreate>>({
    project_id: projectId!,
    issue_type: 'task',
    priority: 'medium',
    title: '',
    description: '',
    label_ids: [],
  });

  const [_files, setFiles] = useState<File[]>([]); // TODO: Upload after issue creation
  const [similarIssues, setSimilarIssues] = useState<SimilarIssueResponse[]>([]);
  const [checkingDuplicates, setCheckingDuplicates] = useState(false);
  const [showDuplicateWarning, setShowDuplicateWarning] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Expandable sections state
  const [sectionsExpanded, setSectionsExpanded] = useState({
    planning: false,
    relationships: false,
    attachments: false,
  });

  // Duplicate check handler for onBlur
  const handleTitleBlur = () => {
    if (formData.title && formData.title.length > 3) {
      checkForDuplicates();
    }
  };

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

  const toggleSection = (section: keyof typeof sectionsExpanded) => {
    setSectionsExpanded((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title || !formData.description) {
      toast.error('Title and description are required');
      return;
    }

    // Validate sub-task parent
    if (formData.issue_type === 'sub_task' && !formData.parent_issue_id) {
      toast.error('Sub-tasks must have a parent issue');
      return;
    }

    try {
      setSubmitting(true);
      const response = await issuesService.createIssue(formData as IssueCreate);

      // TODO: Upload attachments after issue creation
      // if (files.length > 0) {
      //   await uploadAttachments(response.data.id, files);
      // }

      toast.success(`Task ${response.data.issue_key} created successfully`);
      navigate(`/projects/${projectId}/issues/${response.data.issue_key}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create task');
    } finally {
      setSubmitting(false);
    }
  };

  const isBug = formData.issue_type === 'bug';
  const isSubTask = formData.issue_type === 'sub_task';

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Create Task</h1>
        <p className="text-sm text-gray-600 mt-1">
          Fill in the details below to create a new task
        </p>
      </div>

      {/* Duplicate Warning */}
      {showDuplicateWarning && (
        <DuplicateWarning
          similarIssues={similarIssues}
          onDismiss={() => setShowDuplicateWarning(false)}
        />
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow">
        <div className="p-6 space-y-6">
          {/* Basic Information Section */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">
              Basic Information
            </h2>

            {/* Title */}
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
                  value={formData.title}
                  onChange={handleInputChange}
                  onBlur={handleTitleBlur}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief summary of the task"
                />
                {checkingDuplicates && (
                  <div className="absolute right-3 top-2.5">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  </div>
                )}
              </div>
            </div>

            {/* Description - Rich Text Editor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description <span className="text-red-500">*</span>
              </label>
              <RichTextEditor
                content={formData.description || ''}
                onChange={(content) => handleRichTextChange('description', content)}
                placeholder="Provide a detailed description of the task..."
                minHeight="200px"
              />
            </div>

            {/* Type, Priority, Severity Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Type */}
              <div>
                <label htmlFor="issue_type" className="block text-sm font-medium text-gray-700 mb-1">
                  Type <span className="text-red-500">*</span>
                </label>
                <select
                  id="issue_type"
                  name="issue_type"
                  required
                  value={formData.issue_type}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="task">Task</option>
                  <option value="bug">Bug</option>
                  <option value="story">Story</option>
                  <option value="improvement">Improvement</option>
                  <option value="sub_task">Sub-task</option>
                </select>
              </div>

              {/* Priority */}
              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                  Priority <span className="text-red-500">*</span>
                </label>
                <select
                  id="priority"
                  name="priority"
                  required
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

              {/* Severity - Only for bugs */}
              {isBug && (
                <div>
                  <label htmlFor="severity" className="block text-sm font-medium text-gray-700 mb-1">
                    Severity
                  </label>
                  <select
                    id="severity"
                    name="severity"
                    value={formData.severity || 'major'}
                    onChange={handleInputChange}
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
          </div>

          {/* Assignment Section */}
          <div className="space-y-4 border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">
              Assignment
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Assignee */}
              <UserPicker
                projectId={projectId!}
                value={formData.assignee_id}
                onChange={(userId) =>
                  setFormData((prev) => ({ ...prev, assignee_id: userId }))
                }
                label="Assignee"
                placeholder="Unassigned"
              />

              {/* Component */}
              <ComponentPicker
                projectId={projectId!}
                value={formData.component_id}
                onChange={(componentId) =>
                  setFormData((prev) => ({ ...prev, component_id: componentId }))
                }
                label="Component"
                placeholder="None"
              />
            </div>

            {/* Labels */}
            <LabelPicker
              projectId={projectId!}
              value={formData.label_ids || []}
              onChange={(labelIds) =>
                setFormData((prev) => ({ ...prev, label_ids: labelIds }))
              }
              label="Labels"
            />

            {/* Sprint */}
            <SprintPicker
              projectId={projectId!}
              value={formData.sprint_id}
              onChange={(sprintId) =>
                setFormData((prev) => ({ ...prev, sprint_id: sprintId }))
              }
              label="Sprint"
              placeholder="Backlog"
            />
          </div>

          {/* Bug-Specific Fields - Conditional */}
          {isBug && (
            <div className="space-y-4 border-t pt-6">
              <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">
                Bug Details
              </h2>

              {/* Reproduction Steps - Rich Text */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reproduction Steps
                </label>
                <RichTextEditor
                  content={formData.repro_steps || ''}
                  onChange={(content) => handleRichTextChange('repro_steps', content)}
                  placeholder="1. Step one&#10;2. Step two&#10;3. ..."
                  minHeight="150px"
                />
              </div>

              {/* Environment */}
              <div>
                <label htmlFor="environment" className="block text-sm font-medium text-gray-700 mb-1">
                  Environment
                </label>
                <input
                  type="text"
                  id="environment"
                  name="environment"
                  value={formData.environment || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Chrome 120, macOS 14.0"
                />
              </div>

              {/* Stack Trace */}
              <div>
                <label htmlFor="stack_trace" className="block text-sm font-medium text-gray-700 mb-1">
                  Stack Trace
                </label>
                <textarea
                  id="stack_trace"
                  name="stack_trace"
                  rows={6}
                  value={formData.stack_trace || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder="Paste error stack trace here..."
                />
              </div>

              {/* Affected Version & Is Regression */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="affected_version" className="block text-sm font-medium text-gray-700 mb-1">
                    Affected Version
                  </label>
                  <input
                    type="text"
                    id="affected_version"
                    name="affected_version"
                    value={formData.affected_version || ''}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., v2.1.0"
                  />
                </div>

                <div className="flex items-center pt-7">
                  <input
                    type="checkbox"
                    id="is_regression"
                    name="is_regression"
                    checked={formData.is_regression || false}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_regression" className="ml-2 block text-sm text-gray-700">
                    This is a regression (worked before)
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Parent Task - Only for sub-tasks */}
          {isSubTask && (
            <div className="border-t pt-6">
              <IssuePicker
                projectId={projectId!}
                value={formData.parent_issue_id}
                onChange={(issueId) =>
                  setFormData((prev) => ({ ...prev, parent_issue_id: issueId }))
                }
                label="Parent Task"
                required={true}
                placeholder="Select parent task..."
                filterType="parent"
              />
            </div>
          )}

          {/* Planning & Estimation - Expandable */}
          <div className="border-t pt-6">
            <button
              type="button"
              onClick={() => toggleSection('planning')}
              className="flex items-center justify-between w-full text-lg font-semibold text-gray-900 border-b pb-2 hover:text-blue-600"
            >
              <span>Planning & Estimation</span>
              <svg
                className={`h-5 w-5 transition-transform ${sectionsExpanded.planning ? 'rotate-180' : ''
                  }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {sectionsExpanded.planning && (
              <div className="mt-4 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Story Points */}
                  <div>
                    <label htmlFor="story_points" className="block text-sm font-medium text-gray-700 mb-1">
                      Story Points
                    </label>
                    <select
                      id="story_points"
                      name="story_points"
                      value={formData.story_points || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">None</option>
                      <option value="1">1</option>
                      <option value="2">2</option>
                      <option value="3">3</option>
                      <option value="5">5</option>
                      <option value="8">8</option>
                      <option value="13">13</option>
                      <option value="21">21</option>
                    </select>
                  </div>

                  {/* Time Estimate */}
                  <div>
                    <label htmlFor="time_estimate_minutes" className="block text-sm font-medium text-gray-700 mb-1">
                      Time Estimate (hours)
                    </label>
                    <input
                      type="number"
                      id="time_estimate_minutes"
                      name="time_estimate_minutes"
                      min="0"
                      step="0.5"
                      value={formData.time_estimate_minutes ? formData.time_estimate_minutes / 60 : ''}
                      onChange={(e) => {
                        const hours = parseFloat(e.target.value);
                        setFormData((prev) => ({
                          ...prev,
                          time_estimate_minutes: hours ? Math.round(hours * 60) : undefined,
                        }));
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., 2.5"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Relationships - Expandable */}
          <div className="border-t pt-6">
            <button
              type="button"
              onClick={() => toggleSection('relationships')}
              className="flex items-center justify-between w-full text-lg font-semibold text-gray-900 border-b pb-2 hover:text-blue-600"
            >
              <span>Relationships</span>
              <svg
                className={`h-5 w-5 transition-transform ${sectionsExpanded.relationships ? 'rotate-180' : ''
                  }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {sectionsExpanded.relationships && (
              <div className="mt-4 space-y-4">
                {/* Feature Link */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FeaturePicker
                    projectId={projectId!}
                    value={formData.feature_id}
                    onChange={(featureId) =>
                      setFormData((prev) => ({ ...prev, feature_id: featureId }))
                    }
                    label="Link to Feature"
                    placeholder="None"
                  />

                  {formData.feature_id && (
                    <div>
                      <label htmlFor="feature_link_type" className="block text-sm font-medium text-gray-700 mb-1">
                        Link Type
                      </label>
                      <select
                        id="feature_link_type"
                        name="feature_link_type"
                        value={formData.feature_link_type || 'implements'}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="implements">Implements</option>
                        <option value="blocks">Blocks</option>
                        <option value="relates_to">Relates To</option>
                        <option value="caused_by">Caused By</option>
                      </select>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Attachments - Expandable */}
          <div className="border-t pt-6">
            <button
              type="button"
              onClick={() => toggleSection('attachments')}
              className="flex items-center justify-between w-full text-lg font-semibold text-gray-900 border-b pb-2 hover:text-blue-600"
            >
              <span>Attachments</span>
              <svg
                className={`h-5 w-5 transition-transform ${sectionsExpanded.attachments ? 'rotate-180' : ''
                  }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {sectionsExpanded.attachments && (
              <div className="mt-4">
                <FileUpload
                  onFilesChange={setFiles}
                  label="Upload Files"
                  maxFiles={5}
                  maxFileSize={10}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Note: File attachments will be uploaded after task creation
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Form Actions */}
        <div className="bg-gray-50 px-6 py-4 border-t flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate(`/projects/${projectId}/issues`)}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting || checkingDuplicates}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Creating...' : 'Create Task'}
          </button>
        </div>
      </form>
    </div>
  );
};
