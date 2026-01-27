import { useState, useEffect } from 'react';
import { savedSearchService, SavedSearchResponse } from '@/lib/services/saved-search.service';
import toast from 'react-hot-toast';

interface SavedSearchManagerProps {
  projectId: string;
  currentFilters: Record<string, any>;
  onApplySearch: (filters: Record<string, any>) => void;
}

export const SavedSearchManager: React.FC<SavedSearchManagerProps> = ({
  projectId,
  currentFilters,
  onApplySearch,
}) => {
  const [savedSearches, setSavedSearches] = useState<SavedSearchResponse[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showSearches, setShowSearches] = useState(false);
  const [saveName, setSaveName] = useState('');
  const [saveDescription, setSaveDescription] = useState('');
  const [saveAsShared, setSaveAsShared] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadSavedSearches();
    }
  }, [projectId]);

  const loadSavedSearches = async () => {
    try {
      const response = await savedSearchService.getProjectSearches(projectId);
      setSavedSearches(response.data);
    } catch (error: any) {
      console.error('Error loading saved searches:', error);
    }
  };

  const handleSaveSearch = async () => {
    if (!saveName.trim()) {
      toast.error('Please enter a name for this search');
      return;
    }

    try {
      setLoading(true);
      await savedSearchService.create({
        project_id: projectId,
        name: saveName,
        description: saveDescription || undefined,
        filter_config: currentFilters,
        is_shared: saveAsShared,
      });

      toast.success('Search saved successfully');
      setSaveName('');
      setSaveDescription('');
      setSaveAsShared(false);
      setShowSaveDialog(false);
      await loadSavedSearches();
    } catch (error: any) {
      toast.error(error.message || 'Failed to save search');
    } finally {
      setLoading(false);
    }
  };

  const handleApplySearch = (search: SavedSearchResponse) => {
    onApplySearch(search.filter_config);
    setShowSearches(false);
    toast.success(`Applied filter: ${search.name}`);
  };

  const handleDeleteSearch = async (searchId: string, searchName: string) => {
    if (!confirm(`Delete saved search "${searchName}"?`)) return;

    try {
      await savedSearchService.delete(searchId);
      toast.success('Search deleted');
      await loadSavedSearches();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete search');
    }
  };

  const hasActiveFilters = Object.keys(currentFilters).some(
    key => currentFilters[key] !== undefined && currentFilters[key] !== ''
  );

  return (
    <div className="relative">
      <div className="flex gap-2">
        {/* Save Current Filters Button */}
        <button
          onClick={() => setShowSaveDialog(true)}
          disabled={!hasActiveFilters}
          className="btn-secondary text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Save current filters"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          Save Filter
        </button>

        {/* Load Saved Searches Button */}
        <button
          onClick={() => setShowSearches(!showSearches)}
          className="btn-secondary text-sm flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Saved Filters
          {savedSearches.length > 0 && (
            <span className="bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full text-xs">
              {savedSearches.length}
            </span>
          )}
        </button>
      </div>

      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Save Current Filter</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter Name *
                </label>
                <input
                  type="text"
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  className="input w-full"
                  placeholder="e.g., High Priority Bugs"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={saveDescription}
                  onChange={(e) => setSaveDescription(e.target.value)}
                  className="input w-full"
                  rows={2}
                  placeholder="What does this filter show?"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="share-filter"
                  checked={saveAsShared}
                  onChange={(e) => setSaveAsShared(e.target.checked)}
                  className="h-4 w-4 text-blue-600 rounded border-gray-300"
                />
                <label htmlFor="share-filter" className="ml-2 text-sm text-gray-700">
                  Share with team
                </label>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSaveSearch}
                disabled={loading}
                className="btn-primary flex-1"
              >
                {loading ? 'Saving...' : 'Save Filter'}
              </button>
              <button
                onClick={() => {
                  setShowSaveDialog(false);
                  setSaveName('');
                  setSaveDescription('');
                  setSaveAsShared(false);
                }}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Saved Searches Dropdown */}
      {showSearches && (
        <div className="absolute top-full mt-2 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-10 w-80">
          <div className="p-3 border-b border-gray-200">
            <h4 className="font-semibold text-gray-900">Saved Filters</h4>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {savedSearches.length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                No saved filters yet
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {savedSearches.map((search) => (
                  <div
                    key={search.id}
                    className="p-3 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <button
                        onClick={() => handleApplySearch(search)}
                        className="flex-1 text-left"
                      >
                        <div className="font-medium text-gray-900 flex items-center gap-2">
                          {search.name}
                          {search.is_shared && (
                            <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">
                              Shared
                            </span>
                          )}
                        </div>
                        {search.description && (
                          <div className="text-sm text-gray-500 mt-1">
                            {search.description}
                          </div>
                        )}
                        <div className="text-xs text-gray-400 mt-1">
                          {new Date(search.created_at).toLocaleDateString()}
                        </div>
                      </button>

                      <button
                        onClick={() => handleDeleteSearch(search.id, search.name)}
                        className="text-red-600 hover:text-red-700 ml-2"
                        title="Delete"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
