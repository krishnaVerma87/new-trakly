import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { featuresService } from '@/lib/services/features.service';
import { FeatureResponse } from '@/types';

const FeatureRoadmap = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const [features, setFeatures] = useState<FeatureResponse[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
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

        fetchFeatures();
    }, [projectId]);

    if (loading) return <div>Loading roadmap...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900">Feature Roadmap</h1>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <p className="text-gray-500 mb-4">Timeline view coming soon.</p>
                <div className="grid gap-4 max-w-lg mx-auto text-left">
                    {features.map(f => (
                        <div key={f.id} className="border p-4 rounded-lg">
                            <div className="font-semibold">{f.title}</div>
                            <div className="text-sm text-gray-500">Target: {f.target_date || 'Not set'}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default FeatureRoadmap;
