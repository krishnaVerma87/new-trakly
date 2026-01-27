import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsService } from '@/lib/services/projects.service';
import { ProjectResponse, ProjectUpdate } from '@/types'; // You might need to add ProjectUpdate type if missing
import toast from 'react-hot-toast';
import { ProjectReminders } from '@/components/project/ProjectReminders';
import { ComponentsManager } from '@/components/project/ComponentsManager';
import { ProjectMembersManager } from '@/components/project/ProjectMembersManager';


const ProjectSettingsPage = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const navigate = useNavigate();
    const [project, setProject] = useState<ProjectResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'details' | 'components' | 'members' | 'reminders'>('details');


    // Form state for details
    const [formData, setFormData] = useState<ProjectUpdate>({});

    useEffect(() => {
        loadProject();
    }, [projectId]);

    const loadProject = async () => {
        if (!projectId) return;
        try {
            const response = await projectsService.getProject(projectId);
            setProject(response.data);
            setFormData({
                name: response.data.name,
                description: response.data.description,
                is_active: response.data.is_active,
            });
        } catch (error) {
            toast.error('Failed to load project details');
            navigate('/projects');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateProject = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!project || !projectId) return;

        try {
            await projectsService.updateProject(projectId, formData);
            toast.success('Project updated successfully');
            loadProject(); // Reload to get fresh data
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to update project');
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!project) return <div>Project not found</div>;

    return (
        <div className="space-y-6">
            <div className="border-b border-gray-200 pb-5">
                <h1 className="text-3xl font-bold text-gray-900">Project Settings</h1>
                <p className="mt-2 text-sm text-gray-500">
                    Manage settings for {project.name} ({project.key})
                </p>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    {['details', 'components', 'members', 'reminders'].map((tab) => (

                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab as any)}
                            className={`
                whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Content */}
            <div className="mt-6">
                {activeTab === 'details' && (
                    <div className="bg-white shadow rounded-lg p-6 max-w-2xl">
                        <form onSubmit={handleUpdateProject} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Project Name</label>
                                <input
                                    type="text"
                                    value={formData.name || ''}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Description</label>
                                <textarea
                                    rows={3}
                                    value={formData.description || ''}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                />
                            </div>

                            <div className="flex items-center">
                                <input
                                    id="is_active"
                                    type="checkbox"
                                    checked={formData.is_active ?? true}
                                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                                    Active Project
                                </label>
                            </div>

                            <div className="flex justify-end">
                                <button
                                    type="submit"
                                    className="bg-blue-600 border border-transparent rounded-md shadow-sm py-2 px-4 inline-flex justify-center text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                >
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {activeTab === 'components' && (
                    <div className="bg-white shadow rounded-lg p-6">
                        <ComponentsManager projectId={projectId!} />
                    </div>
                )}

                {activeTab === 'members' && (
                    <div className="bg-white shadow rounded-lg p-6">
                        <ProjectMembersManager projectId={projectId!} />
                    </div>
                )}

                {activeTab === 'reminders' && (
                    <div className="bg-white shadow rounded-lg">
                        <ProjectReminders projectId={projectId!} />
                    </div>
                )}

            </div>
        </div>
    );
};

export default ProjectSettingsPage;
