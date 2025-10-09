/**
 * Chat Store
 * Manages chat messages and conversation state
 */

import { create } from 'zustand';
import {
  ChatMessage,
  MessageRole,
  ChatResponse,
  QuickResponse,
  RawResponse,
  ChatMode,
} from '../types/api';

interface ChatState {
  // Current conversation
  conversationId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;

  // Current response metadata
  currentMessageId: string | null;
  currentModel: string | null;
  currentProvider: string | null;
  currentCost: number;
  currentResponseTime: number;
  currentReasoning: string | null;
  currentSystemPrompt: string | null;

  // WebSocket state
  isConnected: boolean;
  processingStatus: string | null;

  // Chat mode
  chatMode: ChatMode;

  // Actions
  setConversationId: (id: string) => void;
  addMessage: (message: ChatMessage) => void;
  addUserMessage: (content: string) => void;
  addAssistantMessage: (
    response: ChatResponse | QuickResponse | RawResponse
  ) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  setConnected: (isConnected: boolean) => void;
  setProcessingStatus: (status: string | null) => void;
  setChatMode: (mode: ChatMode) => void;
  clearMessages: () => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  // Initial state
  conversationId: null,
  messages: [],
  isLoading: false,
  error: null,
  currentMessageId: null,
  currentModel: null,
  currentProvider: null,
  currentCost: 0,
  currentResponseTime: 0,
  currentReasoning: null,
  currentSystemPrompt: null,
  isConnected: false,
  processingStatus: null,
  chatMode: ChatMode.REGULAR,

  // Actions
  setConversationId: (id) => set({ conversationId: id }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  addUserMessage: (content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          role: MessageRole.USER,
          content,
          timestamp: new Date().toISOString(),
        },
      ],
    })),

  addAssistantMessage: (response) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          role: MessageRole.ASSISTANT,
          content: response.content,
          timestamp: new Date().toISOString(),
          model: response.model_used,
          provider: response.provider,
        },
      ],
      currentMessageId: response.message_id,
      currentModel: response.model_used,
      currentProvider: response.provider,
      currentCost: response.cost,
      currentResponseTime: response.response_time_ms,
      currentReasoning: 'reasoning' in response ? response.reasoning : null,
      currentSystemPrompt: response.system_prompt,
      isLoading: false,
      error: null,
    })),

  setLoading: (isLoading) => set({ isLoading, error: null }),

  setError: (error) => set({ error, isLoading: false }),

  setConnected: (isConnected) => set({ isConnected }),

  setProcessingStatus: (processingStatus) => set({ processingStatus }),

  setChatMode: (chatMode) => set({ chatMode }),

  clearMessages: () =>
    set({
      messages: [],
      currentMessageId: null,
      currentModel: null,
      currentProvider: null,
      currentCost: 0,
      currentResponseTime: 0,
      currentReasoning: null,
      currentSystemPrompt: null,
      error: null,
    }),

  reset: () =>
    set({
      conversationId: null,
      messages: [],
      isLoading: false,
      error: null,
      currentMessageId: null,
      currentModel: null,
      currentProvider: null,
      currentCost: 0,
      currentResponseTime: 0,
      currentReasoning: null,
      currentSystemPrompt: null,
      isConnected: false,
      processingStatus: null,
    }),
}));
