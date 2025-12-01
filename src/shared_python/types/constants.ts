/**
 * Constants and display information for PromptYour.AI
 */

import { ThemeType, AudienceType, ThemeInfo, AudienceInfo } from './api';

export const THEME_INFO: Record<ThemeType, ThemeInfo> = {
  [ThemeType.ACADEMIC_HELP]: {
    id: ThemeType.ACADEMIC_HELP,
    name: "Academic Help",
    description: "Study support, homework assistance, and learning guidance",
    icon: "🎓",
    color: "#3B82F6"
  },
  [ThemeType.CREATIVE_WRITING]: {
    id: ThemeType.CREATIVE_WRITING,
    name: "Creative Writing",
    description: "Writing assistance, storytelling, and creative content",
    icon: "✍️",
    color: "#8B5CF6"
  },
  [ThemeType.CODING_PROGRAMMING]: {
    id: ThemeType.CODING_PROGRAMMING,
    name: "Coding & Programming",
    description: "Development help, code review, and technical guidance",
    icon: "💻",
    color: "#10B981"
  },
  [ThemeType.BUSINESS_PROFESSIONAL]: {
    id: ThemeType.BUSINESS_PROFESSIONAL,
    name: "Business & Professional",
    description: "Business strategy, professional development, and workplace advice",
    icon: "💼",
    color: "#F59E0B"
  },
  [ThemeType.PERSONAL_LEARNING]: {
    id: ThemeType.PERSONAL_LEARNING,
    name: "Personal Learning",
    description: "Self-directed learning, skill development, and growth",
    icon: "📚",
    color: "#EF4444"
  },
  [ThemeType.RESEARCH_ANALYSIS]: {
    id: ThemeType.RESEARCH_ANALYSIS,
    name: "Research & Analysis",
    description: "Research methods, data analysis, and investigation",
    icon: "🔬",
    color: "#06B6D4"
  },
  [ThemeType.PROBLEM_SOLVING]: {
    id: ThemeType.PROBLEM_SOLVING,
    name: "Problem Solving",
    description: "Systematic problem resolution and critical thinking",
    icon: "🧩",
    color: "#84CC16"
  },
  [ThemeType.TUTORING_EDUCATION]: {
    id: ThemeType.TUTORING_EDUCATION,
    name: "Tutoring & Education",
    description: "Educational support, teaching methods, and learning strategies",
    icon: "👩‍🏫",
    color: "#EC4899"
  },
  [ThemeType.GENERAL_QUESTIONS]: {
    id: ThemeType.GENERAL_QUESTIONS,
    name: "General Questions",
    description: "General knowledge, information, and everyday questions",
    icon: "❓",
    color: "#6B7280"
  }
};

export const AUDIENCE_INFO: Record<AudienceType, AudienceInfo> = {
  [AudienceType.SMALL_KIDS]: {
    id: AudienceType.SMALL_KIDS,
    name: "Small Kids",
    description: "Simple language, encouraging tone, age-appropriate content",
    ageRange: "Ages 5-10",
    icon: "👶"
  },
  [AudienceType.TEENAGERS]: {
    id: AudienceType.TEENAGERS,
    name: "Teenagers",
    description: "Relatable examples, engaging content, modern references",
    ageRange: "Ages 11-17",
    icon: "👦"
  },
  [AudienceType.ADULTS]: {
    id: AudienceType.ADULTS,
    name: "Adults",
    description: "Professional, practical approach with real-world context",
    ageRange: "Ages 18-65",
    icon: "👩"
  },
  [AudienceType.UNIVERSITY_LEVEL]: {
    id: AudienceType.UNIVERSITY_LEVEL,
    name: "University Level",
    description: "Academic rigor, critical thinking, scholarly approach",
    ageRange: "College/University",
    icon: "🎓"
  },
  [AudienceType.PROFESSIONALS]: {
    id: AudienceType.PROFESSIONALS,
    name: "Professionals",
    description: "Expert-level content, results-oriented, industry-focused",
    ageRange: "Industry Experts",
    icon: "💼"
  },
  [AudienceType.SENIORS]: {
    id: AudienceType.SENIORS,
    name: "Seniors",
    description: "Respectful, patient explanations with clear structure",
    ageRange: "Ages 65+",
    icon: "👴"
  }
};

// Default values
export const DEFAULT_THEME = ThemeType.GENERAL_QUESTIONS;
export const DEFAULT_AUDIENCE = AudienceType.ADULTS;

// API Configuration defaults
export const DEFAULT_API_CONFIG = {
  baseURL: "http://localhost:8000",
  timeout: 60000,
  retryAttempts: 3,
  retryDelay: 1000
};

// WebSocket Configuration
export const DEFAULT_WS_CONFIG = {
  reconnectAttempts: 5,
  reconnectDelay: 1000,
  heartbeatInterval: 30000
};

// Chat Configuration
export const CHAT_CONFIG = {
  maxMessageHistory: 50,
  quickResponseTimeout: 30000,
  enhancedResponseTimeout: 120000,
  typingIndicatorDelay: 500
};