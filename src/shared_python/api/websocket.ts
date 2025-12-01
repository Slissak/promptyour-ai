/**
 * WebSocket Client for PromptYour.AI Real-time Chat
 * Handles WebSocket connections with automatic reconnection and message management
 */

import {
  WebSocketMessage,
  WebSocketResponse,
  QuickInput,
  UserInput,
  UserRating,
  DEFAULT_WS_CONFIG
} from '../types';

type EventCallback = (data: any) => void;
type ErrorCallback = (error: Error) => void;
type ConnectionCallback = () => void;

interface WebSocketConfig {
  reconnectAttempts: number;
  reconnectDelay: number;
  heartbeatInterval: number;
}

export class PromptYourAIWebSocket {
  private ws: WebSocket | null = null;
  private baseUrl: string;
  private userId: string;
  private conversationId: string;
  private config: WebSocketConfig;
  private reconnectCount = 0;
  private heartbeatTimer?: NodeJS.Timeout;
  private requestCallbacks = new Map<string, (response: WebSocketResponse) => void>();
  private eventListeners = new Map<string, EventCallback[]>();

  constructor(
    baseUrl: string,
    userId: string,
    conversationId: string,
    config: Partial<WebSocketConfig> = {}
  ) {
    this.baseUrl = baseUrl.replace('http:', 'ws:').replace('https:', 'wss:');
    this.userId = userId;
    this.conversationId = conversationId;
    this.config = { ...DEFAULT_WS_CONFIG, ...config };
  }

  // Event listener management
  on(event: string, callback: EventCallback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  off(event: string, callback?: EventCallback) {
    if (!callback) {
      this.eventListeners.delete(event);
      return;
    }

    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
  }

  // Connection management
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.baseUrl}/api/v1/ws/chat?user_id=${this.userId}&conversation_id=${this.conversationId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectCount = 0;
          this.startHeartbeat();
          this.emit('connected', null);
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const response: WebSocketResponse = JSON.parse(event.data);
            this.handleMessage(response);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.stopHeartbeat();
          this.emit('disconnected', { code: event.code, reason: event.reason });

          // Attempt to reconnect if not closed intentionally
          if (event.code !== 1000 && this.reconnectCount < this.config.reconnectAttempts) {
            this.attemptReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.emit('error', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  private async attemptReconnect() {
    this.reconnectCount++;
    console.log(`Attempting to reconnect (${this.reconnectCount}/${this.config.reconnectAttempts})`);

    await new Promise(resolve => setTimeout(resolve, this.config.reconnectDelay));

    try {
      await this.connect();
    } catch (error) {
      console.error('Reconnection failed:', error);
      if (this.reconnectCount >= this.config.reconnectAttempts) {
        this.emit('reconnectFailed', null);
      }
    }
  }

  disconnect() {
    if (this.ws) {
      this.stopHeartbeat();
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }
  }

  // Heartbeat management
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping' });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
  }

  // Message handling
  private handleMessage(response: WebSocketResponse) {
    // Handle request-specific callbacks
    if (response.request_id && this.requestCallbacks.has(response.request_id)) {
      const callback = this.requestCallbacks.get(response.request_id)!;
      callback(response);
      this.requestCallbacks.delete(response.request_id);
      return;
    }

    // Handle different message types
    switch (response.type) {
      case 'pong':
        // Heartbeat response - no action needed
        break;

      case 'chat_response':
        this.emit('chatResponse', response.data);
        break;

      case 'error':
        this.emit('error', new Error(response.error || 'Unknown WebSocket error'));
        break;

      case 'processing_update':
        this.emit('processingUpdate', response.data);
        break;

      case 'conversation_history':
        this.emit('conversationHistory', response.data);
        break;

      default:
        console.warn('Unknown WebSocket message type:', response.type);
    }
  }

  // Send message with optional callback
  private send(message: WebSocketMessage, callback?: (response: WebSocketResponse) => void): void {
    if (!this.isConnected()) {
      throw new Error('WebSocket is not connected');
    }

    if (callback && message.request_id) {
      this.requestCallbacks.set(message.request_id, callback);
    }

    this.ws!.send(JSON.stringify(message));
  }

  // Generate unique request ID
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Public API methods
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // Send quick chat message
  async sendQuickMessage(input: QuickInput): Promise<WebSocketResponse> {
    return new Promise((resolve, reject) => {
      if (!this.isConnected()) {
        reject(new Error('WebSocket is not connected'));
        return;
      }

      const requestId = this.generateRequestId();
      const message: WebSocketMessage = {
        type: 'chat_request',
        data: { ...input, quick: true },
        request_id: requestId
      };

      this.send(message, (response) => {
        if (response.type === 'error') {
          reject(new Error(response.error));
        } else {
          resolve(response);
        }
      });

      // Set timeout
      setTimeout(() => {
        if (this.requestCallbacks.has(requestId)) {
          this.requestCallbacks.delete(requestId);
          reject(new Error('Request timeout'));
        }
      }, 30000); // 30 second timeout for quick messages
    });
  }

  // Send enhanced chat message
  async sendEnhancedMessage(input: UserInput): Promise<WebSocketResponse> {
    return new Promise((resolve, reject) => {
      if (!this.isConnected()) {
        reject(new Error('WebSocket is not connected'));
        return;
      }

      const requestId = this.generateRequestId();
      const message: WebSocketMessage = {
        type: 'chat_request',
        data: { ...input, quick: false },
        request_id: requestId
      };

      this.send(message, (response) => {
        if (response.type === 'error') {
          reject(new Error(response.error));
        } else {
          resolve(response);
        }
      });

      // Set timeout
      setTimeout(() => {
        if (this.requestCallbacks.has(requestId)) {
          this.requestCallbacks.delete(requestId);
          reject(new Error('Request timeout'));
        }
      }, 120000); // 2 minute timeout for enhanced messages
    });
  }

  // Rate message
  rateMessage(rating: UserRating): void {
    const message: WebSocketMessage = {
      type: 'user_rating',
      data: rating
    };

    this.send(message);
  }

  // Get conversation history
  async getConversationHistory(): Promise<WebSocketResponse> {
    return new Promise((resolve, reject) => {
      if (!this.isConnected()) {
        reject(new Error('WebSocket is not connected'));
        return;
      }

      const requestId = this.generateRequestId();
      const message: WebSocketMessage = {
        type: 'get_conversation_history',
        request_id: requestId
      };

      this.send(message, (response) => {
        if (response.type === 'error') {
          reject(new Error(response.error));
        } else {
          resolve(response);
        }
      });

      // Set timeout
      setTimeout(() => {
        if (this.requestCallbacks.has(requestId)) {
          this.requestCallbacks.delete(requestId);
          reject(new Error('Request timeout'));
        }
      }, 10000); // 10 second timeout for history requests
    });
  }

  // Cancel request
  cancelRequest(requestId?: string): void {
    const message: WebSocketMessage = {
      type: 'cancel_request',
      data: { request_id: requestId }
    };

    this.send(message);
  }
}