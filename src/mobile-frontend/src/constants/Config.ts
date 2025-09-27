/**
 * Mobile App Configuration
 * Environment-specific settings and API endpoints
 */

import { Platform } from 'react-native';
import Constants from 'expo-constants';
import * as Device from 'expo-device';

const isDevelopment = __DEV__;

export const API_CONFIG = {
  // Use localhost for iOS simulator, 10.0.2.2 for Android emulator
  baseURL: Platform.select({
    ios: 'http://localhost:8001',
    android: Device.isDevice ? 'http://10.0.2.2:8001' : 'http://localhost:8001',
    default: 'http://localhost:8001',
  }),
  timeout: 60000,
  retryAttempts: 3,
  retryDelay: 1000,
};

export const APP_CONFIG = {
  appName: 'PromptYour.AI',
  version: Constants.expoConfig?.version || '1.0.0',
  isDevelopment,
};

export const THEME_CONFIG = {
  colors: {
    primary: '#3B82F6',
    primaryDark: '#2563EB',
    secondary: '#10B981',
    background: '#FFFFFF',
    surface: '#F9FAFB',
    text: '#1F2937',
    textSecondary: '#6B7280',
    border: '#E5E7EB',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    quick: '#FEF3C7',
    quickBorder: '#FCD34D',
    enhanced: '#DBEAFE',
    enhancedBorder: '#60A5FA',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    full: 9999,
  },
  typography: {
    sizes: {
      xs: 12,
      sm: 14,
      md: 16,
      lg: 18,
      xl: 24,
      xxl: 32,
    },
    weights: {
      regular: '400' as const,
      medium: '500' as const,
      semibold: '600' as const,
      bold: '700' as const,
    },
  },
};

export const CHAT_CONFIG = {
  maxMessageLength: 2000,
  typingIndicatorDelay: 1500,
  messageAnimationDuration: 300,
  quickResponseTimeout: 30000,
  enhancedResponseTimeout: 120000,
};