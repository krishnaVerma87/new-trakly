import { useState, useEffect } from 'react';
import { WorkflowTemplateResponse } from '@/types';
import { workflowsService } from '@/lib/services/workflows.service';
import { toast } from 'react-hot-toast';
import { CreateWorkflowTemplateModal } from './CreateWorkflowTemplateModal';
import { EditWorkflowTemplateModal } from './EditWorkflowTemplateModal';

export const WorkflowsTab = () => {
  const [templates, setTemplates] = useState<WorkflowTemplateResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<WorkflowTemplateResponse | null>(null);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await workflowsService.listTemplates(true);
      setTemplates(response.data || []);
    } catch (error) {
      console.error('Failed to load workflow templates:', error);
      toast.error('Failed to load workflow templates');
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleDelete = async (template: WorkflowTemplateResponse) => {
    if (template.is_system) {
      toast.error('Cannot delete system templates');
      return;
    }

    if (template.project_count && template.project_count > 0) {
      toast.error(
        `Cannot delete template: ${template.project_count} project(s) are using it`
      );
      return;
    }

    if (!confirm(`Are you sure you want to delete the template "${template.name}"?`)) {
      return;
    }

    try {
      await workflowsService.deleteTemplate(template.id);
      toast.success('Template deleted successfully');
      loadTemplates();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete template');
    }
  };

  const handleSetDefault = async (template: WorkflowTemplateResponse) => {
    if (template.is_default) {
      return;
    }

    try {
      await workflowsService.updateTemplate(template.id, { is_default: true });
      toast.success(`"${template.name}" set as default template`);
      loadTemplates();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to set default template');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Workflow Templates</h2>
          <p className="text-sm text-gray-600 mt-1">
            Manage Kanban board workflows for your organization
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Create Template
        </button>
      </div>

      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="divide-y divide-gray-200">
          {templates.map((template) => (
            <div key={template.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-medium text-gray-900">
                      {template.name}
                    </h3>
                    {template.is_default && (
                      <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        Default
                      </span>
                    )}
                    {template.is_system && (
                      <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                        System
                      </span>
                    )}
                  </div>
                  {template.description && (
                    <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                  )}

                  {/* Column chips */}
                  <div className="flex flex-wrap gap-2 mt-3">
                    {template.columns.map((column) => (
                      <div
                        key={column.id}
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-md border border-gray-200 bg-white text-xs"
                        style={
                          column.color && column.color.startsWith('#')
                            ? { borderLeftColor: column.color, borderLeftWidth: '4px' }
                            : undefined
                        }
                      >
                        <span className="font-medium">{column.name}</span>
                        {column.wip_limit && (
                          <span className="text-gray-500">
                            (WIP: {column.wip_limit})
                          </span>
                        )}
                        {column.issue_count !== undefined && column.issue_count > 0 && (
                          <span className="text-gray-500">
                            {column.issue_count} issue{column.issue_count !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                    <span>{template.columns.length} columns</span>
                    {template.project_count !== undefined && (
                      <span>
                        {template.project_count} project{template.project_count !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => setEditingTemplate(template)}
                    className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Edit Columns
                  </button>

                  {!template.is_default && (
                    <button
                      onClick={() => handleSetDefault(template)}
                      className="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100"
                    >
                      Set as Default
                    </button>
                  )}

                  {!template.is_system && (
                    <button
                      onClick={() => handleDelete(template)}
                      className="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100"
                      disabled={template.project_count !== undefined && template.project_count > 0}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
          {templates.length === 0 && (
            <div className="px-6 py-12 text-center text-gray-500">
              <p className="text-sm">No workflow templates found</p>
              <p className="text-xs mt-1">Create your first template to get started</p>
            </div>
          )}
        </div>
      </div>

      {showCreateModal && (
        <CreateWorkflowTemplateModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            loadTemplates();
          }}
        />
      )}

      {editingTemplate && (
        <EditWorkflowTemplateModal
          isOpen={true}
          template={editingTemplate}
          onClose={() => setEditingTemplate(null)}
          onSuccess={() => {
            setEditingTemplate(null);
            loadTemplates();
          }}
        />
      )}
    </div>
  );
};
