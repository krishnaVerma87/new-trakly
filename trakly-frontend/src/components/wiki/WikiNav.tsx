import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { wikiService } from '@/lib/services/wiki.service';
import type { WikiPageTreeNode } from '@/types';
import toast from 'react-hot-toast';

interface WikiNavProps {
  projectId: string;
  currentSlug?: string;
}

export const WikiNav: React.FC<WikiNavProps> = ({ projectId, currentSlug }) => {
  const [tree, setTree] = useState<WikiPageTreeNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadTree();
  }, [projectId]);

  const loadTree = async () => {
    try {
      setLoading(true);
      const res = await wikiService.getWikiTree(projectId);
      setTree(res.data);
    } catch (error) {
      toast.error('Failed to load wiki navigation');
    } finally {
      setLoading(false);
    }
  };

  const toggleNode = (nodeId: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };

  const renderNode = (node: WikiPageTreeNode, level: number = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const isCurrent = node.slug === currentSlug;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.id} className="select-none">
        <div
          className={`group flex items-center gap-1.5 py-1.5 px-3 mx-2 rounded-lg text-sm transition-all cursor-pointer ${
            isCurrent
              ? 'bg-blue-500 text-white font-medium shadow-sm'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
          style={{ paddingLeft: `${level * 20 + 12}px` }}
        >
          {hasChildren ? (
            <button
              onClick={() => toggleNode(node.id)}
              className={`flex-shrink-0 w-4 h-4 flex items-center justify-center rounded transition-all ${
                isCurrent ? 'hover:bg-blue-600' : 'hover:bg-gray-200'
              }`}
            >
              <svg
                className={`w-3 h-3 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          ) : (
            <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isCurrent ? 'bg-white' : 'bg-gray-300'}`} />
          )}
          <Link
            to={`/projects/${projectId}/wiki/${node.slug}`}
            className="flex-1 truncate"
          >
            {node.title}
          </Link>
        </div>
        {hasChildren && isExpanded && (
          <div className="mt-0.5">
            {node.children.map((child) => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
        <p className="text-sm text-gray-500 mt-3">Loading pages...</p>
      </div>
    );
  }

  if (tree.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-sm text-gray-500 mb-3">No pages yet</p>
        <Link
          to={`/projects/${projectId}/wiki/new`}
          className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create first page
        </Link>
      </div>
    );
  }

  return (
    <div className="py-4 px-2">
      <div className="space-y-1">
        {tree.map((node) => renderNode(node))}
      </div>
    </div>
  );
};
