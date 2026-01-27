import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { featuresService } from '@/lib/services/features.service';
import { CreateFeatureModal } from '@/components/feature/CreateFeatureModal';
import { FeatureResponse } from '@/types';

const FeaturesPage = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const navigate = useNavigate();
    const [features, setFeatures] = useState<FeatureResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    const fetchFeatures = async () => {
        if (!projectId) return;
        try {
            const response = await featuresService.listFeatures({ project_id: projectId });
            setFeatures(response.data);
        } catch (error) {
            console.error('Error fetching features:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFeatures();
    }, [projectId]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-900">Features</h1>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="btn-primary"
                >
                    Create Feature
                </button>
            </div>

            {features.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                    <p className="text-gray-500">No features found. Create your first feature to get started!</p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {features.map((feature) => (
                        <div
                            key={feature.id}
                            onClick={() => navigate(`/projects/${projectId}/features/${feature.id}`)}
                            className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
                        >
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900">{feature.title}</h3>
                                    <p className="text-sm text-gray-500 mt-1">{feature.feature_key}</p>
                                </div>
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800`}>
                                    {feature.status.replace('_', ' ')}
                                </span>
                            </div>
                            <div className="mt-4">
                                <div className="flex justify-between text-sm text-gray-600 mb-1">
                                    <span>Progress</span>
                                    <span>{feature.progress_percentage}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${feature.progress_percentage}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <CreateFeatureModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                projectId={projectId!}
                onSuccess={fetchFeatures}
            />
        </div>
    );
};

export default FeaturesPage;
