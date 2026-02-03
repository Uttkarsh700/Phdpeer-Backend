/**
 * Baseline Service
 * 
 * Handles baseline creation and management API calls.
 * 
 * IMPORTANT: All API calls go through @/api/client (apiClient)
 */

import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import type { Baseline, CreateBaselineRequest } from '@/types/api';

export const baselineService = {
  /**
   * Create a baseline
   */
  create: async (data: CreateBaselineRequest): Promise<{ baselineId: string }> => {
    return apiClient.post<{ baselineId: string }>(ENDPOINTS.BASELINES.CREATE, data);
  },

  /**
   * Get baseline by ID
   */
  getById: async (baselineId: string): Promise<Baseline> => {
    return apiClient.get<Baseline>(ENDPOINTS.BASELINES.GET_BY_ID(baselineId));
  },

  /**
   * Get user's baselines
   */
  getUserBaselines: async (skip?: number, limit?: number): Promise<Baseline[]> => {
    return apiClient.get<Baseline[]>(ENDPOINTS.BASELINES.LIST, { skip, limit });
  },

  /**
   * Get baseline with document information
   */
  getWithDocument: async (baselineId: string): Promise<{
    baseline: Baseline;
    document: any;
  }> => {
    return apiClient.get(`${ENDPOINTS.BASELINES.GET_BY_ID(baselineId)}/with-document`);
  },

  /**
   * Delete baseline
   */
  delete: async (baselineId: string): Promise<void> => {
    return apiClient.delete<void>(ENDPOINTS.BASELINES.DELETE(baselineId));
  },
};

export default baselineService;
