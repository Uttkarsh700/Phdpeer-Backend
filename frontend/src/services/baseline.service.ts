/**
 * Baseline Service
 * 
 * Handles baseline creation and management API calls.
 */

import { api } from './api.client';
import type { Baseline, CreateBaselineRequest } from '@/types/api';

export const baselineService = {
  /**
   * Create a baseline
   */
  create: async (data: CreateBaselineRequest): Promise<{ baselineId: string }> => {
    return api.post('/api/v1/baselines', data);
  },

  /**
   * Get baseline by ID
   */
  getById: async (baselineId: string): Promise<Baseline> => {
    return api.get(`/api/v1/baselines/${baselineId}`);
  },

  /**
   * Get user's baselines
   */
  getUserBaselines: async (skip?: number, limit?: number): Promise<Baseline[]> => {
    return api.get('/api/v1/baselines', { skip, limit });
  },

  /**
   * Get baseline with document information
   */
  getWithDocument: async (baselineId: string): Promise<{
    baseline: Baseline;
    document: any;
  }> => {
    return api.get(`/api/v1/baselines/${baselineId}/with-document`);
  },

  /**
   * Delete baseline
   */
  delete: async (baselineId: string): Promise<void> => {
    return api.delete(`/api/v1/baselines/${baselineId}`);
  },
};

export default baselineService;
