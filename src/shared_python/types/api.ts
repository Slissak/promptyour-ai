/**
 * TypeScript types matching backend API schemas
 * Based on src/backend/app/models/schemas.py
 */

// Enums matching backend configuration
export enum ThemeType {
  ACADEMIC_HELP = 'academic_help',
  CREATIVE_WRITING = 'creative_writing',
  CODING_PROGRAMMING = 'coding_programming',
  BUSINESS_PROFESSIONAL = 'business_professional',
  PERSONAL_LEARNING = 'personal_learning',
  RESEARCH_ANALYSIS = 'research_analysis',
  PROBLEM_SOLVING = 'problem_solving',
  TUTORING_EDUCATION = 'tutoring_education',
  GENERAL_QUESTIONS = 'general_questions',
}

export enum AudienceType {
  SMALL_KIDS = 'small_kids',
  TEENAGERS = 'teenagers',
  ADULTS = 'adults',
  UNIVERSITY_LEVEL = 'university_level',
  PROFESSIONALS = 'professionals',
  SENIORS = 'seniors',
}

export enum ResponseStyle {
  PARAGRAPH_BRIEF = 'paragraph_brief',
  STRUCTURED_DETAILED = 'structured_detailed',
  INSTRUCTIONS_ONLY = 'instructions_only',
  COMPREHENSIVE = 'comprehensive',
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
}

export enum ChatMode {
  REGULAR = 'regular',
  QUICK = 'quick',
  RAW = 'raw',
}

// Message Types
export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp?: string;
  model?: string;
  provider?: string;
}

// Input Types
export interface UserInput {
  question: string;
  theme: ThemeType;
  audience: AudienceType;
  response_style: ResponseStyle;
  context?: string;
  conversation_id?: string;
  message_history?: ChatMessage[];
  force_model?: string;
  force_provider?: string;
}

export interface QuickInput {
  question: string;
  conversation_id?: string;
  message_history?: ChatMessage[];
  force_model?: string;
  force_provider?: string;
}

export interface RawInput {
  question: string;
  conversation_id?: string;
  message_history?: ChatMessage[];
  force_model?: string;
  force_provider?: string;
}

// Response Types
export interface ChatResponse {
  content: string;
  model_used: string;
  provider: string;
  message_id: string;
  cost: number;
  response_time_ms: number;
  reasoning: string;
  system_prompt: string;
  raw_response?: string;
  thinking?: string;
}

export interface QuickResponse {
  content: string;
  model_used: string;
  provider: string;
  message_id: string;
  cost: number;
  response_time_ms: number;
  system_prompt: string;
  thinking?: string;
}

export interface RawResponse {
  content: string;
  model_used: string;
  provider: string;
  message_id: string;
  cost: number;
  response_time_ms: number;
  system_prompt: string;
  thinking?: string;
}

// Rating
export interface UserRating {
  message_id: string;
  rating: number; // 1-5
  feedback?: string;
}

// WebSocket Message Types
export interface WSMessage {
  type: string;
  [key: string]: any;
}

export interface WSChatRequest extends WSMessage {
  type: 'chat_request';
  mode: ChatMode;
  data: UserInput | QuickInput | RawInput;
}

export interface WSChatResponse extends WSMessage {
  type: 'chat_response';
  data: ChatResponse | QuickResponse | RawResponse;
}

export interface WSError extends WSMessage {
  type: 'error';
  error: string;
  details?: string;
}

export interface WSProcessingUpdate extends WSMessage {
  type: 'processing_update';
  status: string;
  message?: string;
}

// Configuration Types
export interface ThemeConfig {
  id: string;
  name: string;
  description: string;
}

export interface AudienceConfig {
  id: string;
  name: string;
  description: string;
}

export interface ResponseStyleConfig {
  id: string;
  name: string;
  output_length: string;
  description: string;
}

// API Configuration
export interface APIConfig {
  baseURL: string;
  wsURL: string;
  timeout: number;
}
