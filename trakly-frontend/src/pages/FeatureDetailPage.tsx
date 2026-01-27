import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { featuresService } from '@/lib/services/features.service'; // Assuming this service exists or will update
import { FeatureWithIssuesResponse } from '@/types';
import toast from 'react-hot-toast';

const FeatureDetailPage = () => {
    const { featureId } = useParams<{ projectId: string; featureId: string }>();
    const [feature, setFeature] = useState<FeatureWithIssuesResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFeature = async () => {
            if (!featureId) return;
            try {
                const response = await featuresService.getFeature(featureId);
                setFeature(response.data);
            } catch (error) {
                toast.error('Failed to load feature');
            } finally {
                setLoading(false);
            }
        };
        fetchFeature();
    }, [featureId]);

    if (loading) return <div>Loading...</div>;
    if (!feature) return <div>Feature not found</div>;

    return (
        <div className="space-y-6">
            <div className="border-b border-gray-200 pb-5">
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{feature.title}</h1>
                        <p className="mt-1 text-sm text-gray-500">{feature.feature_key}</p>
                    </div>
                    <div className="flex gap-2">
                        <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 capitalize">
                            {feature.status.replace('_', ' ')}
                        </span>
                    </div>
                </div>
            </div>

            <div className="bg-white px-6 py-5 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{feature.description || 'No description provided.'}</p>
            </div>

            <div className="bg-white px-6 py-5 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Progress</h3>
                <div className="flex items-center gap-4">
                    <div className="flex-1 bg-gray-200 rounded-full h-4">
                        <div
                            className="bg-green-600 h-4 rounded-full transition-all duration-300"
                            style={{ width: `${feature.progress_percentage}%` }}
                        ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-700">{feature.progress_percentage}%</span>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm text-gray-500">
                    <div>
                        <span className="block font-medium text-gray-900">{feature.bug_count}</span>
                        Total Bugs
                    </div>
                    <div>
                        <span className="block font-medium text-red-600">{feature.open_bug_count}</span>
                        Open Bugs
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900">Linked Issues</h3>
                </div>
                <ul className="divide-y divide-gray-200">
                    {feature.linked_issues.map((issue) => (
                        <li key={issue.id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50">
                            <div className="flex items-center gap-4">
                                <span className="px-2 py-1 text-xs bg-gray-100 rounded text-gray-600">{issue.link_type}</span>
                                <div>
                                    <p className="text-sm font-medium text-gray-900">{issue.issue_key}: {issue.title}</p>
                                    <p className="text-xs text-gray-500 capitalize">{issue.issue_type} • {issue.status}</p>
                                </div>
                            </div>
                        </li>
                    ))}
                    {feature.linked_issues.length === 0 && (
                        <li className="px-6 py-8 text-center text-gray-500">No linked issues</li>
                    )}
                </ul>
            </div>
        </div>
    );
};

export default FeatureDetailPage;
