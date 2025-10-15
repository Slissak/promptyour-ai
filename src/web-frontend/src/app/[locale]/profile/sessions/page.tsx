'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { getUserSessions, signOutAllDevices, getSessionInfo } from '@/lib/sessions/actions';
import Link from 'next/link';

export default function SessionsPage() {
  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;

  useEffect(() => {
    async function loadSessions() {
      const result = await getSessionInfo();
      if (result.error) {
        setError(result.error);
      } else if (result.session) {
        setSessionInfo(result.session);
      }
      setIsLoading(false);
    }

    loadSessions();
  }, []);

  const handleSignOutAll = async () => {
    if (!confirm('Are you sure you want to sign out from all devices? You will be logged out immediately.')) {
      return;
    }

    setIsSigningOut(true);
    setError(null);

    const result = await signOutAllDevices(locale);

    if (result.error) {
      setError(result.error);
      setIsSigningOut(false);
    } else {
      setSuccess('Signed out from all devices successfully');
      setTimeout(() => {
        router.push(result.redirectTo || `/${locale}/login`);
      }, 1500);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Loading sessions...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/${locale}/profile`}
            className="text-sm text-primary-600 hover:text-primary-500 mb-4 inline-block"
          >
            ← Back to Profile
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Active Sessions</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage where you're signed in
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
              </div>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 rounded-md bg-green-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">{success}</h3>
              </div>
            </div>
          </div>
        )}

        {/* Current Session Info */}
        <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">Current Session</h2>
          </div>

          <div className="px-6 py-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                      <svg className="h-6 w-6 text-green-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-900">This Device</h3>
                    <p className="text-sm text-gray-500">Current session - Active now</p>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {sessionInfo?.last_sign_in && (
                    <div>
                      <dt className="text-xs font-medium text-gray-500">Last Sign In</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(sessionInfo.last_sign_in).toLocaleString()}
                      </dd>
                    </div>
                  )}

                  {sessionInfo?.created_at && (
                    <div>
                      <dt className="text-xs font-medium text-gray-500">Account Created</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(sessionInfo.created_at).toLocaleDateString()}
                      </dd>
                    </div>
                  )}

                  {sessionInfo?.expires_at && (
                    <div>
                      <dt className="text-xs font-medium text-gray-500">Session Expires</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(sessionInfo.expires_at * 1000).toLocaleString()}
                      </dd>
                    </div>
                  )}
                </div>
              </div>

              <div className="ml-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Session Management Actions */}
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">Session Security</h2>
          </div>

          <div className="px-6 py-6 space-y-4">
            <div className="flex items-start">
              <div className="flex-1">
                <h3 className="text-sm font-medium text-gray-900">Sign Out All Devices</h3>
                <p className="mt-1 text-sm text-gray-500">
                  This will sign you out from all devices and browsers where you're currently logged in,
                  including this one. You'll need to sign in again.
                </p>
              </div>
              <button
                onClick={handleSignOutAll}
                disabled={isSigningOut}
                className="ml-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isSigningOut ? 'Signing Out...' : 'Sign Out All'}
              </button>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      Enhanced Session Management (Coming Soon)
                    </h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <p>
                        Future updates will include:
                      </p>
                      <ul className="list-disc list-inside mt-2 space-y-1">
                        <li>View all active sessions across devices</li>
                        <li>See device information (browser, OS, location)</li>
                        <li>Revoke individual sessions</li>
                        <li>Email notifications for new sign-ins</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Security Tips */}
        <div className="mt-6 bg-white shadow-md rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">Security Tips</h2>
          </div>

          <div className="px-6 py-6">
            <ul className="space-y-3 text-sm text-gray-600">
              <li className="flex items-start">
                <svg className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Always sign out when using shared or public computers</span>
              </li>
              <li className="flex items-start">
                <svg className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Use a strong, unique password for your account</span>
              </li>
              <li className="flex items-start">
                <svg className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>If you notice any suspicious activity, sign out all devices immediately</span>
              </li>
              <li className="flex items-start">
                <svg className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Consider using password reset if you suspect your account may be compromised</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
