'use client';

import { useState, useEffect } from 'react';

export type UserMode = 'regular' | 'advanced';

const USER_MODE_KEY = 'promptyourai_user_mode';

export function useUserMode() {
  const [userMode, setUserModeState] = useState<UserMode>('regular');
  const [isLoaded, setIsLoaded] = useState(false);

  // Load user mode from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(USER_MODE_KEY);
    if (stored === 'regular' || stored === 'advanced') {
      setUserModeState(stored);
    }
    setIsLoaded(true);
  }, []);

  // Save to localStorage whenever mode changes
  const setUserMode = (mode: UserMode) => {
    setUserModeState(mode);
    localStorage.setItem(USER_MODE_KEY, mode);
  };

  return {
    userMode,
    setUserMode,
    isLoaded,
    isRegularMode: userMode === 'regular',
    isAdvancedMode: userMode === 'advanced'
  };
}
