/**
 * API Client Type Definitions
 * 
 * Type-safe definitions for API requests and responses
 */

/**
 * HTTP Method types
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

/**
 * Request configuration options
 */
export interface RequestConfig {
  /** Request headers */
  headers?: Record<string, string>;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Whether to include credentials (cookies) */
  credentials?: RequestCredentials;
  /** Request signal for cancellation */
  signal?: AbortSignal;
}

/**
 * API Request options extending RequestConfig
 */
export interface ApiRequestOptions<TBody = unknown> extends RequestConfig {
  /** Request body (for POST, PUT, PATCH) */
  body?: TBody;
  /** Query parameters (for GET, DELETE) */
  params?: Record<string, string | number | boolean | null | undefined>;
}

/**
 * Standard API Response wrapper
 */
export interface ApiResponse<TData = unknown> {
  /** Response data */
  data: TData;
  /** Response status code */
  status: number;
  /** Response status text */
  statusText: string;
  /** Response headers */
  headers: Headers;
}

/**
 * Paginated response structure
 */
export interface PaginatedResponse<TItem = unknown> {
  items: TItem[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * Error response structure from backend
 */
export interface ErrorResponse {
  /** Error message */
  message: string;
  /** Error code */
  code?: string;
  /** Detailed error information */
  detail?: string | Record<string, unknown>;
  /** Field-specific validation errors */
  errors?: Record<string, string[]>;
  /** HTTP status code */
  status?: number;
}
