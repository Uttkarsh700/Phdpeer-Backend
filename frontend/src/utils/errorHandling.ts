/**
 * Error Handling Utilities
 * 
 * Centralized error handling and user-friendly error messages.
 */

import type { ApiError } from '@/types/api';

// Error message mapping
const ERROR_MESSAGES: Record<string, string> = {
  // Network errors
  NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  
  // Authentication errors
  '401': 'You are not authenticated. Please log in.',
  '403': 'You do not have permission to perform this action.',
  
  // Not found errors
  '404': 'The requested resource was not found.',
  
  // Validation errors
  '400': 'Invalid request. Please check your input.',
  '422': 'Validation failed. Please check your input.',
  
  // Server errors
  '500': 'An internal server error occurred. Please try again later.',
  '502': 'The server is temporarily unavailable. Please try again later.',
  '503': 'The service is temporarily unavailable. Please try again later.',
  
  // Business logic errors
  DUPLICATE_BASELINE: 'A baseline already exists for this document.',
  TIMELINE_ALREADY_COMMITTED: 'This timeline has already been committed.',
  MILESTONE_ALREADY_COMPLETED: 'This milestone is already marked as completed.',
  ASSESSMENT_TOO_SOON: 'You recently completed an assessment. Please wait before taking another.',
  INVALID_DATE_RANGE: 'Invalid date range. End date must be after start date.',
  EMPTY_TIMELINE: 'Cannot commit an empty timeline. Add stages and milestones first.',
  MISSING_BASELINE: 'Baseline not found. Please create a baseline first.',
};

// Get user-friendly error message
export const getErrorMessage = (error: any): string => {
  // Handle ApiError type
  if (error && typeof error === 'object') {
    // Check for custom error code
    if (error.code && ERROR_MESSAGES[error.code]) {
      return ERROR_MESSAGES[error.code];
    }
    
    // Check for HTTP status code
    if (error.status && ERROR_MESSAGES[error.status]) {
      return ERROR_MESSAGES[error.status];
    }
    
    // Return error message if available
    if (error.message) {
      return error.message;
    }
    
    // Check for detail field (FastAPI format)
    if (error.detail) {
      if (typeof error.detail === 'string') {
        return error.detail;
      }
      if (Array.isArray(error.detail)) {
        return error.detail.map((d: any) => d.msg || d).join(', ');
      }
    }
  }
  
  // Handle string errors
  if (typeof error === 'string') {
    return error;
  }
  
  // Default error message
  return 'An unexpected error occurred. Please try again.';
};

// Error type detection
export const isNetworkError = (error: any): boolean => {
  return error?.code === 'NETWORK_ERROR' || error?.message?.includes('network');
};

export const isAuthError = (error: any): boolean => {
  const code = error?.code || error?.status;
  return code === '401' || code === '403' || code === 401 || code === 403;
};

export const isValidationError = (error: any): boolean => {
  const code = error?.code || error?.status;
  return code === '400' || code === '422' || code === 400 || code === 422;
};

export const isNotFoundError = (error: any): boolean => {
  const code = error?.code || error?.status;
  return code === '404' || code === 404;
};

export const isServerError = (error: any): boolean => {
  const code = error?.code || error?.status;
  return code === '500' || code === '502' || code === '503' || 
         code === 500 || code === 502 || code === 503;
};

// Error logging (could integrate with external service)
export const logError = (error: any, context?: string): void => {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[Error${context ? ` - ${context}` : ''}]:`, error);
  }
  
  // In production, could send to error tracking service (e.g., Sentry)
  // Example: Sentry.captureException(error, { tags: { context } });
};

// Retry logic for transient errors
export const shouldRetry = (error: any, attemptNumber: number, maxAttempts: number = 3): boolean => {
  if (attemptNumber >= maxAttempts) return false;
  
  // Retry on network errors
  if (isNetworkError(error)) return true;
  
  // Retry on 5xx server errors
  if (isServerError(error)) return true;
  
  // Don't retry on client errors (4xx)
  return false;
};

// Exponential backoff delay
export const getRetryDelay = (attemptNumber: number): number => {
  return Math.min(1000 * Math.pow(2, attemptNumber), 10000); // Max 10 seconds
};

// Error boundary helper
export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: any;
}

export const createErrorBoundaryState = (): ErrorBoundaryState => ({
  hasError: false,
  error: null,
  errorInfo: null,
});

// Validation error formatter
export const formatValidationErrors = (errors: string[]): string => {
  if (errors.length === 0) return '';
  if (errors.length === 1) return errors[0];
  return errors.map((err, i) => `${i + 1}. ${err}`).join('\n');
};

// Safe error extraction for display
export const extractErrorDetails = (error: any): {
  title: string;
  message: string;
  details?: string;
} => {
  const message = getErrorMessage(error);
  
  // Determine title based on error type
  let title = 'Error';
  if (isNetworkError(error)) title = 'Connection Error';
  else if (isAuthError(error)) title = 'Authentication Error';
  else if (isValidationError(error)) title = 'Validation Error';
  else if (isNotFoundError(error)) title = 'Not Found';
  else if (isServerError(error)) title = 'Server Error';
  
  // Extract additional details if available
  const details = error?.details ? JSON.stringify(error.details, null, 2) : undefined;
  
  return { title, message, details };
};

// Rate limiting detection
export const isRateLimitError = (error: any): boolean => {
  const code = error?.code || error?.status;
  return code === '429' || code === 429 || error?.message?.includes('rate limit');
};

// Conflict detection (for duplicate operations)
export const isConflictError = (error: any): boolean => {
  const code = error?.code || error?.status;
  return code === '409' || code === 409 || 
         error?.message?.includes('already exists') ||
         error?.message?.includes('duplicate') ||
         error?.message?.includes('conflict');
};
