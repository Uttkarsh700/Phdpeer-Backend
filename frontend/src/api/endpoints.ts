/**
 * API Endpoints Configuration
 * 
 * Centralized endpoint definitions. All API endpoints should be defined here.
 * This ensures no hardcoded URLs exist in service files.
 * 
 * Usage:
 * ```ts
 * import { ENDPOINTS } from '@/api/endpoints';
 * 
 * const response = await api.get(ENDPOINTS.ASSESSMENTS.GET_LATEST);
 * ```
 */

import { env } from '@/config/env';

/**
 * Helper function to build endpoint paths
 * Ensures consistent path formatting
 */
function endpoint(...parts: string[]): string {
  return parts
    .map(part => part.replace(/^\/|\/$/g, '')) // Remove leading/trailing slashes
    .filter(part => part.length > 0)
    .join('/');
}

/**
 * API Endpoints
 * 
 * All endpoints are relative paths. The base URL is configured in env.ts
 * and applied automatically by the API client.
 */
export const ENDPOINTS = {
  // Assessment endpoints
  ASSESSMENTS: {
    BASE: endpoint('assessments'),
    SUBMIT: endpoint('assessments', 'submit'),
    GET_BY_ID: (id: string) => endpoint('assessments', id),
    GET_LATEST: endpoint('assessments', 'latest'),
    GET_HISTORY: endpoint('assessments', 'history'),
    COMPARE: endpoint('assessments', 'compare'),
  },

  // PhD Doctor endpoints
  DOCTOR: {
    BASE: endpoint('doctor'),
    SAVE_DRAFT: endpoint('doctor', 'save-draft'),
    SUBMIT: endpoint('doctor', 'submit'),
  },

  // Analytics endpoints
  ANALYTICS: {
    BASE: endpoint('analytics'),
    SUMMARY: endpoint('analytics', 'summary'),
  },

  // Document endpoints
  DOCUMENTS: {
    BASE: endpoint('documents'),
    UPLOAD: endpoint('documents', 'upload'),
    GET_BY_ID: (id: string) => endpoint('documents', id),
    LIST: endpoint('documents'),
    DELETE: (id: string) => endpoint('documents', id),
  },

  // Baseline endpoints
  BASELINES: {
    BASE: endpoint('baselines'),
    CREATE: endpoint('baselines'),
    GET_BY_ID: (id: string) => endpoint('baselines', id),
    LIST: endpoint('baselines'),
    UPDATE: (id: string) => endpoint('baselines', id),
    DELETE: (id: string) => endpoint('baselines', id),
  },

  // Timeline endpoints
  TIMELINES: {
    BASE: endpoint('timelines'),
    DRAFT: endpoint('timelines', 'draft'),
    GET_DRAFT: (id: string) => endpoint('timelines', 'draft', id),
    COMMIT: (id: string) => endpoint('timelines', 'draft', id, 'commit'),
    GET_COMMITTED: (id: string) => endpoint('timelines', 'committed', id),
    LIST: endpoint('timelines'),
  },

  // Progress endpoints
  PROGRESS: {
    BASE: endpoint('progress'),
    GET_BY_TIMELINE: (timelineId: string) => endpoint('progress', 'timeline', timelineId),
    COMPLETE: endpoint('progress', 'complete'),
    MILESTONE_COMPLETE: (milestoneId: string) => endpoint('progress', 'milestones', milestoneId, 'complete'),
    UPDATE: endpoint('progress'),
  },

  // Health check endpoint
  HEALTH: {
    CHECK: endpoint('health'),
  },
} as const;

/**
 * Get full URL for an endpoint (useful for debugging or external tools)
 * 
 * @param path - Endpoint path from ENDPOINTS
 * @returns Full URL including base URL
 * 
 * @example
 * ```ts
 * const url = getEndpointUrl(ENDPOINTS.ASSESSMENTS.GET_LATEST);
 * // Returns: 'http://localhost:8000/api/v1/assessments/latest'
 * ```
 */
export function getEndpointUrl(path: string): string {
  const baseUrl = env.apiBaseUrl.endsWith('/') 
    ? env.apiBaseUrl.slice(0, -1) 
    : env.apiBaseUrl;
  
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}/api/${env.apiVersion}${cleanPath}`;
}
