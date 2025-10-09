/**
 * Configuration Store
 * Manages user configuration and preferences
 */

import { create } from 'zustand';
import {
  ThemeType,
  AudienceType,
  ResponseStyle,
  ThemeConfig,
  AudienceConfig,
  ResponseStyleConfig,
} from '../types/api';
import { storageService } from '../services/storage';

interface ConfigState {
  // Current selections
  theme: ThemeType;
  audience: AudienceType;
  responseStyle: ResponseStyle;
  context: string;

  // Available options
  themes: ThemeConfig[];
  audiences: AudienceConfig[];
  responseStyles: ResponseStyleConfig[];

  // Loading state
  isLoading: boolean;

  // Actions
  setTheme: (theme: ThemeType) => void;
  setAudience: (audience: AudienceType) => void;
  setResponseStyle: (style: ResponseStyle) => void;
  setContext: (context: string) => void;
  setThemes: (themes: ThemeConfig[]) => void;
  setAudiences: (audiences: AudienceConfig[]) => void;
  setResponseStyles: (styles: ResponseStyleConfig[]) => void;
  loadFromStorage: () => Promise<void>;
  saveToStorage: () => Promise<void>;
  reset: () => void;
}

const DEFAULT_THEME = ThemeType.GENERAL_QUESTIONS;
const DEFAULT_AUDIENCE = AudienceType.ADULTS;
const DEFAULT_RESPONSE_STYLE = ResponseStyle.STRUCTURED_DETAILED;

export const useConfigStore = create<ConfigState>((set, get) => ({
  // Initial state
  theme: DEFAULT_THEME,
  audience: DEFAULT_AUDIENCE,
  responseStyle: DEFAULT_RESPONSE_STYLE,
  context: '',
  themes: [],
  audiences: [],
  responseStyles: [],
  isLoading: false,

  // Actions
  setTheme: (theme) => {
    set({ theme });
    storageService.setLastTheme(theme);
  },

  setAudience: (audience) => {
    set({ audience });
    storageService.setLastAudience(audience);
  },

  setResponseStyle: (responseStyle) => {
    set({ responseStyle });
    storageService.setLastResponseStyle(responseStyle);
  },

  setContext: (context) => set({ context }),

  setThemes: (themes) => set({ themes }),

  setAudiences: (audiences) => set({ audiences }),

  setResponseStyles: (responseStyles) => set({ responseStyles }),

  loadFromStorage: async () => {
    try {
      set({ isLoading: true });

      const [savedTheme, savedAudience, savedResponseStyle] =
        await Promise.all([
          storageService.getLastTheme(),
          storageService.getLastAudience(),
          storageService.getLastResponseStyle(),
        ]);

      set({
        theme: (savedTheme as ThemeType) || DEFAULT_THEME,
        audience: (savedAudience as AudienceType) || DEFAULT_AUDIENCE,
        responseStyle:
          (savedResponseStyle as ResponseStyle) || DEFAULT_RESPONSE_STYLE,
        isLoading: false,
      });
    } catch (error) {
      console.error('[ConfigStore] Error loading from storage:', error);
      set({ isLoading: false });
    }
  },

  saveToStorage: async () => {
    try {
      const { theme, audience, responseStyle } = get();
      await Promise.all([
        storageService.setLastTheme(theme),
        storageService.setLastAudience(audience),
        storageService.setLastResponseStyle(responseStyle),
      ]);
    } catch (error) {
      console.error('[ConfigStore] Error saving to storage:', error);
    }
  },

  reset: () =>
    set({
      theme: DEFAULT_THEME,
      audience: DEFAULT_AUDIENCE,
      responseStyle: DEFAULT_RESPONSE_STYLE,
      context: '',
    }),
}));
