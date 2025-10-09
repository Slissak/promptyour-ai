/**
 * Storage Service
 * Handles local persistence using AsyncStorage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
  USER_ID: '@promptyourai:user_id',
  CONVERSATION_HISTORY: '@promptyourai:conversation_history',
  USER_PREFERENCES: '@promptyourai:user_preferences',
  API_BASE_URL: '@promptyourai:api_base_url',
  LAST_THEME: '@promptyourai:last_theme',
  LAST_AUDIENCE: '@promptyourai:last_audience',
  LAST_RESPONSE_STYLE: '@promptyourai:last_response_style',
  CHAT_MODE: '@promptyourai:chat_mode',
};

class StorageService {
  /**
   * Save a value to storage
   */
  async set(key: string, value: any): Promise<void> {
    try {
      const jsonValue = JSON.stringify(value);
      await AsyncStorage.setItem(key, jsonValue);
    } catch (error) {
      console.error(`[Storage] Error saving ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get a value from storage
   */
  async get<T>(key: string): Promise<T | null> {
    try {
      const jsonValue = await AsyncStorage.getItem(key);
      return jsonValue != null ? JSON.parse(jsonValue) : null;
    } catch (error) {
      console.error(`[Storage] Error reading ${key}:`, error);
      return null;
    }
  }

  /**
   * Remove a value from storage
   */
  async remove(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error(`[Storage] Error removing ${key}:`, error);
      throw error;
    }
  }

  /**
   * Clear all storage
   */
  async clear(): Promise<void> {
    try {
      await AsyncStorage.clear();
    } catch (error) {
      console.error('[Storage] Error clearing storage:', error);
      throw error;
    }
  }

  /**
   * User ID management
   */
  async getUserId(): Promise<string | null> {
    return this.get<string>(STORAGE_KEYS.USER_ID);
  }

  async setUserId(userId: string): Promise<void> {
    return this.set(STORAGE_KEYS.USER_ID, userId);
  }

  /**
   * User preferences management
   */
  async getUserPreferences(): Promise<any> {
    return this.get(STORAGE_KEYS.USER_PREFERENCES);
  }

  async setUserPreferences(preferences: any): Promise<void> {
    return this.set(STORAGE_KEYS.USER_PREFERENCES, preferences);
  }

  /**
   * Last used theme
   */
  async getLastTheme(): Promise<string | null> {
    return this.get<string>(STORAGE_KEYS.LAST_THEME);
  }

  async setLastTheme(theme: string): Promise<void> {
    return this.set(STORAGE_KEYS.LAST_THEME, theme);
  }

  /**
   * Last used audience
   */
  async getLastAudience(): Promise<string | null> {
    return this.get<string>(STORAGE_KEYS.LAST_AUDIENCE);
  }

  async setLastAudience(audience: string): Promise<void> {
    return this.set(STORAGE_KEYS.LAST_AUDIENCE, audience);
  }

  /**
   * Last used response style
   */
  async getLastResponseStyle(): Promise<string | null> {
    return this.get<string>(STORAGE_KEYS.LAST_RESPONSE_STYLE);
  }

  async setLastResponseStyle(style: string): Promise<void> {
    return this.set(STORAGE_KEYS.LAST_RESPONSE_STYLE, style);
  }

  /**
   * Chat mode
   */
  async getChatMode(): Promise<string | null> {
    return this.get<string>(STORAGE_KEYS.CHAT_MODE);
  }

  async setChatMode(mode: string): Promise<void> {
    return this.set(STORAGE_KEYS.CHAT_MODE, mode);
  }

  /**
   * API Base URL
   */
  async getApiBaseUrl(): Promise<string | null> {
    return this.get<string>(STORAGE_KEYS.API_BASE_URL);
  }

  async setApiBaseUrl(url: string): Promise<void> {
    return this.set(STORAGE_KEYS.API_BASE_URL, url);
  }

  /**
   * Conversation history
   */
  async getConversationHistory(): Promise<any[]> {
    const history = await this.get<any[]>(STORAGE_KEYS.CONVERSATION_HISTORY);
    return history || [];
  }

  async setConversationHistory(history: any[]): Promise<void> {
    return this.set(STORAGE_KEYS.CONVERSATION_HISTORY, history);
  }

  async addConversation(conversation: any): Promise<void> {
    const history = await this.getConversationHistory();
    history.unshift(conversation); // Add to beginning
    // Keep only last 50 conversations
    const trimmedHistory = history.slice(0, 50);
    return this.setConversationHistory(trimmedHistory);
  }

  async deleteConversation(conversationId: string): Promise<void> {
    const history = await this.getConversationHistory();
    const filtered = history.filter((c) => c.id !== conversationId);
    return this.setConversationHistory(filtered);
  }
}

// Export singleton instance
export const storageService = new StorageService();
export default storageService;
