import { createClient } from '@/lib/supabase/server';
import { getCurrentUserProfile } from '@/lib/supabase/queries/profiles';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function ProfilePage({ params }: { params: { locale: string } }) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect(`/${params.locale}/login`);
  }

  const profile = await getCurrentUserProfile();

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="max-w-md w-full">
          <div className="rounded-md bg-yellow-50 p-4">
            <h3 className="text-sm font-medium text-yellow-800">
              Profile not found
            </h3>
            <p className="mt-2 text-sm text-yellow-700">
              Your profile hasn't been created yet. This might happen if you signed up before the profile system was added.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/${params.locale}`}
            className="text-sm text-primary-600 hover:text-primary-500 mb-4 inline-block"
          >
            ← Back to Home
          </Link>
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Your Profile</h1>
            <Link
              href={`/${params.locale}/profile/edit`}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Edit Profile
            </Link>
          </div>
        </div>

        {/* Profile Card */}
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          {/* Avatar Section */}
          <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-12">
            <div className="flex items-center space-x-6">
              <div className="flex-shrink-0">
                {profile.avatar_url ? (
                  <img
                    src={profile.avatar_url}
                    alt={profile.display_name || profile.full_name || 'Profile'}
                    className="h-24 w-24 rounded-full border-4 border-white object-cover"
                  />
                ) : (
                  <div className="h-24 w-24 rounded-full border-4 border-white bg-white flex items-center justify-center">
                    <span className="text-3xl font-bold text-primary-600">
                      {(profile.display_name || profile.full_name || profile.email || 'U')[0].toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-white">
                  {profile.display_name || profile.full_name || 'Anonymous User'}
                </h2>
                <p className="text-primary-100">{profile.email}</p>
              </div>
            </div>
          </div>

          {/* Profile Information */}
          <div className="px-6 py-6 space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {profile.full_name || 'Not set'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Display Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {profile.display_name || 'Not set'}
                  </dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Bio</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {profile.bio || 'No bio added yet'}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Preferences */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferences</h3>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Default Theme</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {profile.default_theme || 'Not set'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Default Audience</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {profile.default_audience || 'Not set'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Default Response Style</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {profile.default_response_style || 'Not set'}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Usage Statistics */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Statistics</h3>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Total Chats</dt>
                  <dd className="mt-1 text-2xl font-semibold text-gray-900">
                    {profile.total_chats}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Total Messages</dt>
                  <dd className="mt-1 text-2xl font-semibold text-gray-900">
                    {profile.total_messages}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Account Information */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Member Since</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(profile.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(profile.updated_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Session Management Link */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Security & Sessions</h3>
              <Link
                href={`/${params.locale}/profile/sessions`}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg className="h-5 w-5 mr-2 text-gray-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
                Manage Sessions
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
