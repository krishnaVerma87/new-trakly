import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { isAdmin } from '@/lib/utils/roles';

import { GlobalSearch } from '@/components/layout/GlobalSearch';
import { NotificationDropdown } from '@/components/notifications/NotificationDropdown';

const TopBar = () => {
  const { user, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showDropdown]);

  const adminUser = isAdmin(user);

  return (
    <div className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 h-16 z-40">
      <div className="flex items-center justify-between h-full px-6">
        <div className="flex items-center gap-12 flex-1">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-primary-600">Trakly</h1>
          </div>
          <GlobalSearch />
        </div>

        <div className="flex items-center space-x-4">
          <NotificationDropdown />
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors"
            >
              <div className="text-sm text-right">
                <div className="font-medium text-gray-900">{user?.full_name}</div>
                <div className="text-gray-500">{user?.email}</div>
              </div>
              <svg
                className={`w-4 h-4 text-gray-500 transition-transform ${showDropdown ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showDropdown && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
                <Link
                  to="/settings?tab=profile"
                  onClick={() => setShowDropdown(false)}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  👤 Profile
                </Link>
                {adminUser && (
                  <Link
                    to="/settings"
                    onClick={() => setShowDropdown(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    ⚙️ Settings
                  </Link>
                )}
                <div className="border-t border-gray-200 my-1"></div>
                <button
                  onClick={() => {
                    setShowDropdown(false);
                    logout();
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                >
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
