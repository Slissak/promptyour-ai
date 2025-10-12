/**
 * Conversation History Management Utilities
 * Handles conversation state, message history, and persistence
 */

import {
  ChatMessage,
  MessageRole,
  QuickResponse,
  ChatResponse,
  ThemeType,
  AudienceType,
  CHAT_CONFIG
} from '../types';

export interface ConversationMetadata {
  id: string;
  title?: string;
  theme?: ThemeType;
  audience?: AudienceType;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastMessage?: string;
}

export interface Conversation {
  metadata: ConversationMetadata;
  messages: ChatMessage[];
}

export class ConversationManager {
  private conversations = new Map<string, Conversation>();
  private activeConversationId: string | null = null;

  constructor() {
    // Don't load from storage - start fresh on each page load
    // this.loadFromStorage();
  }

  // Conversation lifecycle
  createConversation(
    theme?: ThemeType,
    audience?: AudienceType,
    initialMessage?: string
  ): string {
    const id = this.generateConversationId();
    const now = new Date().toISOString();

    const conversation: Conversation = {
      metadata: {
        id,
        theme,
        audience,
        title: this.generateTitle(initialMessage),
        createdAt: now,
        updatedAt: now,
        messageCount: 0,
        lastMessage: initialMessage
      },
      messages: []
    };

    this.conversations.set(id, conversation);
    this.activeConversationId = id;
    this.saveToStorage();

    return id;
  }

  getConversation(id: string): Conversation | null {
    return this.conversations.get(id) || null;
  }

  getActiveConversation(): Conversation | null {
    if (!this.activeConversationId) {
      return null;
    }
    return this.getConversation(this.activeConversationId);
  }

  setActiveConversation(id: string): boolean {
    if (this.conversations.has(id)) {
      this.activeConversationId = id;
      return true;
    }
    return false;
  }

  deleteConversation(id: string): boolean {
    const deleted = this.conversations.delete(id);
    if (deleted) {
      if (this.activeConversationId === id) {
        this.activeConversationId = null;
      }
      this.saveToStorage();
    }
    return deleted;
  }

  getAllConversations(): ConversationMetadata[] {
    return Array.from(this.conversations.values())
      .map(conv => conv.metadata)
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  }

  // Message management
  addUserMessage(conversationId: string, content: string): boolean {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      return false;
    }

    const message: ChatMessage = {
      id: Date.now().toString(),
      role: MessageRole.USER,
      content,
      timestamp: new Date().toISOString()
    };

    conversation.messages.push(message);
    this.updateConversationMetadata(conversationId, content);
    this.saveToStorage();

