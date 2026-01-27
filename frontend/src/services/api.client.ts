/**
 * API Client
 * 
 * Configured Axios instance with interceptors for authentication,
 * error handling, and request/response transformation.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { env } from '@/config/env';
import type { ApiResponse, ApiError } from '@/types/api';

/**
 * Create configured axios instance
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: env.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor
 * Adds authentication token and other headers
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log requests in development
    if (env.isDevelopment) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 * Handles errors and transforms responses
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (env.isDevelopment) {
      console.log(`[API] Response:`, response.data);
    }

    return response;
  },
  (error: AxiosError) => {
    const apiError = handleApiError(error);

    // Log errors in development
    if (env.isDevelopment) {
      console.error('[API] Error:', apiError);
    }

    return Promise.reject(apiError);
  }
);

/**
 * Handle API errors and transform to consistent format
 */
function handleApiError(error: AxiosError): ApiError {
  if (error.response) {
    // Server responded with error status
    const data = error.response.data as any;
    
    return {
      message: data?.message || data?.detail || 'An error occurred',
      code: String(error.response.status),
      details: data,
    };
  } else if (error.request) {
    // Request made but no response
    return {
      message: 'No response from server. Please check your connection.',
      code: 'NETWORK_ERROR',
      details: error.request,
    };
  } else {
    // Something else happened
    return {
      message: error.message || 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR',
      details: error,
    };
  }
}

/**
 * Helper functions for common request patterns
 */

export const api = {
  /**
   * GET request
   */
  get: async <T>(url: string, params?: any): Promise<T> => {
    const response = await apiClient.get<T>(url, { params });
    return response.data;
  },

  /**
   * POST request
   */
  post: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.post<T>(url, data);
    return response.data;
  },

  /**
   * PUT request
   */
  put: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.put<T>(url, data);
    return response.data;
  },

  /**
   * PATCH request
   */
  patch: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.patch<T>(url, data);
    return response.data;
  },

  /**
   * DELETE request
   */
  delete: async <T>(url: string): Promise<T> => {
    const response = await apiClient.delete<T>(url);
    return response.data;
  },

  /**
   * Upload file
   */
  upload: async <T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },
};

export default api;
