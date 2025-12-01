'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type UserMode = 'regular' | 'advanced';

interface UserModeContextType {
  userMode: UserMode;
  setUserMode: (mode: UserMode) => void;
  isLoaded: boolean;
}

const UserModeContext = createContext<UserModeContextType | undefined>(undefined);

const USER_MODE_KEY = 'promptyourai_user_mode';

export function UserModeProvider({ children }: { children: ReactNode }) {
  const [userMode, setUserModeState] = useState<UserMode>('regular');
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(USER_MODE_KEY);
    if (stored === 'regular' || stored === 'advanced') {
      setUserModeState(stored);
    }
    setIsLoaded(true);
  }, []);

  const setUserMode = (mode: UserMode) => {
    setUserModeState(mode);
    localStorage.setItem(USER_MODE_KEY, mode);
  };

  return (
    <UserModeContext.Provider value={{ userMode, setUserMode, isLoaded }}>
      {children}
    </UserModeContext.Provider>
  );
}

export function useUserModeContext() {
  const context = useContext(UserModeContext);
  if (context === undefined) {
    throw new Error('useUserModeContext must be used within a UserModeProvider');
  }
  return context;
}
