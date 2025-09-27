/**
 * TypeScript definitions for PromptYour.AI API
 * Generated from backend Pydantic schemas
 */

// Enums
export enum ThemeType {
  ACADEMIC_HELP = "academic_help",
  CREATIVE_WRITING = "creative_writing",
  CODING_PROGRAMMING = "coding_programming",
  BUSINESS_PROFESSIONAL = "business_professional",
  PERSONAL_LEARNING = "personal_learning",
  RESEARCH_ANALYSIS = "research_analysis",
  PROBLEM_SOLVING = "problem_solving",
  TUTORING_EDUCATION = "tutoring_education",
  GENERAL_QUESTIONS = "general_questions"
}

export enum AudienceType {
  SMALL_KIDS = "small_kids",           // Ages 5-10
  TEENAGERS = "teenagers",             // Ages 11-17
  ADULTS = "adults",                   // Ages 18-65
  UNIVERSITY_LEVEL = "university_level", // College/University
  PROFESSIONALS = "professionals",      // Industry experts
  SENIORS = "seniors"                  // Ages 65+
}

export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant"
}

// Core Message Types
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  model?: string;
  provider?: string;
  metadata?: {
    type?: 'quick' | 'enhanced' | 'error';
    model?: string;
    provider?: string;
    theme?: string;
    audience?: string;
  };
}

// Request Types
export interface QuickInput {
  question: string;
  conversation_id?: string;
  message_history?: ChatMessage[];
  force_model?: string;
  force_provider?: string;
}

export interface UserInput {
  question: string;
  theme: ThemeType;
  audience: AudienceType;
  context?: string;
  conversation_id?: string;
  message_history?: ChatMessage[];
  force_model?: string;
  force_provider?: string;
}

// Response Types
export interface QuickResponse {
  content: string;
  model_used: string;
  provider: string;
  message_id: string;
  cost: number;
  response_time_ms: number;
}

export interface ChatResponse {
  content: string;
  model_used: string;
  provider: string;
  message_id: string;
  cost: number;
  response_time_ms: number;
  reasoning: string;
}

// Provider Status Types
export interface ProviderStatus {
  provider: string;
  status: "healthy" | "unhealthy" | "unknown";
  details: string;
}

export interface ProvidersStatusResponse {
  status: "healthy" | "unhealthy";
  providers: ProviderStatus[];
}

// User Rating Types
export interface UserRating {
  message_id: string;
  rating: number; // 1-5
  feedback?: string;
}

// Conversation History Types
export interface ConversationHistoryResponse {
  conversation_id: string;
  messages: ChatMessage[];
  count: number;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'ping' | 'chat_request' | 'user_rating' | 'cancel_request' | 'get_conversation_history';
  data?: any;
  request_id?: string;
}

export interface WebSocketResponse {
  type: 'pong' | 'chat_response' | 'error' | 'processing_update' | 'conversation_history';
  data?: any;
  request_id?: string;
  error?: string;
}

// Theme and Audience Display Info
export interface ThemeInfo {
  id: ThemeType;
  name: string;
  description: string;
  icon: string;
  color: string;
}

export interface AudienceInfo {
  id: AudienceType;
  name: string;
  description: string;
  ageRange: string;
  icon: string;
}

// API Error Types
export interface APIError {
  detail: string;
  status_code: number;
}

// Configuration Types
export interface APIConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}