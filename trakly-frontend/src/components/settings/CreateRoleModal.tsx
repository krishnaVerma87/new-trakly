import { useState, FormEvent } from 'react';
import { Modal } from '@/components/ui/Modal';
import { rolesService } from '@/lib/services/roles.service';
import { toast } from 'react-hot-toast';

interface CreateRoleModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export const CreateRoleModal: React.FC<CreateRoleModalProps> = ({
    isOpen,
    onClose,
    onSuccess,
}) => {
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
    });

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!formData.name.trim()) {
            toast.error('Role name is required');
            return;
        }

        try {
            setSubmitting(true);
            await rolesService.createRole(formData);
            toast.success('Role created successfully');
            onSuccess();
            onClose();
            setFormData({ name: '', description: '' });
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create role');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Create Role">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Role Name <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g. Manager, Developer"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                    </label>
                    <input
                        type="text"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Optional description"
                    />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
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
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                        disabled={submitting}
                    >
                        {submitting ? 'Creating...' : 'Create Role'}
                    </button>
                </div>
            </form>
        </Modal>
    );
};
