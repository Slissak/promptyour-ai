/**
 * Mobile API Service
 * Wrapper around shared API client for mobile-specific functionality
 */

import { PromptYourAIClient } from '../shared/api/client';
import { getConversationManager } from '../shared/utils/conversation';
import type {
  QuickInput,
  QuickResponse,
  UserInput,
  ChatResponse,
  ChatMessage,
  MessageRole,
  ThemeType,
  AudienceType
} from '../shared/types/api';
import { API_CONFIG } from '../constants/Config';

export class MobileApiService {
  private client: PromptYourAIClient;
  private conversationManager = getConversationManager();

  constructor() {
    this.client = new PromptYourAIClient({
      baseURL: API_CONFIG.baseURL,
      timeout: API_CONFIG.timeout,
      retryAttempts: API_CONFIG.retryAttempts,
      retryDelay: API_CONFIG.retryDelay,
    });
  }

  // Quick response methods
  async sendQuickMessage(question: string): Promise<QuickResponse> {
    const conversationId = this.getOrCreateActiveConversation();
    const messageHistory = this.conversationManager.getMessageHistory(conversationId);

    const input: QuickInput = {
      question,
      conversation_id: conversationId,
      message_history: messageHistory,
    };

    const response = await this.client.sendQuickMessage(input);

    // Store in conversation history
    this.conversationManager.addUserMessage(conversationId, question);
    this.conversationManager.addQuickResponse(conversationId, response);

    return response;
  }

  // Enhanced response methods
  async sendEnhancedMessage(
    question: string,
    theme: ThemeType,
    audience: AudienceType
  ): Promise<ChatResponse> {
    const conversationId = this.getOrCreateActiveConversation();
    const messageHistory = this.conversationManager.getMessageHistory(conversationId);

    const input: UserInput = {
      question,
      theme,
      audience,
      conversation_id: conversationId,
      message_history: messageHistory,
    };

    const response = await this.client.sendEnhancedMessage(input);

    // Update conversation history (replace quick response if exists)
    this.conversationManager.addEnhancedResponse(conversationId, response);

    return response;
  }

  // Conversation management
  private getOrCreateActiveConversation(): string {
    let activeConversation = this.conversationManager.getActiveConversation();

    if (!activeConversation) {
      const conversationId = this.conversationManager.createConversation();
      this.conversationManager.setActiveConversation(conversationId);
      return conversationId;
    }

    return activeConversation.metadata.id;
  }

  startNewConversation(): string {
    const conversationId = this.conversationManager.createConversation();
    this.conversationManager.setActiveConversation(conversationId);
    return conversationId;
  }

  getConversationHistory(conversationId?: string): ChatMessage[] {
    const id = conversationId || this.getOrCreateActiveConversation();
    return this.conversationManager.getMessageHistory(id);
  }

  getAllConversations() {
    return this.conversationManager.getAllConversations();
  }

  // Health check
  async checkApiHealth(): Promise<boolean> {
    try {
      await this.client.getProviderStatus();
      return true;
    } catch (error) {
      console.warn('API health check failed:', error);
      return false;
    }
  }

  // Provider status
  async getProviderStatus() {
    return this.client.getProviderStatus();
  }

  // Error handling helper
  handleApiError(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    } else if (error.message) {
      return error.message;
    } else {
      return 'An unexpected error occurred. Please try again.';
    }
  }
}

// Singleton instance
let apiService: MobileApiService | null = null;

export const getMobileApiService = (): MobileApiService => {
  if (!apiService) {
    apiService = new MobileApiService();
  }
  return apiService;
};