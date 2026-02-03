/**
 * Centralized API Client Wrapper
 * 
 * This is the SINGLE POINT OF ENTRY for all backend API calls.
 * All services MUST use this client - no direct fetch/axios calls allowed.
 * 
 * Features:
 * - Typed request and response helpers
 * - Standard error handling
 * - Idempotency header support
 * - No domain logic (pure API client)
 */

import axios, {
  AxiosInstance,
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';
import { env, features } from '@/config/env';
import type { ApiError } from '@/types/api';

/**
 * Request configuration options
 */
export interface ApiRequestOptions extends Omit<AxiosRequestConfig, 'headers'> {
  /**
   * Idempotency key for ensuring request idempotency
   * When provided, adds 'Idempotency-Key' header to the request
   */
  idempotencyKey?: string;
  
  /**
   * Custom headers to merge with default headers
   */
  headers?: Record<string, string>;
  
  /**
   * Skip authentication token (for public endpoints)
   */
  skipAuth?: boolean;
  
  /**
   * Retry configuration
   */
  retry?: {
    attempts: number;
    delay: number;
  };
}

/**
 * Typed API response
 */
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

/**
 * Enhanced API Error with additional context
 */
export class ApiClientError extends Error {
  public readonly code: string;
  public readonly status?: number;
  public readonly details?: any;
  public readonly originalError?: AxiosError;
  public readonly isNetworkError: boolean;
  public readonly isTimeoutError: boolean;
  public readonly isServerError: boolean;
  public readonly isClientError: boolean;

  constructor(error: AxiosError | Error, message?: string) {
    const apiError = error instanceof AxiosError 
      ? transformAxiosError(error)
      : { message: error.message, code: 'UNKNOWN_ERROR', status: undefined, details: undefined };

    super(message || apiError.message);
    this.name = 'ApiClientError';
    this.code = apiError.code || 'UNKNOWN_ERROR';
    this.status = error instanceof AxiosError && error.response ? error.response.status : undefined;
    this.details = apiError.details;
    
    if (error instanceof AxiosError) {
      this.originalError = error;
      this.isNetworkError = !error.response && !!error.request;
      this.isTimeoutError = error.code === 'ECONNABORTED' || error.message.includes('timeout');
      this.isServerError = error.response ? error.response.status >= 500 : false;
      this.isClientError = error.response ? error.response.status >= 400 && error.response.status < 500 : false;
    } else {
      this.isNetworkError = false;
      this.isTimeoutError = false;
      this.isServerError = false;
      this.isClientError = false;
    }

    // Maintain stack trace (V8-specific, not available in all environments)
    if (typeof (Error as any).captureStackTrace === 'function') {
      (Error as any).captureStackTrace(this, ApiClientError);
    }
  }
}

/**
 * Transform Axios error to standardized format
 */
function transformAxiosError(error: AxiosError): ApiError {
  if (error.response) {
    // Server responded with error status
    const data = error.response.data as any;
    const status = error.response.status;
    
    return {
      message: extractErrorMessage(data, status),
      code: String(status),
      details: data,
    };
  } else if (error.request) {
    // Request made but no response received
    if (error.code === 'ECONNABORTED') {
      return {
        message: 'Request timed out. Please try again.',
        code: 'TIMEOUT_ERROR',
        details: error.request,
      };
    }
    
    return {
      message: 'No response from server. Please check your connection.',
      code: 'NETWORK_ERROR',
      details: error.request,
    };
  } else {
    // Error in request setup
    return {
      message: error.message || 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR',
      details: error,
    };
  }
}

/**
 * Extract error message from response data
 */
function extractErrorMessage(data: any, status: number): string {
  // FastAPI format
  if (data?.detail) {
    if (typeof data.detail === 'string') {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: any) => d.msg || d).join(', ');
    }
  }
  
  // Standard format
  if (data?.message) {
    return data.message;
  }
  
  // Validation errors
  if (data?.errors && Array.isArray(data.errors)) {
    return data.errors.join(', ');
  }
  
  // Default messages by status
  const defaultMessages: Record<number, string> = {
    400: 'Bad request. Please check your input.',
    401: 'Authentication required. Please log in.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    409: 'A conflict occurred. The resource may have been modified.',
    422: 'Validation failed. Please check your input.',
    429: 'Too many requests. Please try again later.',
    500: 'An internal server error occurred.',
    502: 'Bad gateway. The server is temporarily unavailable.',
    503: 'Service unavailable. Please try again later.',
  };
  
  return defaultMessages[status] || 'An error occurred';
}

/**
 * Generate idempotency key (UUID v4)
 */
function generateIdempotencyKey(): string {
  // Simple UUID v4 generator (for browser compatibility)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Create configured Axios instance
 */
const axiosInstance: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: env.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor
 * - Adds authentication token
 * - Adds idempotency key if provided
 * - Logs requests in development
 */
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add authentication token (unless skipped)
    if (!(config as any).skipAuth) {
      const token = localStorage.getItem('auth_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    // Add idempotency key if provided
    const idempotencyKey = (config as any).idempotencyKey;
    if (idempotencyKey && config.headers) {
      config.headers['Idempotency-Key'] = idempotencyKey;
    }

    // Merge custom headers
    const customHeaders = (config as any).headers;
    if (customHeaders && config.headers) {
      Object.assign(config.headers, customHeaders);
    }

    // Log requests in development
    if (env.isDevelopment && features.enableDebug) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        idempotencyKey,
      });
    }

    return config;
  },
  (error) => {
    return Promise.reject(new ApiClientError(error));
  }
);

