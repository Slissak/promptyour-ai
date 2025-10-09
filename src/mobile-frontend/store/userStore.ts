/**
 * User Store
 * Manages user state and preferences
 */

import { create } from 'zustand';
import { storageService } from '../services/storage';

interface UserState {
  userId: string | null;
  isInitialized: boolean;

  // Actions
  setUserId: (userId: string) => void;
  initializeUser: () => Promise<void>;
  clearUser: () => void;
}

// Generate a unique user ID
const generateUserId = (): string => {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const useUserStore = create<UserState>((set, get) => ({
  // Initial state
  userId: null,
  isInitialized: false,

  // Actions
  setUserId: (userId) => {
    set({ userId });
    storageService.setUserId(userId);
  },

  initializeUser: async () => {
    try {
      // Try to load existing user ID
      let userId = await storageService.getUserId();

      // If no user ID exists, create a new one
      if (!userId) {
        userId = generateUserId();
        await storageService.setUserId(userId);
      }

      set({ userId, isInitialized: true });
    } catch (error) {
      console.error('[UserStore] Error initializing user:', error);
      // Fallback to generating a new user ID
      const userId = generateUserId();
      set({ userId, isInitialized: true });
    }
  },

  clearUser: async () => {
    await storageService.remove('@promptyourai:user_id');
    set({ userId: null, isInitialized: false });
  },
}));
