/**
 * WebSocket Service Layer
 * Handles real-time communication with the backend via WebSocket
 */

import {
  WSMessage,
  WSChatRequest,
  WSChatResponse,
  WSError,
  WSProcessingUpdate,
  ChatMode,
  UserInput,
  QuickInput,
  RawInput,
  ChatResponse,
  QuickResponse,
  RawResponse,
} from '../types/api';

// WebSocket Configuration
const WS_BASE_URL = process.env.EXPO_PUBLIC_WS_URL || 'ws://localhost:8001';
const WS_PREFIX = '/api/v1/ws';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 5;
const HEARTBEAT_INTERVAL = 30000; // 30 seconds

type MessageHandler = (message: WSMessage) => void;
type ConnectionHandler = () => void;
type ErrorHandler = (error: Error) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private userId: string;
  private conversationId: string | null = null;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private connectionHandlers: ConnectionHandler[] = [];
  private disconnectionHandlers: ConnectionHandler[] = [];
  private errorHandlers: ErrorHandler[] = [];
  private isManualDisconnect = false;

  constructor(userId: string) {
    this.userId = userId;
  }

  /**
   * Connect to WebSocket server
   */
  connect(conversationId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        if (this.ws?.readyState === WebSocket.OPEN) {
          resolve();
          return;
        }

        this.conversationId = conversationId || null;
        this.isManualDisconnect = false;

        const params = new URLSearchParams({ user_id: this.userId });
        if (this.conversationId) {
          params.append('conversation_id', this.conversationId);
        }

        const wsUrl = `${WS_BASE_URL}${WS_PREFIX}/chat?${params.toString()}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.connectionHandlers.forEach((handler) => handler());
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data) as WSMessage;
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          const err = new Error('WebSocket error occurred');
          this.errorHandlers.forEach((handler) => handler(err));
          reject(err);
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Disconnected');
          this.stopHeartbeat();
          this.disconnectionHandlers.forEach((handler) => handler());

          if (!this.isManualDisconnect) {
            this.attemptReconnect();
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    this.isManualDisconnect = true;
    this.stopHeartbeat();

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Attempt to reconnect
   */
  private attemptReconnect() {
    if (this.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.error('[WebSocket] Max reconnect attempts reached');
      const error = new Error('Failed to reconnect after multiple attempts');
      this.errorHandlers.forEach((handler) => handler(error));
      return;
    }

    this.reconnectAttempts++;
    console.log(
      `[WebSocket] Attempting to reconnect (${this.reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`
    );

    this.reconnectTimer = setTimeout(() => {
      this.connect(this.conversationId || undefined).catch((error) => {
        console.error('[WebSocket] Reconnect failed:', error);
      });
    }, RECONNECT_DELAY);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, HEARTBEAT_INTERVAL);
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * Send a message through WebSocket
   */
  private send(message: WSMessage) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      throw new Error('WebSocket is not connected');
    }
  }

  /**
   * Send a chat request
   */
  sendChatMessage(
    mode: ChatMode,
    data: UserInput | QuickInput | RawInput
  ): Promise<ChatResponse | QuickResponse | RawResponse> {
    return new Promise((resolve, reject) => {
      try {
        const message: WSChatRequest = {
          type: 'chat_request',
          mode,
          data,
        };

        // Set up one-time listener for response
        const responseHandler = (msg: WSMessage) => {
          if (msg.type === 'chat_response') {
            this.off('chat_response', responseHandler);
            this.off('error', errorHandler);
            resolve((msg as WSChatResponse).data);
          }
        };

        const errorHandler = (msg: WSMessage) => {
          if (msg.type === 'error') {
            this.off('chat_response', responseHandler);
            this.off('error', errorHandler);
            reject(new Error((msg as WSError).error));
          }
        };

        this.on('chat_response', responseHandler);
        this.on('error', errorHandler);

        this.send(message);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: WSMessage) {
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach((handler) => handler(message));

    // Also call handlers for 'all' type
    const allHandlers = this.messageHandlers.get('all') || [];
    allHandlers.forEach((handler) => handler(message));
  }

  /**
   * Register a message handler
   */
  on(messageType: string, handler: MessageHandler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, []);
    }
    this.messageHandlers.get(messageType)!.push(handler);
  }

  /**
   * Unregister a message handler
   */
  off(messageType: string, handler: MessageHandler) {
    const handlers = this.messageHandlers.get(messageType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Register a connection handler
   */
  onConnect(handler: ConnectionHandler) {
    this.connectionHandlers.push(handler);
  }

  /**
   * Register a disconnection handler
   */
  onDisconnect(handler: ConnectionHandler) {
    this.disconnectionHandlers.push(handler);
  }

  /**
   * Register an error handler
   */
  onError(handler: ErrorHandler) {
    this.errorHandlers.push(handler);
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state
   */
  getState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

// Export factory function to create instances
export const createWebSocketService = (userId: string) => {
  return new WebSocketService(userId);
};
