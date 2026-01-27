import { useState, FormEvent } from 'react';
import { Modal } from '@/components/ui/Modal';
import { workflowsService } from '@/lib/services/workflows.service';
import { toast } from 'react-hot-toast';
import { WorkflowColumnCreate } from '@/types';

interface CreateWorkflowTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface ColumnRow extends WorkflowColumnCreate {
  id: string;
}

export const CreateWorkflowTemplateModal: React.FC<CreateWorkflowTemplateModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isDefault, setIsDefault] = useState(false);
  const [columns, setColumns] = useState<ColumnRow[]>([
    { id: crypto.randomUUID(), name: 'To Do', position: 0, wip_limit: undefined, color: '#3B82F6' },
    { id: crypto.randomUUID(), name: 'In Progress', position: 1, wip_limit: 5, color: '#F59E0B' },
    { id: crypto.randomUUID(), name: 'Done', position: 2, wip_limit: undefined, color: '#10B981' },
  ]);

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
    // Reposition remaining columns
    updatedColumns.forEach((col, index) => {
      col.position = index;
    });
    setColumns(updatedColumns);
  };

  const updateColumn = (id: string, field: keyof WorkflowColumnCreate, value: any) => {
    setColumns(
      columns.map((c) =>
        c.id === id ? { ...c, [field]: value } : c
      )
    );
  };

  const moveColumn = (id: string, direction: 'up' | 'down') => {
    const index = columns.findIndex((c) => c.id === id);
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === columns.length - 1)
    ) {
      return;
    }

    const newColumns = [...columns];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newColumns[index], newColumns[targetIndex]] = [newColumns[targetIndex], newColumns[index]];

    // Update positions
    newColumns.forEach((col, idx) => {
      col.position = idx;
    });

    setColumns(newColumns);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validation
    if (!name.trim()) {
      toast.error('Template name is required');
      return;
    }

    const invalidColumns = columns.filter((c) => !c.name.trim());
    if (invalidColumns.length > 0) {
      toast.error('All columns must have a name');
      return;
    }

    // Check for duplicate column names
    const columnNames = columns.map((c) => c.name.trim().toLowerCase());
    const duplicates = columnNames.filter((name, index) => columnNames.indexOf(name) !== index);
    if (duplicates.length > 0) {
      toast.error(`Duplicate column name(s) found: ${duplicates.join(', ')}`);
      return;
    }

    try {
      setSubmitting(true);
      await workflowsService.createTemplate({
        name: name.trim(),
        description: description.trim() || undefined,
        is_default: isDefault,
        columns: columns.map(({ id, ...col }) => ({
          ...col,
          wip_limit: col.wip_limit || undefined,
        })),
      });

      toast.success('Workflow template created successfully');
      onSuccess();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create template');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setIsDefault(false);
    setColumns([
      { id: crypto.randomUUID(), name: 'To Do', position: 0, wip_limit: undefined, color: '#3B82F6' },
      { id: crypto.randomUUID(), name: 'In Progress', position: 1, wip_limit: 5, color: '#F59E0B' },
      { id: crypto.randomUUID(), name: 'Done', position: 2, wip_limit: undefined, color: '#10B981' },
    ]);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Create Workflow Template" size="xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Template Info */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Software Development"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
              placeholder="Optional description of this workflow"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is-default"
              checked={isDefault}
              onChange={(e) => setIsDefault(e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is-default" className="ml-2 text-sm text-gray-700">
              Set as default template for new projects
            </label>
          </div>
        </div>

        {/* Columns */}
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
              <div key={column.id} className="flex items-center gap-2 p-3 bg-gray-50 rounded-md border border-gray-200">
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
          <p className="text-xs text-gray-500 mt-2">
            Drag columns to reorder. WIP (Work In Progress) limits are optional.
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={handleClose}
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
            {submitting ? 'Creating...' : 'Create Template'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
