/**
 * Assessment Service
 * 
 * Handles journey health assessment API calls.
 */

import { api } from './api.client';
import type {
  JourneyAssessment,
  AssessmentSummary,
  SubmitQuestionnaireRequest,
} from '@/types/api';

export const assessmentService = {
  /**
   * Submit questionnaire and get assessment
   */
  submitQuestionnaire: async (
    data: SubmitQuestionnaireRequest
  ): Promise<AssessmentSummary> => {
    return api.post('/api/v1/assessments/submit', data);
  },

  /**
   * Get assessment by ID
   */
  getById: async (assessmentId: string): Promise<JourneyAssessment> => {
    return api.get(`/api/v1/assessments/${assessmentId}`);
  },

  /**
   * Get latest assessment
   */
  getLatest: async (): Promise<JourneyAssessment | null> => {
    return api.get('/api/v1/assessments/latest');
  },

  /**
   * Get assessment history
   */
  getHistory: async (
    assessmentType?: string,
    limit?: number
  ): Promise<JourneyAssessment[]> => {
    return api.get('/api/v1/assessments/history', { assessmentType, limit });
  },

  /**
   * Compare two assessments
   */
  compare: async (
    assessmentId1: string,
    assessmentId2: string
  ): Promise<{
    assessment1Id: string;
    assessment1Date: string;
    assessment1Score: number;
    assessment2Id: string;
    assessment2Date: string;
    assessment2Score: number;
    change: number;
    improvement: boolean;
    percentageChange: number;
  }> => {
    return api.get('/api/v1/assessments/compare', {
      assessmentId1,
      assessmentId2,
    });
  },
};

export default assessmentService;
