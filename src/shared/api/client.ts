/**
 * HTTP API Client for PromptYour.AI
 * Handles all REST API interactions with the backend
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import {
  QuickInput,
  QuickResponse,
  UserInput,
  ChatResponse,
  UserRating,
  ConversationHistoryResponse,
  ProvidersStatusResponse,
  APIConfig,
  APIError,
  DEFAULT_API_CONFIG
} from '../types';

export class PromptYourAIClient {
  private client: AxiosInstance;
  private config: APIConfig;

  constructor(config: Partial<APIConfig> = {}) {
    this.config = { ...DEFAULT_API_CONFIG, ...config };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for logging and auth (future)
    this.client.interceptors.request.use(
      (config) => {
        // Add auth headers when implemented
        // config.headers.Authorization = `Bearer ${token}`;
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config;

        // Handle retries
        if (error.response?.status === 500 && originalRequest && this.config.retryAttempts > 0) {
          await this.delay(this.config.retryDelay);
          this.config.retryAttempts--;
          return this.client.request(originalRequest);
        }

        return Promise.reject(this.handleAPIError(error));
      }
    );
  }

  private handleAPIError(error: AxiosError): APIError {
    if (error.response) {
      // Server responded with error status
      return {
        detail: (error.response.data as any)?.detail || 'Server error occurred',
        status_code: error.response.status
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        detail: 'Network error: Unable to reach server',
        status_code: 0
      };
    } else {
      // Something happened in setting up the request
      return {
        detail: `Request error: ${error.message}`,
        status_code: 0
      };
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Update configuration
  updateConfig(newConfig: Partial<APIConfig>) {
    this.config = { ...this.config, ...newConfig };
    this.client.defaults.baseURL = this.config.baseURL;
    this.client.defaults.timeout = this.config.timeout;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }

  // Quick chat endpoint
  async sendQuickMessage(input: QuickInput): Promise<QuickResponse> {
    const response = await this.client.post<QuickResponse>('/api/v1/chat/quick', input);
    return response.data;
  }

  // Enhanced chat endpoint
  async sendEnhancedMessage(input: UserInput): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/api/v1/chat/message', input);
    return response.data;
  }

  // Rate message
  async rateMessage(messageId: string, rating: UserRating): Promise<{ message: string; message_id: string; rating: number }> {
    const response = await this.client.post(`/api/v1/chat/rate/${messageId}`, rating);
    return response.data;
  }

  // Get conversation history
  async getConversationHistory(
    conversationId: string,
    limit: number = 10
  ): Promise<ConversationHistoryResponse> {
    const response = await this.client.get<ConversationHistoryResponse>(
      `/api/v1/chat/conversations/${conversationId}/history`,
      { params: { limit } }
    );
    return response.data;
  }

  // Get provider status
  async getProviderStatus(): Promise<ProvidersStatusResponse> {
    const response = await this.client.get<ProvidersStatusResponse>('/api/v1/providers/status');
    return response.data;
  }

  // Get available models
  async getAvailableModels(): Promise<{ models: any[]; count: number }> {
    const response = await this.client.get('/api/v1/chat/models/available');
    return response.data;
  }

  // Get available themes
  async getThemes(): Promise<{ themes: string[] }> {
    const response = await this.client.get('/api/v1/chat/options/themes');
    return response.data;
  }

  // Get available audiences
  async getAudiences(): Promise<{ audiences: string[] }> {
    const response = await this.client.get('/api/v1/chat/options/audiences');
    return response.data;
  }

  // Get available response styles
  async getResponseStyles(): Promise<{ response_styles: string[] }> {
    const response = await this.client.get('/api/v1/chat/options/response-styles');
    return response.data;
  }

  // Cancel request (for future implementation)
  async cancelRequest(requestId: string): Promise<void> {
    // This would be implemented when the backend supports request cancellation
    console.warn('Request cancellation not yet implemented in backend');
  }
}

// Singleton instance for easy usage
let defaultClient: PromptYourAIClient | null = null;

export const getDefaultClient = (config?: Partial<APIConfig>): PromptYourAIClient => {
  if (!defaultClient || config) {
    defaultClient = new PromptYourAIClient(config);
  }
  return defaultClient;
};

// Convenience functions using the default client
export const api = {
  healthCheck: () => getDefaultClient().healthCheck(),
  sendQuickMessage: (input: QuickInput) => getDefaultClient().sendQuickMessage(input),
  sendEnhancedMessage: (input: UserInput) => getDefaultClient().sendEnhancedMessage(input),
  rateMessage: (messageId: string, rating: UserRating) => getDefaultClient().rateMessage(messageId, rating),
  getConversationHistory: (conversationId: string, limit?: number) =>
    getDefaultClient().getConversationHistory(conversationId, limit),
  getProviderStatus: () => getDefaultClient().getProviderStatus(),
  getAvailableModels: () => getDefaultClient().getAvailableModels(),
};