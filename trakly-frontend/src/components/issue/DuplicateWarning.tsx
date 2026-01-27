import React from 'react';
import { SimilarIssueResponse } from '@/types';
import { IssueTypeIcon } from './IssueTypeIcon';
import { IssueStatusBadge } from './IssueStatusBadge';

interface DuplicateWarningProps {
  similarIssues: SimilarIssueResponse[];
  onDismiss: () => void;
}

export const DuplicateWarning: React.FC<DuplicateWarningProps> = ({ similarIssues, onDismiss }) => {
  if (similarIssues.length === 0) return null;

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-yellow-800">
            Possible Duplicate Issues Found
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            <p className="mb-3">
              We found {similarIssues.length} similar issue{similarIssues.length > 1 ? 's' : ''}.
              Please review before creating a new one:
            </p>
            <div className="space-y-2">
              {similarIssues.map((issue) => (
                <div
                  key={issue.id}
                  className="bg-white border border-yellow-200 rounded p-3 hover:bg-yellow-50 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <IssueTypeIcon type={issue.issue_type} className="w-5 h-5 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <a
                          href={`/projects/${issue.project_id}/issues/${issue.issue_key}`}
                          className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {issue.issue_key}
                        </a>
                        <IssueStatusBadge status={issue.status} />
                        <span className="text-xs text-gray-500">
                          {(issue.similarity_score * 100).toFixed(0)}% match
                        </span>
                      </div>
                      <p className="text-sm text-gray-900">{issue.title}</p>
                      {issue.description && (
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {issue.description}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="ml-auto pl-3">
          <button
            type="button"
            onClick={onDismiss}
            className="inline-flex rounded-md bg-yellow-50 p-1.5 text-yellow-500 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 focus:ring-offset-yellow-50"
          >
            <span className="sr-only">Dismiss</span>
            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};
