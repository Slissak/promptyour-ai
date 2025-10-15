'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { getProfile, updateProfile } from '@/lib/profile/actions';
import Link from 'next/link';
import type { UserProfile, UserProfileUpdate } from '@/types/profile';

export default function EditProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [formData, setFormData] = useState<UserProfileUpdate>({
    full_name: '',
    display_name: '',
    bio: '',
    avatar_url: '',
    default_theme: '',
    default_audience: '',
    default_response_style: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;

  // Load profile data
  useEffect(() => {
    async function loadProfile() {
      const result = await getProfile();
      if (result.error || !result.profile) {
        setError(result.error || 'Failed to load profile');
        setIsLoading(false);
        return;
      }

      setProfile(result.profile);
      setFormData({
        full_name: result.profile.full_name || '',
        display_name: result.profile.display_name || '',
        bio: result.profile.bio || '',
        avatar_url: result.profile.avatar_url || '',
        default_theme: result.profile.default_theme || '',
        default_audience: result.profile.default_audience || '',
        default_response_style: result.profile.default_response_style || '',
      });
      setIsLoading(false);
    }

    loadProfile();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value || null
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setIsSaving(true);

    try {
      const result = await updateProfile(formData);

      if (result.error) {
        setError(result.error);
        setIsSaving(false);
        return;
      }

      setSuccess(true);
      setIsSaving(false);

      // Redirect to profile page after success
      setTimeout(() => {
        router.push(`/${locale}/profile`);
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Loading profile...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="max-w-md w-full">
          <div className="rounded-md bg-red-50 p-4">
            <h3 className="text-sm font-medium text-red-800">
              {error || 'Profile not found'}
            </h3>
          </div>
          <div className="mt-4">
            <Link
              href={`/${locale}/profile`}
              className="text-primary-600 hover:text-primary-500"
            >
              ← Back to Profile
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/${locale}/profile`}
            className="text-sm text-primary-600 hover:text-primary-500 mb-4 inline-block"
          >
            ← Back to Profile
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Edit Profile</h1>
          <p className="mt-2 text-sm text-gray-600">
            Update your profile information and preferences
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{error}</h3>
                </div>
              </div>
            </div>
          )}

          {success && (
            <div className="rounded-md bg-green-50 p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    ✅ Profile updated successfully! Redirecting...
                  </h3>
                </div>
              </div>
            </div>
          )}

          {/* Personal Information */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <input
                  type="text"
                  name="full_name"
                  id="full_name"
                  value={formData.full_name || ''}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  disabled={isSaving}
                />
              </div>

              <div>
                <label htmlFor="display_name" className="block text-sm font-medium text-gray-700">
                  Display Name
                </label>
                <input
                  type="text"
                  name="display_name"
                  id="display_name"
                  value={formData.display_name || ''}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  disabled={isSaving}
                />
                <p className="mt-1 text-xs text-gray-500">
                  This is how your name will appear to others
                </p>
              </div>

              <div>
                <label htmlFor="bio" className="block text-sm font-medium text-gray-700">
                  Bio
                </label>
                <textarea
                  name="bio"
                  id="bio"
                  rows={3}
                  value={formData.bio || ''}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  disabled={isSaving}
                  placeholder="Tell us about yourself..."
                />
              </div>

              <div>
                <label htmlFor="avatar_url" className="block text-sm font-medium text-gray-700">
                  Avatar URL
                </label>
                <input
                  type="url"
                  name="avatar_url"
                  id="avatar_url"
                  value={formData.avatar_url || ''}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  disabled={isSaving}
                  placeholder="https://example.com/avatar.jpg"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Enter the URL of your profile picture
                </p>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Default Preferences</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="default_theme" className="block text-sm font-medium text-gray-700">
                  Default Theme
                </label>
                <input
                  type="text"
                  name="default_theme"
                  id="default_theme"
                  value={formData.default_theme || ''}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  disabled={isSaving}
                  placeholder="e.g., Dark, Light"
                />
              </div>

              <div>
                <label htmlFor="default_audience" className="block text-sm font-medium text-gray-700">
                  Default Audience
                </label>
                <input
                  type="text"
                  name="default_audience"
                  id="default_audience"
                  value={formData.default_audience || ''}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  disabled={isSaving}
                  placeholder="e.g., General, Technical"
                />
              </div>

              <div>
                <label htmlFor="default_response_style" className="block text-sm font-medium text-gray-700">
                  Default Response Style
                </label>
                <input
                  type="text"
                  name="default_response_style"
                  id="default_response_style"
                  value={formData.default_response_style || ''}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  disabled={isSaving}
                  placeholder="e.g., Quick, Detailed"
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <Link
              href={`/${locale}/profile`}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={isSaving || success}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isSaving ? 'Saving...' : success ? 'Saved!' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
