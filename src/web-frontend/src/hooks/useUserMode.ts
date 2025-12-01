'use client';

import { useUserModeContext } from '@/context/UserModeContext';

export type UserMode = 'regular' | 'advanced';

export function useUserMode() {
  const { userMode, setUserMode, isLoaded } = useUserModeContext();

  return {
    userMode,
    setUserMode,
    isLoaded,
    isRegularMode: userMode === 'regular',
    isAdvancedMode: userMode === 'advanced'
  };
}
