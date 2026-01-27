import React from 'react';
import { FileUpload } from '@/components/ui/FileUpload';
import toast from 'react-hot-toast';

interface IssueAttachmentsProps {
    issueId: string;
    projectId: string;
}

export const IssueAttachments: React.FC<IssueAttachmentsProps> = ({ issueId, projectId }) => {
    // Placeholder implementation until API is ready
    const handleFilesChange = async (files: File[]) => {
        toast.success(`${files.length} files prepared for upload (implementation pending)`);
        console.log('Files to upload:', files, issueId, projectId);
    };

    return (
        <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Attachments</h3>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                <p className="text-gray-500 mb-4">No attachments yet.</p>
                <FileUpload onFilesChange={handleFilesChange} />
            </div>
        </div>
    );
};
