import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { wikiService } from '@/lib/services/wiki.service';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import type { WikiPageResponse, WikiPageCreate, WikiPageUpdate } from '@/types';
import toast from 'react-hot-toast';

interface WikiPageEditorProps {
  projectId: string;
  slug?: string; // If provided, edit existing page. Otherwise, create new.
  parentId?: string; // For creating child pages
}

export const WikiPageEditor: React.FC<WikiPageEditorProps> = ({ projectId, slug, parentId }) => {
  const [page, setPage] = useState<WikiPageResponse | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [customSlug, setCustomSlug] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  const isEditMode = !!slug;

  useEffect(() => {
    if (isEditMode && slug) {
      loadPage();
    }
  }, [projectId, slug]);

  const loadPage = async () => {
    if (!slug) return;

    try {
      setLoading(true);
      const res = await wikiService.getPageBySlug(projectId, slug);
      const pageData = res.data;
      setPage(pageData);
      setTitle(pageData.title);
      setContent(pageData.content);
      setCustomSlug(pageData.slug);
    } catch (error) {
      toast.error('Failed to load wiki page');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!title.trim()) {
      toast.error('Title is required');
      return;
    }

    try {
      setSaving(true);

      if (isEditMode && page) {
        // Update existing page
        const updateData: WikiPageUpdate = {
          title: title.trim(),
          content,
        };

        if (customSlug && customSlug !== page.slug) {
          updateData.slug = customSlug;
        }

        const res = await wikiService.updatePage(projectId, page.id, updateData);
        toast.success('Page updated');
        navigate(`/projects/${projectId}/wiki/${res.data.slug}`);
      } else {
        // Create new page
        const createData: WikiPageCreate = {
          title: title.trim(),
          content,
          parent_id: parentId,
        };

        if (customSlug) {
          createData.slug = customSlug;
        }

        const res = await wikiService.createPage(projectId, createData);
        toast.success('Page created');
        navigate(`/projects/${projectId}/wiki/${res.data.slug}`);
      }
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Failed to save page';
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (isEditMode && page) {
      navigate(`/projects/${projectId}/wiki/${page.slug}`);
    } else {
      navigate(`/projects/${projectId}/wiki`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-3 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
          <p className="text-sm text-gray-500 mt-3">Loading editor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Top Bar with Actions */}
      <div className="px-8 py-4 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {isEditMode ? 'Edit Page' : 'Create New Page'}
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {isEditMode ? 'Update your documentation' : 'Add new content to your wiki'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCancel}
              disabled={saving}
              className="px-5 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={saving || !title.trim()}
              className="inline-flex items-center gap-2 px-5 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving && (
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {saving ? 'Saving...' : (isEditMode ? 'Save Changes' : 'Publish Page')}
            </button>
          </div>
        </div>
      </div>

      {/* Editor Content */}
      <div className="px-8 py-8">
        <div className="space-y-8">
          {/* Title Input */}
          <div>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Page title"
              autoFocus
              className="w-full text-4xl font-bold text-gray-900 border-none px-0 py-2 focus:outline-none focus:ring-0 placeholder-gray-300"
            />
          </div>

          {/* Custom Slug (collapsible advanced option) */}
          <details className="group">
            <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 flex items-center gap-2">
              <svg className="w-4 h-4 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              Advanced: Custom URL slug
            </summary>
            <div className="mt-3 pl-6">
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg">
                <span className="text-sm text-gray-400">/wiki/</span>
                <input
                  type="text"
                  value={customSlug}
                  onChange={(e) => setCustomSlug(e.target.value)}
                  placeholder="auto-generated-from-title"
                  className="flex-1 text-sm bg-transparent border-none px-0 py-0 focus:outline-none focus:ring-0 placeholder-gray-400"
                />
              </div>
              <p className="text-xs text-gray-400 mt-2 pl-1">
                Leave blank to auto-generate from title
              </p>
            </div>
          </details>

          {/* Content Editor */}
          <div className="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
            <RichTextEditor
              content={content}
              onChange={setContent}
              placeholder="Start writing your page content..."
              minHeight="600px"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
