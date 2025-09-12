/**
 * Application Constants and Configuration
 * 
 * Centralized configuration management
 * Senior pattern: Environment-aware configuration with type safety
 */

// Environment Configuration
export const ENV = {
  NODE_ENV: process.env.NODE_ENV as 'development' | 'production' | 'test',
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  IS_DEVELOPMENT: process.env.NODE_ENV === 'development',
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
  IS_TEST: process.env.NODE_ENV === 'test',
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
  },
  EXAMS: {
    PUBLIC: '/public/exams',
    PRIVATE: '/private/admin/exams',
  },
  USER_EXAMS: '/private/users/me/exams',
  USERS: '/private/admin/users',
  VOTE_ASSIGNMENTS: '/private/supervisor/vote-assignments',
} as const;

// UI Constants
export const UI = {
  DEBOUNCE_DELAY: 300,
  TOAST_DURATION: 5000,
  LOADING_DELAY: 200, // Delay before showing loading spinner
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
} as const;

// User Roles
export const USER_ROLES = {
  ADMIN: 'admin',
  SUPERVISOR: 'supervisor', 
  USER: 'user',
} as const;

export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];

// Role Permissions
export const PERMISSIONS = {
  [USER_ROLES.ADMIN]: {
    canCreateExam: true,
    canAssignVotes: false,
    canViewAllUsers: true,
    canManageUsers: true,
  },
  [USER_ROLES.SUPERVISOR]: {
    canCreateExam: false,
    canAssignVotes: true,
    canViewAllUsers: true,
    canManageUsers: false,
  },
  [USER_ROLES.USER]: {
    canCreateExam: false,
    canAssignVotes: false,
    canViewAllUsers: false,
    canManageUsers: false,
  },
} as const;

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
} as const;

// Theme Configuration
export const THEME = {
  COLORS: {
    primary: {
      50: '#eff6ff',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
    },
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      500: '#6b7280',
      600: '#4b5563',
      900: '#111827',
    },
    red: {
      500: '#ef4444',
      600: '#dc2626',
    },
    green: {
      500: '#10b981',
      600: '#059669',
    },
  },
} as const;

// Validation Rules
export const VALIDATION = {
  EMAIL: {
    PATTERN: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
    MAX_LENGTH: 254,
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
  },
  EXAM_TITLE: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 100,
  },
} as const;

// Date/Time Formats
export const DATE_FORMATS = {
  DISPLAY: 'MMM d, yyyy',
  DISPLAY_WITH_TIME: 'MMM d, yyyy h:mm a',
  INPUT: 'yyyy-MM-dd',
  ISO: 'yyyy-MM-dd\'T\'HH:mm:ss.SSSxxx',
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  GENERIC: 'An unexpected error occurred. Please try again.',
  NETWORK: 'Network error. Please check your connection and try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION: 'Please check your input and try again.',
  SESSION_EXPIRED: 'Your session has expired. Please login again.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  EXAM_CREATED: 'Exam created successfully!',
  VOTE_ASSIGNED: 'Vote assigned successfully!',
  LOGIN: 'Welcome back!',
  LOGOUT: 'Logged out successfully.',
  PROFILE_UPDATED: 'Profile updated successfully!',
} as const;

// Feature Flags (for A/B testing, gradual rollouts)
export const FEATURES = {
  ENABLE_DARK_MODE: ENV.IS_DEVELOPMENT,
  ENABLE_ANALYTICS: ENV.IS_PRODUCTION,
  ENABLE_ERROR_REPORTING: ENV.IS_PRODUCTION,
  ENABLE_PERFORMANCE_MONITORING: ENV.IS_PRODUCTION,
} as const;
