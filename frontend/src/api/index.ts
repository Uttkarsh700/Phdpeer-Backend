/**
 * API Module Index
 * 
 * Central export point for all API-related modules.
 * 
 * IMPORTANT: All backend API calls MUST use apiClient from this module.
 */

export { ENDPOINTS, getEndpointUrl } from './endpoints';
export { apiClient, api, ApiClient, ApiClientError } from './client';
export type { ApiRequestOptions, ApiResponse } from './client';
