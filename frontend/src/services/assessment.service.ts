/**
 * Assessment Service
 * 
 * Handles journey health assessment API calls.
 * 
 * IMPORTANT: 
 * - All endpoints are defined in @/api/endpoints.ts
 * - All API calls go through @/api/client (apiClient)
 * - Never hardcode API paths or use direct fetch/axios calls
 */

import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import type {
  JourneyAssessment,
  AssessmentSummary,
  SubmitQuestionnaireRequest,
} from '@/types/api';

export const assessmentService = {
  /**
   * Save questionnaire draft
   * 
   * Calls POST /doctor/save-draft
   * Auto-saves responses without submitting.
   */
  saveDraft: async (data: {
    responses: Array<{
      dimension: string;
      question_id: string;
      response_value: number;
      question_text?: string;
    }>;
    notes?: string;
  }): Promise<{ draftId: string }> => {
    return apiClient.post<{ draftId: string; draft_id?: string }>(
      ENDPOINTS.DOCTOR.SAVE_DRAFT,
      data
    ).then(response => ({
      draftId: response.draftId || response.draft_id || '',
    }));
  },

  /**
   * Submit questionnaire and get assessment
   * 
   * Calls POST /doctor/submit
   * Returns JourneyAssessment summary.
   */
  submitQuestionnaire: async (
    data: SubmitQuestionnaireRequest & { draftId?: string }
  ): Promise<AssessmentSummary> => {
    // Backend expects draft_id if provided
    const payload: any = {
      responses: data.responses.map(r => ({
        dimension: r.dimension,
        question_id: r.questionId,
        response_value: r.responseValue,
        question_text: r.questionText,
      })),
      assessment_type: data.assessmentType || 'self_assessment',
      ...(data.notes && { notes: data.notes }),
      ...(data.draftId && { draft_id: data.draftId }),
    };
    
    return apiClient.post<AssessmentSummary>(ENDPOINTS.DOCTOR.SUBMIT, payload);
  },

  /**
   * Get assessment by ID
   */
  getById: async (assessmentId: string): Promise<JourneyAssessment> => {
    return apiClient.get<JourneyAssessment>(ENDPOINTS.ASSESSMENTS.GET_BY_ID(assessmentId));
  },

  /**
   * Get latest assessment
   */
  getLatest: async (): Promise<JourneyAssessment | null> => {
    return apiClient.get<JourneyAssessment | null>(ENDPOINTS.ASSESSMENTS.GET_LATEST);
  },

  /**
   * Get assessment history
   */
  getHistory: async (
    assessmentType?: string,
    limit?: number
  ): Promise<JourneyAssessment[]> => {
    return apiClient.get<JourneyAssessment[]>(ENDPOINTS.ASSESSMENTS.GET_HISTORY, {
      assessmentType,
      limit,
    });
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
    return apiClient.get(ENDPOINTS.ASSESSMENTS.COMPARE, {
      assessmentId1,
      assessmentId2,
    });
  },
};

export default assessmentService;
