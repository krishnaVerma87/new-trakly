import { useState, FormEvent, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { workflowsService } from '@/lib/services/workflows.service';
import { toast } from 'react-hot-toast';
import {
  WorkflowTemplateResponse,
  WorkflowColumnCreate,
  WorkflowMigrationPreview,
  ColumnMigrationAction,
} from '@/types';

interface EditWorkflowTemplateModalProps {
  isOpen: boolean;
  template: WorkflowTemplateResponse;
  onClose: () => void;
  onSuccess: () => void;
}

interface ColumnRow extends WorkflowColumnCreate {
  id: string;
  originalId?: string; // Track original ID for migration
}

export const EditWorkflowTemplateModal: React.FC<EditWorkflowTemplateModalProps> = ({
  isOpen,
  template,
  onClose,
  onSuccess,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [columns, setColumns] = useState<ColumnRow[]>([]);
  const [preview, setPreview] = useState<WorkflowMigrationPreview | null>(null);
  const [migrationActions, setMigrationActions] = useState<Record<string, string>>({});
  const [showingPreview, setShowingPreview] = useState(false);

  useEffect(() => {
    // Initialize columns from template
    const initialColumns: ColumnRow[] = template.columns.map((col) => ({
      id: col.id,
      originalId: col.id,
      name: col.name,
      position: col.position,
      wip_limit: col.wip_limit,
      color: col.color,
    }));
    setColumns(initialColumns);
  }, [template]);

  const addColumn = () => {
    if (columns.length >= 20) {
      toast.error('Maximum 20 columns allowed');
      return;
    }
    setColumns([
      ...columns,
      {
        id: crypto.randomUUID(),
        name: '',
        position: columns.length,
        wip_limit: undefined,
        color: '#6B7280',
      },
    ]);
  };

  const removeColumn = (id: string) => {
    if (columns.length === 1) {
      toast.error('At least one column is required');
      return;
    }
    const updatedColumns = columns.filter((c) => c.id !== id);
    updatedColumns.forEach((col, index) => {
      col.position = index;
    });
    setColumns(updatedColumns);
  };

  const updateColumn = (id: string, field: keyof WorkflowColumnCreate, value: any) => {
    setColumns(columns.map((c) => (c.id === id ? { ...c, [field]: value } : c)));
  };

  const moveColumn = (id: string, direction: 'up' | 'down') => {
    const index = columns.findIndex((c) => c.id === id);
    if ((direction === 'up' && index === 0) || (direction === 'down' && index === columns.length - 1)) {
      return;
    }

    const newColumns = [...columns];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newColumns[index], newColumns[targetIndex]] = [newColumns[targetIndex], newColumns[index]];

    newColumns.forEach((col, idx) => {
      col.position = idx;
    });

    setColumns(newColumns);
  };

  const handlePreview = async () => {
    // Validation
    const invalidColumns = columns.filter((c) => !c.name.trim());
    if (invalidColumns.length > 0) {
      toast.error('All columns must have a name');
      return;
    }

    const columnNames = columns.map((c) => c.name.trim().toLowerCase());
    const duplicates = columnNames.filter((name, index) => columnNames.indexOf(name) !== index);
    if (duplicates.length > 0) {
      toast.error(`Duplicate column name(s) found: ${duplicates.join(', ')}`);
      return;
    }

    try {
      setSubmitting(true);
      const response = await workflowsService.previewColumnChanges(template.id, {
        columns: columns.map(({ id, originalId, ...col }) => col),
      });

      setPreview(response.data);
      setShowingPreview(true);

      if (response.data.safe_to_apply) {
        toast.success('Changes can be applied safely');
      } else {
        toast(`${response.data.warnings.length} migration(s) required`, { icon: '⚠️' });
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to preview changes');
    } finally {
      setSubmitting(false);
    }
  };

  const handleApply = async () => {
    if (!preview) {
      return;
    }

    // If there are warnings, ensure all have migration targets
    if (preview.warnings.length > 0) {
      const missingActions = preview.warnings.filter((w) => !migrationActions[w.column_id]);
      if (missingActions.length > 0) {
        toast.error('Please select a target column for all warnings');
        return;
      }
    }

    try {
      setSubmitting(true);

      const actions: ColumnMigrationAction[] = preview.warnings.map((warning) => ({
        old_column_id: warning.column_id,
        new_column_id: migrationActions[warning.column_id],
      }));

      await workflowsService.updateColumns(template.id, {
        columns: columns.map(({ id, originalId, ...col }) => col),
        migration_actions: actions.length > 0 ? actions : undefined,
      });

      toast.success('Workflow columns updated successfully');
      onSuccess();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update columns');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!showingPreview) {
      await handlePreview();
    } else {
      await handleApply();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Edit Workflow: ${template.name}`} size="xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        {!showingPreview ? (
          <>
            {/* Column Editor */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Workflow Columns <span className="text-red-500">*</span>
                </label>
                <button
                  type="button"
                  onClick={addColumn}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  disabled={columns.length >= 20}
                >
                  + Add Column
                </button>
              </div>

              <div className="space-y-2">
                {columns.map((column, index) => (
                  <div
                    key={column.id}
                    className="flex items-center gap-2 p-3 bg-gray-50 rounded-md border border-gray-200"
                  >
                    {/* Move buttons */}
                    <div className="flex flex-col gap-0.5">
                      <button
                        type="button"
                        onClick={() => moveColumn(column.id, 'up')}
                        disabled={index === 0}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        ▲
                      </button>
                      <button
                        type="button"
                        onClick={() => moveColumn(column.id, 'down')}
                        disabled={index === columns.length - 1}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        ▼
                      </button>
                    </div>

                    {/* Column name */}
                    <input
                      type="text"
                      value={column.name}
                      onChange={(e) => updateColumn(column.id, 'name', e.target.value)}
                      className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      placeholder="Column name"
                      required
                    />

                    {/* WIP Limit */}
                    <input
                      type="number"
                      value={column.wip_limit || ''}
                      onChange={(e) =>
                        updateColumn(column.id, 'wip_limit', e.target.value ? parseInt(e.target.value) : undefined)
                      }
                      className="w-20 px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      placeholder="WIP"
                      min="1"
                    />

                    {/* Color picker */}
                    <input
                      type="color"
                      value={column.color || '#6B7280'}
                      onChange={(e) => updateColumn(column.id, 'color', e.target.value)}
                      className="w-12 h-9 border border-gray-300 rounded cursor-pointer"
                    />

                    {/* Remove button */}
                    <button
                      type="button"
                      onClick={() => removeColumn(column.id)}
                      className="p-2 text-red-600 hover:text-red-800 disabled:opacity-30"
                      disabled={columns.length === 1}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>

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
                {submitting ? 'Checking...' : 'Preview Changes'}
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Migration Preview */}
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Change Summary</h3>
                <div className="text-sm text-blue-700 space-y-1">
                  {preview?.changes.map((change, idx) => (
                    <div key={idx}>
                      {change.action === 'added' && `+ Adding column: ${change.new_name}`}
                      {change.action === 'removed' && `- Removing column: ${change.old_name}`}
                      {change.action === 'renamed' && `~ Renaming: ${change.old_name} → ${change.new_name}`}
                    </div>
                  ))}
                  {preview?.changes.length === 0 && <div>No structural changes detected</div>}
                </div>
              </div>

              {preview && preview.warnings.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-medium text-yellow-900 mb-3">Migration Required</h3>
                  <p className="text-sm text-yellow-700 mb-4">
                    The following columns are being removed but contain issues. Please select where to move the
                    issues:
                  </p>

                  <div className="space-y-4">
                    {preview.warnings.map((warning) => (
                      <div key={warning.column_id} className="bg-white p-3 rounded border border-yellow-200">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-medium text-gray-900">{warning.column_name}</h4>
                            <p className="text-sm text-gray-600">
                              {warning.issue_count} issue{warning.issue_count !== 1 ? 's' : ''} need to be moved
                            </p>
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Move issues to: <span className="text-red-500">*</span>
                          </label>
                          <select
                            value={migrationActions[warning.column_id] || ''}
                            onChange={(e) =>
                              setMigrationActions({
                                ...migrationActions,
                                [warning.column_id]: e.target.value,
                              })
                            }
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            required
                          >
                            <option value="">Select target column...</option>
                            {warning.suggested_target_columns.map((col) => (
                              <option key={col.id} value={col.id}>
                                {col.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {preview?.safe_to_apply && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-700">
                    ✓ Changes can be applied safely. No issues will be affected.
                  </p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-between pt-4 border-t">
              <button
                type="button"
                onClick={() => {
                  setShowingPreview(false);
                  setPreview(null);
                  setMigrationActions({});
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={submitting}
              >
                ← Back to Edit
              </button>
              <div className="flex gap-3">
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
                  {submitting ? 'Applying...' : 'Apply Changes'}
                </button>
              </div>
            </div>
          </>
        )}
      </form>
    </Modal>
  );
};
