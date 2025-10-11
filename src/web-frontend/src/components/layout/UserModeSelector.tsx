'use client';

import { useUserMode } from '@/hooks/useUserMode';

export function UserModeSelector() {
  const { userMode, setUserMode, isLoaded } = useUserMode();

  if (!isLoaded) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">Mode:</span>
      <div className="inline-flex rounded-lg border border-gray-300 bg-white p-1">
        <button
          onClick={() => setUserMode('regular')}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
            userMode === 'regular'
              ? 'bg-primary-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          👤 Regular
        </button>
        <button
          onClick={() => setUserMode('advanced')}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
            userMode === 'advanced'
              ? 'bg-primary-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          🔬 Advanced
        </button>
      </div>
    </div>
  );
}
