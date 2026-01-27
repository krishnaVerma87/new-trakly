import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '@/lib/services/auth.service';
import toast from 'react-hot-toast';

interface SignupFormData {
  organizationName: string;
  organizationSlug: string;
  organizationDescription: string;
  userEmail: string;
  userPassword: string;
  userConfirmPassword: string;
  userFullName: string;
  userTimezone: string;
}

export const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<SignupFormData>({
    organizationName: '',
    organizationSlug: '',
    organizationDescription: '',
    userEmail: '',
    userPassword: '',
    userConfirmPassword: '',
    userFullName: '',
    userTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Auto-generate slug from organization name
    if (name === 'organizationName') {
      const slug = value
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-');
      setFormData((prev) => ({ ...prev, organizationSlug: slug }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (formData.userPassword !== formData.userConfirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (formData.userPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    if (!formData.organizationSlug.match(/^[a-z0-9-]+$/)) {
      toast.error('Organization slug can only contain lowercase letters, numbers, and hyphens');
      return;
    }

    try {
      setLoading(true);
      await authService.signup({
        organization_name: formData.organizationName,
        organization_slug: formData.organizationSlug,
        organization_description: formData.organizationDescription || undefined,
        user_email: formData.userEmail,
        user_password: formData.userPassword,
        user_full_name: formData.userFullName,
        user_timezone: formData.userTimezone,
      });

      toast.success('Welcome to Trakly! Your organization has been created.');
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Signup failed:', error);
      toast.error(error.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Your Organization</h1>
          <p className="text-gray-600 mt-2">Start tracking bugs and features with Trakly</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Organization Section */}
          <div className="border-b pb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Organization Details</h2>

            <div className="space-y-4">
              <div>
                <label htmlFor="organizationName" className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="organizationName"
                  name="organizationName"
                  required
                  value={formData.organizationName}
                  onChange={handleInputChange}
                  placeholder="e.g., Acme Corporation"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label htmlFor="organizationSlug" className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Slug <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="organizationSlug"
                  name="organizationSlug"
                  required
                  value={formData.organizationSlug}
                  onChange={handleInputChange}
                  pattern="^[a-z0-9-]+$"
                  placeholder="e.g., acme-corporation"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Lowercase letters, numbers, and hyphens only. This will be your unique URL identifier.
                </p>
              </div>

              <div>
                <label htmlFor="organizationDescription" className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  id="organizationDescription"
                  name="organizationDescription"
                  rows={2}
                  value={formData.organizationDescription}
                  onChange={handleInputChange}
                  placeholder="Tell us about your organization..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Admin User Section */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Admin Account</h2>

            <div className="space-y-4">
              <div>
                <label htmlFor="userFullName" className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="userFullName"
                  name="userFullName"
                  required
                  value={formData.userFullName}
                  onChange={handleInputChange}
                  placeholder="e.g., John Doe"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label htmlFor="userEmail" className="block text-sm font-medium text-gray-700 mb-1">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  id="userEmail"
                  name="userEmail"
                  required
                  value={formData.userEmail}
                  onChange={handleInputChange}
                  placeholder="admin@example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="userPassword" className="block text-sm font-medium text-gray-700 mb-1">
                    Password <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    id="userPassword"
                    name="userPassword"
                    required
                    minLength={8}
                    value={formData.userPassword}
                    onChange={handleInputChange}
                    placeholder="Min. 8 characters"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="userConfirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm Password <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    id="userConfirmPassword"
                    name="userConfirmPassword"
                    required
                    minLength={8}
                    value={formData.userConfirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm password"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Creating organization...
                </span>
              ) : (
                'Create Organization'
              )}
            </button>
          </div>

          {/* Login Link */}
          <div className="text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:text-blue-800 font-medium">
              Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};
