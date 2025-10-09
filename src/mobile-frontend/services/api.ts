/**
 * API Service Layer
 * Handles all HTTP requests to the backend
 */

import {
  UserInput,
  QuickInput,
  RawInput,
  ChatResponse,
  QuickResponse,
  RawResponse,
  UserRating,
  ThemeConfig,
  AudienceConfig,
  ResponseStyleConfig,
} from '../types/api';

// API Configuration
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8001';
const API_PREFIX = '/api/v1';
const REQUEST_TIMEOUT = 60000; // 60 seconds

class APIService {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}${API_PREFIX}`;
  }

  /**
   * Generic request handler with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: 'An error occurred',
        }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      throw new Error('An unknown error occurred');
    }
  }

  /**
   * Health check endpoints
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health', { method: 'GET' });
  }

  async chatHealthCheck(): Promise<any> {
    return this.request('/chat/health', { method: 'GET' });
  }

  /**
   * Chat endpoints - Regular mode
   */
  async sendMessage(input: UserInput): Promise<ChatResponse> {
    return this.request('/chat/message', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  /**
   * Chat endpoints - Quick mode
   */
  async sendQuickMessage(input: QuickInput): Promise<QuickResponse> {
    return this.request('/chat/quick', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  /**
   * Chat endpoints - Raw mode
   */
  async sendRawMessage(input: RawInput): Promise<RawResponse> {
    return this.request('/chat/raw', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  /**
   * Rate a message response
   */
  async rateMessage(messageId: string, rating: UserRating): Promise<any> {
    return this.request(`/chat/rate/${messageId}`, {
      method: 'POST',
      body: JSON.stringify(rating),
    });
  }

  /**
   * Get conversation history
   */
  async getConversationHistory(
    conversationId: string,
    limit: number = 10
  ): Promise<any> {
    return this.request(
      `/chat/conversations/${conversationId}/history?limit=${limit}`,
      { method: 'GET' }
    );
  }

  /**
   * Get available models
   */
  async getAvailableModels(): Promise<any> {
    return this.request('/chat/models/available', { method: 'GET' });
  }

  /**
   * Configuration endpoints
   */
  async getThemes(): Promise<{ themes: ThemeConfig[] }> {
    return this.request('/config/themes', { method: 'GET' });
  }

  async getAudiences(): Promise<{ audiences: AudienceConfig[] }> {
    // Note: This endpoint might need to be added to backend
    // For now, return hardcoded values matching backend
    return Promise.resolve({
      audiences: [
        { id: 'small_kids', name: 'Small Kids', description: 'Ages 5-10' },
        { id: 'teenagers', name: 'Teenagers', description: 'Ages 11-17' },
        { id: 'adults', name: 'Adults', description: 'Ages 18-65' },
        { id: 'university_level', name: 'University Level', description: 'College/University students' },
        { id: 'professionals', name: 'Professionals', description: 'Industry professionals' },
        { id: 'seniors', name: 'Seniors', description: 'Ages 65+' },
      ],
    });
  }

  async getResponseStyles(): Promise<{ response_styles: ResponseStyleConfig[] }> {
    // Note: This endpoint might need to be added to backend
    // For now, return hardcoded values matching backend
    return Promise.resolve({
      response_styles: [
        {
          id: 'paragraph_brief',
          name: 'Paragraph Brief',
          output_length: 'short',
          description: 'One big paragraph with shorter, concise output',
        },
        {
          id: 'structured_detailed',
          name: 'Structured Detailed',
          output_length: 'long',
          description: 'Divided into points with more detailed, longer output',
        },
        {
          id: 'instructions_only',
          name: 'Instructions Only',
          output_length: 'short',
          description: 'Only instructions without background explanations',
        },
        {
          id: 'comprehensive',
          name: 'Comprehensive',
          output_length: 'very_long',
          description: 'With background and explanations (long and comprehensive)',
        },
      ],
    });
  }

  /**
   * Update the base URL (useful for switching environments)
   */
  setBaseURL(url: string) {
    this.baseURL = `${url}${API_PREFIX}`;
  }

  /**
   * Get the current base URL
   */
  getBaseURL(): string {
    return API_BASE_URL;
  }
}

// Export singleton instance
export const apiService = new APIService();
export default apiService;
