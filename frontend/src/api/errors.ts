/**
 * API Error Handling
 * 
 * Standardized error classes for API client
 */

import type { ErrorResponse } from './types';

/**
 * Base API Error class
 */
export class ApiError extends Error {
  /** HTTP status code */
  status: number;
  /** Error code from backend */
  code?: string;
  /** Detailed error information */
  detail?: string | Record<string, unknown>;
  /** Field-specific validation errors */
  errors?: Record<string, string[]>;
  /** Original error response */
  response?: ErrorResponse;

  constructor(
    message: string,
    status: number = 500,
    response?: ErrorResponse
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = response?.code;
    this.detail = response?.detail;
    this.errors = response?.errors;
    this.response = response;

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    // Type assertion needed because captureStackTrace is not in standard TypeScript Error type
    if ((Error as any).captureStackTrace) {
      (Error as any).captureStackTrace(this, ApiError);
    }
  }
}

/**
 * Network Error - connection issues, timeouts, etc.
 */
export class NetworkError extends ApiError {
  constructor(message: string = 'Network error occurred') {
    super(message, 0);
    this.name = 'NetworkError';
  }
}

/**
 * Timeout Error - request exceeded timeout
 */
export class TimeoutError extends ApiError {
  constructor(message: string = 'Request timeout') {
    super(message, 408);
    this.name = 'TimeoutError';
  }
}

/**
 * Client Error - 4xx status codes
 */
export class ClientError extends ApiError {
  constructor(
    message: string,
    status: number,
    response?: ErrorResponse
  ) {
    super(message, status, response);
    this.name = 'ClientError';
  }
}

/**
 * Server Error - 5xx status codes
 */
export class ServerError extends ApiError {
  constructor(
    message: string,
    status: number,
    response?: ErrorResponse
  ) {
    super(message, status, response);
    this.name = 'ServerError';
  }
}

/**
 * Validation Error - 422 or field-specific errors
 */
export class ValidationError extends ClientError {
  constructor(
    message: string,
    errors?: Record<string, string[]>,
    response?: ErrorResponse
  ) {
    super(message, 422, response);
    this.name = 'ValidationError';
    this.errors = errors;
  }
}

/**
 * Unauthorized Error - 401
 */
export class UnauthorizedError extends ClientError {
  constructor(message: string = 'Unauthorized') {
    super(message, 401);
    this.name = 'UnauthorizedError';
  }
}

/**
 * Forbidden Error - 403
 */
export class ForbiddenError extends ClientError {
  constructor(message: string = 'Forbidden') {
    super(message, 403);
    this.name = 'ForbiddenError';
  }
}

/**
 * Not Found Error - 404
 */
export class NotFoundError extends ClientError {
  constructor(message: string = 'Resource not found') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

/**
 * Create appropriate error instance based on status code
 */
export function createApiError(
  message: string,
  status: number,
  response?: ErrorResponse
): ApiError {
  if (status === 0) {
    return new NetworkError(message);
  }

  if (status === 401) {
    return new UnauthorizedError(response?.message || message);
  }

  if (status === 403) {
    return new ForbiddenError(response?.message || message);
  }

  if (status === 404) {
    return new NotFoundError(response?.message || message);
  }

  if (status === 408) {
    return new TimeoutError(response?.message || message);
  }

  if (status === 422) {
    return new ValidationError(
      response?.message || message,
      response?.errors,
      response
    );
  }

  if (status >= 400 && status < 500) {
    return new ClientError(
      response?.message || message,
      status,
      response
    );
  }

  if (status >= 500) {
    return new ServerError(
      response?.message || message,
      status,
      response
    );
  }

  return new ApiError(message, status, response);
}