/**
 * Response interceptor
 * - Transforms errors to ApiClientError
 * - Logs responses in development
 */
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log responses in development
    if (env.isDevelopment && features.enableDebug) {
      console.log(`[API] Response:`, {
        status: response.status,
        url: response.config.url,
        data: response.data,
      });
    }

    return response;
  },
  (error: AxiosError) => {
    const apiError = new ApiClientError(error);
    
    // Log errors in development
    if (env.isDevelopment && features.enableDebug) {
      console.error('[API] Error:', {
        code: apiError.code,
        status: apiError.status,
        message: apiError.message,
        details: apiError.details,
      });
    }

    return Promise.reject(apiError);
  }
);

/**
 * Centralized API Client
 * 
 * All backend API calls MUST go through this client.
 * No direct fetch/axios calls should exist in the codebase.
 */
export class ApiClient {
  /**
   * GET request
   */
  async get<T = any>(
    url: string,
    params?: Record<string, any>,
    options?: ApiRequestOptions
  ): Promise<T> {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.ts:298',message:'ApiClient.get called',data:{url,params,hasParams:!!params},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    const config: AxiosRequestConfig = {
      method: 'GET',
      url,
      params,
      ...options,
    };

    try {
      const response = await axiosInstance.request<T>(config);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.ts:312',message:'API request successful',data:{status:response.status,url,hasData:!!response.data,dataKeys:Object.keys(response.data||{})},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'ALL'})}).catch(()=>{});
      // #endregion
      return response.data;
    } catch (error) {
      // #region agent log
      const isAxiosError = error instanceof AxiosError;
      const errorObj = error as any;
      fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.ts:314',message:'API request failed',data:{errorType:errorObj?.constructor?.name,isAxiosError,status:isAxiosError ? errorObj.response?.status : undefined,errorMessage:errorObj?.message || String(error)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'ALL'})}).catch(()=>{});
      // #endregion
      throw error instanceof ApiClientError ? error : new ApiClientError(error as Error);
    }
  }

  /**
   * POST request
   */
  async post<T = any>(
    url: string,
    data?: any,
    options?: ApiRequestOptions
  ): Promise<T> {
    // Auto-generate idempotency key if not provided for POST requests
    const idempotencyKey = options?.idempotencyKey || generateIdempotencyKey();

    const config: AxiosRequestConfig = {
      method: 'POST',
      url,
      data,
      idempotencyKey,
      ...options,
    };

    try {
      const response = await axiosInstance.request<T>(config);
      return response.data;
    } catch (error) {
      throw error instanceof ApiClientError ? error : new ApiClientError(error as Error);
    }
  }

  /**
   * PUT request
   */
  async put<T = any>(
    url: string,
    data?: any,
    options?: ApiRequestOptions
  ): Promise<T> {
    const config: AxiosRequestConfig = {
      method: 'PUT',
      url,
      data,
      ...options,
    };

    try {
      const response = await axiosInstance.request<T>(config);
      return response.data;
    } catch (error) {
      throw error instanceof ApiClientError ? error : new ApiClientError(error as Error);
    }
  }

  /**
   * PATCH request
   */
  async patch<T = any>(
    url: string,
    data?: any,
    options?: ApiRequestOptions
  ): Promise<T> {
    const config: AxiosRequestConfig = {
      method: 'PATCH',
      url,
      data,
      ...options,
    };

    try {
      const response = await axiosInstance.request<T>(config);
      return response.data;
    } catch (error) {
      throw error instanceof ApiClientError ? error : new ApiClientError(error as Error);
    }
  }

  /**
   * DELETE request
   */
  async delete<T = any>(
    url: string,
    options?: ApiRequestOptions
  ): Promise<T> {
    const config: AxiosRequestConfig = {
      method: 'DELETE',
      url,
      ...options,
    };

    try {
      const response = await axiosInstance.request<T>(config);
      return response.data;
    } catch (error) {
      throw error instanceof ApiClientError ? error : new ApiClientError(error as Error);
    }
  }

  /**
   * Upload file
   */
  async upload<T = any>(
    url: string,
    file: File,
    options?: ApiRequestOptions & {
      onProgress?: (progress: number) => void;
      fieldName?: string;
    }
  ): Promise<T> {
    const formData = new FormData();
    formData.append(options?.fieldName || 'file', file);

    const config: AxiosRequestConfig = {
      method: 'POST',
      url,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...options?.headers,
      },
      onUploadProgress: (progressEvent) => {
        if (options?.onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          options.onProgress(progress);
        }
      },
      ...options,
    };

    try {
      const response = await axiosInstance.request<T>(config);
      return response.data;
    } catch (error) {
      throw error instanceof ApiClientError ? error : new ApiClientError(error as Error);
    }
  }

  /**
   * Raw request (for advanced use cases)
   * Use with caution - prefer typed methods above
   */
  async request<T = any>(config: AxiosRequestConfig & ApiRequestOptions): Promise<ApiResponse<T>> {
    try {
      const response = await axiosInstance.request<T>(config);
      return {
        data: response.data,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers as Record<string, string>,
      };
    } catch (error) {
      throw error instanceof ApiClientError ? error : new ApiClientError(error as Error);
    }
  }
}

/**
 * Default API client instance
 * 
 * This is the SINGLE INSTANCE that all services should use.
 * Import this, not the class.
 */
export const apiClient = new ApiClient();

/**
 * Legacy compatibility: Export as 'api' for backward compatibility
 * @deprecated Use 'apiClient' instead
 */
export const api = apiClient;

// ApiClientError is already exported above with 'export class ApiClientError'
// No need for duplicate export statement

export default apiClient;