    return true;
  }

  addQuickResponse(conversationId: string, response: QuickResponse): boolean {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      return false;
    }

    const message: ChatMessage = {
      id: response.message_id,
      role: MessageRole.ASSISTANT,
      content: response.content,
      timestamp: new Date().toISOString(),
      model: response.model_used,
      provider: response.provider
    };

    conversation.messages.push(message);
    this.updateConversationMetadata(conversationId, response.content);
    this.saveToStorage();

    return true;
  }

  addEnhancedResponse(conversationId: string, response: ChatResponse): boolean {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      return false;
    }

    // Replace the last assistant message if it exists (quick response)
    // This handles the case where user gets quick response then enhanced
    const lastMessage = conversation.messages[conversation.messages.length - 1];
    if (lastMessage && lastMessage.role === MessageRole.ASSISTANT) {
      conversation.messages[conversation.messages.length - 1] = {
        id: response.message_id,
        role: MessageRole.ASSISTANT,
        content: response.content,
        timestamp: new Date().toISOString(),
        model: response.model_used,
        provider: response.provider
      };
    } else {
      // Add new message if no quick response to replace
      conversation.messages.push({
        id: response.message_id,
        role: MessageRole.ASSISTANT,
        content: response.content,
        timestamp: new Date().toISOString(),
        model: response.model_used,
        provider: response.provider
      });
    }

    this.updateConversationMetadata(conversationId, response.content);
    this.saveToStorage();

    return true;
  }

  getMessageHistory(conversationId: string, limit?: number): ChatMessage[] {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      return [];
    }

    const messages = conversation.messages;
    const maxLimit = limit || CHAT_CONFIG.maxMessageHistory;

    return messages.slice(-maxLimit);
  }

  clearConversationHistory(conversationId: string): boolean {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      return false;
    }

    conversation.messages = [];
    conversation.metadata.messageCount = 0;
    conversation.metadata.updatedAt = new Date().toISOString();
    this.saveToStorage();

    return true;
  }

  clearAllConversations(): void {
    this.conversations.clear();
    this.activeConversationId = null;
    // Clear localStorage
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.removeItem('promptyour_conversations');
      } catch (error) {
        console.error('Failed to clear conversations from localStorage:', error);
      }
    }
  }

  // Utility methods
  private generateConversationId(): string {
    return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateTitle(initialMessage?: string): string {
    if (!initialMessage) {
      return 'New Conversation';
    }

    // Create a title from the first few words
    const words = initialMessage.split(' ').slice(0, 6);
    let title = words.join(' ');

    if (initialMessage.split(' ').length > 6) {
      title += '...';
    }

    return title.length > 50 ? title.slice(0, 47) + '...' : title;
  }

  private updateConversationMetadata(conversationId: string, lastMessage: string) {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      return;
    }

    conversation.metadata.updatedAt = new Date().toISOString();
    conversation.metadata.messageCount = conversation.messages.length;
    conversation.metadata.lastMessage = lastMessage.length > 100
      ? lastMessage.slice(0, 97) + '...'
      : lastMessage;

    // Update title if it's still the default
    if (conversation.metadata.title === 'New Conversation' && conversation.messages.length === 1) {
      const firstUserMessage = conversation.messages.find(m => m.role === MessageRole.USER);
      if (firstUserMessage) {
        conversation.metadata.title = this.generateTitle(firstUserMessage.content);
      }
    }
  }

  // Persistence (localStorage for web, AsyncStorage for mobile)
  // Disabled - user wants fresh start on each page reload and new chat
  private saveToStorage() {
    // Persistence disabled - conversations don't persist across page reloads
    // This ensures clean history management per session
    return;
  }

  private loadFromStorage() {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const stored = localStorage.getItem('promptyour_conversations');
        if (stored) {
          const data = JSON.parse(stored);
          this.conversations = new Map(data.conversations || []);
          this.activeConversationId = data.activeConversationId || null;
        }
      } catch (error) {
        console.error('Failed to load conversations from localStorage:', error);
      }
    }
  }

  // Export/Import functionality
  exportConversations(): string {
    const data = {
      conversations: Array.from(this.conversations.entries()),
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
    return JSON.stringify(data, null, 2);
  }

  importConversations(jsonData: string): boolean {
    try {
      const data = JSON.parse(jsonData);
      if (data.conversations && Array.isArray(data.conversations)) {
        // Merge with existing conversations
        const importedConversations = new Map(data.conversations);
        for (const [id, conversation] of importedConversations) {
          this.conversations.set(id as string, conversation as Conversation);
        }
        this.saveToStorage();
        return true;
      }
    } catch (error) {
      console.error('Failed to import conversations:', error);
    }
    return false;
  }

  // Search functionality
  searchConversations(query: string): ConversationMetadata[] {
    const lowercaseQuery = query.toLowerCase();
    return this.getAllConversations().filter(conv =>
      conv.title?.toLowerCase().includes(lowercaseQuery) ||
      conv.lastMessage?.toLowerCase().includes(lowercaseQuery)
    );
  }

  searchMessages(conversationId: string, query: string): ChatMessage[] {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      return [];
    }

    const lowercaseQuery = query.toLowerCase();
    return conversation.messages.filter(message =>
      message.content.toLowerCase().includes(lowercaseQuery)
    );
  }
}

// Singleton instance
let conversationManager: ConversationManager | null = null;

export const getConversationManager = (): ConversationManager => {
  if (!conversationManager) {
    conversationManager = new ConversationManager();
  }
  return conversationManager;
};