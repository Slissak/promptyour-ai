'use client';

import { useState } from 'react';
import { signOut } from '@/lib/auth/actions';
import { useRouter, useParams } from 'next/navigation';

interface UserMenuProps {
  userEmail: string;
}

export function UserMenu({ userEmail }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const params = useParams();
  const locale = (params.locale as string) || 'en';

  const handleSignOut = async () => {
    setIsLoading(true);
    try {
      await signOut(locale);
    } catch (error) {
      console.error('Error signing out:', error);
      // Redirect to login anyway with locale
      router.push(`/${locale}/login`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
      >
        <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white font-medium">
          {userEmail.charAt(0).toUpperCase()}
        </div>
        <span className="text-sm text-gray-700 hidden sm:inline">{userEmail}</span>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop to close menu when clicking outside */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown menu */}
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
            <div className="px-4 py-2 border-b border-gray-200">
              <p className="text-sm text-gray-500">Signed in as</p>
              <p className="text-sm font-medium text-gray-900 truncate">{userEmail}</p>
            </div>
            <button
              onClick={handleSignOut}
              disabled={isLoading}
              className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing out...' : 'Sign out'}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
