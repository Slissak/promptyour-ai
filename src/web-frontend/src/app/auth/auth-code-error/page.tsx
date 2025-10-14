'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function AuthCodeErrorPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [errorDetails, setErrorDetails] = useState({
    error: '',
    errorCode: '',
    errorDescription: '',
  });

  useEffect(() => {
    setErrorDetails({
      error: searchParams.get('error') || '',
      errorCode: searchParams.get('error_code') || '',
      errorDescription: searchParams.get('error_description') || '',
    });
  }, [searchParams]);

  const getErrorMessage = () => {
    if (errorDetails.errorCode === 'otp_expired') {
      return {
        title: '⏰ Verification Link Expired',
        message: 'The email verification link has expired. Verification links are valid for 24 hours.',
        suggestion: 'Please request a new verification email by trying to log in again.',
      };
    }

    if (errorDetails.error === 'access_denied') {
      return {
        title: '🚫 Access Denied',
        message: 'The verification link is invalid or has already been used.',
        suggestion: 'If you haven\'t verified your email yet, try requesting a new verification email.',
      };
    }

    return {
      title: '❌ Verification Error',
      message: errorDetails.errorDescription || 'Something went wrong with email verification.',
      suggestion: 'Please try again or contact support if the problem persists.',
    };
  };

  const error = getErrorMessage();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="text-6xl mb-4">{error.title.split(' ')[0]}</div>
          <h2 className="text-3xl font-extrabold text-gray-900 mb-4">
            {error.title.substring(error.title.indexOf(' ') + 1)}
          </h2>
        </div>

        <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
          <div className="border-l-4 border-red-500 pl-4">
            <p className="text-sm text-gray-700 mb-2">
              <strong>What happened:</strong>
            </p>
            <p className="text-sm text-gray-600">{error.message}</p>
          </div>

          <div className="border-l-4 border-blue-500 pl-4">
            <p className="text-sm text-gray-700 mb-2">
              <strong>What to do:</strong>
            </p>
            <p className="text-sm text-gray-600">{error.suggestion}</p>
          </div>

          {errorDetails.errorCode === 'otp_expired' && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h3 className="text-sm font-medium text-blue-800 mb-2">
                📝 How to get a new verification email:
              </h3>
              <ol className="list-decimal list-inside text-sm text-blue-700 space-y-1">
                <li>Go to the login page</li>
                <li>Enter your email and password</li>
                <li>Click "Sign in"</li>
                <li>You'll see a "Resend verification email" button</li>
                <li>Check your inbox for the new email</li>
              </ol>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-3">
          <Link
            href="/login"
            className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            Go to Login Page
          </Link>
          <Link
            href="/"
            className="w-full flex justify-center py-3 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            Back to Home
          </Link>
        </div>

        {/* Technical Details (for debugging) */}
        {process.env.NODE_ENV === 'development' && (
          <details className="mt-8">
            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
              Technical Details (Development Only)
            </summary>
            <div className="mt-2 p-3 bg-gray-100 rounded text-xs font-mono">
              <p><strong>Error:</strong> {errorDetails.error}</p>
              <p><strong>Error Code:</strong> {errorDetails.errorCode}</p>
              <p><strong>Description:</strong> {errorDetails.errorDescription}</p>
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
