import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { WikiNav } from '@/components/wiki/WikiNav';
import { WikiPageViewer } from '@/components/wiki/WikiPageViewer';
import { WikiPageEditor } from '@/components/wiki/WikiPageEditor';

export const WikiPage: React.FC = () => {
  const { projectId, slug, action } = useParams<{ projectId: string; slug?: string; action?: string }>();
  const [navOpen, setNavOpen] = useState(true);

  if (!projectId) {
    return <div className="p-8 text-center text-red-600">Project ID is required</div>;
  }

  const isEditing = action === 'edit';
  const isCreating = slug === 'new' || action === 'new';

  return (
    <div className="flex gap-6 h-full">
      {/* Collapsible Wiki Navigation */}
      {navOpen && (
        <div className="w-72 flex-shrink-0 bg-white border border-gray-200 rounded-lg shadow-sm flex flex-col overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Pages
              </h2>
              <div className="flex items-center gap-1">
                <Link
                  to={`/projects/${projectId}/wiki/new`}
                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  title="New page"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </Link>
                <button
                  onClick={() => setNavOpen(false)}
                  className="p-1.5 text-gray-400 hover:bg-gray-100 rounded transition-colors"
                  title="Close navigation"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Navigation Tree */}
          <div className="flex-1 overflow-y-auto">
            <WikiNav projectId={projectId} currentSlug={slug} />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 min-w-0">
        {/* Toggle button when nav is closed */}
        {!navOpen && (
          <button
            onClick={() => setNavOpen(true)}
            className="mb-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            Show Pages
          </button>
        )}

        {/* Page Content */}
        {isCreating ? (
          <WikiPageEditor projectId={projectId} />
        ) : isEditing && slug ? (
          <WikiPageEditor projectId={projectId} slug={slug} />
        ) : slug ? (
          <WikiPageViewer projectId={projectId} slug={slug} />
        ) : (
          <div className="flex items-center justify-center h-96">
            <div className="text-center max-w-md">
              <div className="w-20 h-20 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <svg
                  className="w-10 h-10 text-blue-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Wiki</h3>
              <p className="text-gray-500 mb-6">
                Create and organize your project documentation
              </p>
              <Link
                to={`/projects/${projectId}/wiki/new`}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create First Page
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
