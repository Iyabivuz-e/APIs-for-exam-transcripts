/**
 * API Utilities
 * 
 * Professional error handling and response processing
 * Senior pattern: Centralized API utilities with type safety
 */

import { ApiError } from '../services/api';
import { HTTP_STATUS, ERROR_MESSAGES } from '../config/constants';

// Result type for better error handling
export type Result<T, E = ApiError> = 
  | { success: true; data: T }
  | { success: false; error: E };

// Wrap async operations for better error handling
export async function wrapAsync<T>(
  operation: () => Promise<T>
): Promise<Result<T>> {
  try {
    const data = await operation();
    return { success: true, data };
  } catch (error) {
    const apiError = error instanceof ApiError 
      ? error 
      : new ApiError(HTTP_STATUS.INTERNAL_SERVER_ERROR, ERROR_MESSAGES.GENERIC);
    
    return { success: false, error: apiError };
  }
}

// Format API errors for user display
export function formatApiError(error: ApiError): string {
  switch (error.status) {
    case HTTP_STATUS.BAD_REQUEST:
      return error.message || ERROR_MESSAGES.VALIDATION;
    case HTTP_STATUS.UNAUTHORIZED:
      return ERROR_MESSAGES.UNAUTHORIZED;
    case HTTP_STATUS.FORBIDDEN:
      return ERROR_MESSAGES.FORBIDDEN;
    case HTTP_STATUS.NOT_FOUND:
      return ERROR_MESSAGES.NOT_FOUND;
    case HTTP_STATUS.CONFLICT:
      return error.message || 'A conflict occurred. Please try again.';
    case HTTP_STATUS.UNPROCESSABLE_ENTITY:
      return error.message || ERROR_MESSAGES.VALIDATION;
    case HTTP_STATUS.INTERNAL_SERVER_ERROR:
    default:
      return ERROR_MESSAGES.GENERIC;
  }
}

// Check if error is a network error
export function isNetworkError(error: unknown): boolean {
  return (
    error instanceof TypeError ||
    (error instanceof ApiError && error.status === 0) ||
    (typeof error === 'object' && error !== null && 'code' in error && error.code === 'NETWORK_ERROR')
  );
}

// Retry mechanism for failed API calls
export async function retryOperation<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000,
  shouldRetry: (error: unknown) => boolean = isNetworkError
): Promise<T> {
  let lastError: unknown;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      
      // Don't retry if it's not a retryable error or if it's the last attempt
      if (!shouldRetry(error) || attempt === maxRetries) {
        throw error;
      }
      
      // Wait before retrying (exponential backoff)
      const waitTime = delay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
  
  throw lastError;
}

// Debounce function for search inputs
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

// Throttle function for scroll events, etc.
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
}

// Safe JSON parsing
export function safeJsonParse<T>(
  json: string,
  defaultValue: T
): T {
  try {
    return JSON.parse(json);
  } catch {
    return defaultValue;
  }
}

// Format file size for display
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Validate file type and size
export function validateFile(
  file: File,
  allowedTypes: string[],
  maxSize: number
): { valid: boolean; error?: string } {
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `File type not allowed. Allowed types: ${allowedTypes.join(', ')}`
    };
  }
  
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `File too large. Maximum size: ${formatFileSize(maxSize)}`
    };
  }
  
  return { valid: true };
}

// Generate unique ID (simple version)
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Copy text to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textArea);
      return success;
    }
  } catch {
    return false;
  }
}
