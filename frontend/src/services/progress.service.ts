/**
 * Progress Service
 * 
 * Handles progress tracking and milestone completion API calls.
 * 
 * IMPORTANT: All API calls go through @/api/client (apiClient)
 */

import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import type { ProgressEvent } from '@/types/api';

export const progressService = {
  /**
   * Mark milestone as completed
   * 
   * Calls POST /progress/complete (or POST /progress/milestones/:id/complete)
   * Frontend does not calculate delays - backend provides all delay indicators.
   */
  completeMilestone: async (
    milestoneId: string,
    completionDate?: string,
    notes?: string
  ): Promise<{ eventId: string }> => {
    // Backend expects completion_date and notes
    return apiClient.post<{ eventId: string; event_id?: string }>(
      `${ENDPOINTS.PROGRESS.BASE}/milestones/${milestoneId}/complete`,
      { 
        completion_date: completionDate, 
        notes 
      }
    ).then(response => ({
      eventId: response.eventId || response.event_id || '',
    }));
  },

  /**
   * Log progress event
   */
  logEvent: async (data: {
    eventType: string;
    title: string;
    description: string;
    eventDate?: string;
    milestoneId?: string;
    impactLevel?: string;
    tags?: string;
    notes?: string;
  }): Promise<{ eventId: string }> => {
    return apiClient.post<{ eventId: string }>(`${ENDPOINTS.PROGRESS.BASE}/events`, data);
  },

  /**
   * Get milestone delay information
   */
  getMilestoneDelay: async (milestoneId: string): Promise<{
    milestoneId: string;
    milestoneTitle: string;
    isCompleted: boolean;
    isCritical: boolean;
    targetDate?: string;
    actualCompletionDate?: string;
    comparisonDate: string;
    delayDays: number;
    status: string;
    hasTargetDate: boolean;
  }> => {
    return apiClient.get(`${ENDPOINTS.PROGRESS.BASE}/milestones/${milestoneId}/delay`);
  },

  /**
   * Get stage progress
   */
  getStageProgress: async (stageId: string): Promise<{
    stageId: string;
    stageTitle: string;
    stageOrder: number;
    totalMilestones: number;
    completedMilestones: number;
    pendingMilestones: number;
    completionPercentage: number;
    overdueMilestones: number;
    averageDelayDays: number;
    hasMilestones: boolean;
  }> => {
    return apiClient.get(`${ENDPOINTS.PROGRESS.BASE}/stages/${stageId}`);
  },

  /**
   * Get timeline progress
   */
  getTimelineProgress: async (committedTimelineId: string): Promise<{
    timelineId: string;
    timelineTitle: string;
    committedDate: string;
    targetCompletionDate?: string;
    durationProgressPercentage?: number;
    totalStages: number;
    completedStages: number;
    totalMilestones: number;
    completedMilestones: number;
    pendingMilestones: number;
    completionPercentage: number;
    criticalMilestones: number;
    completedCriticalMilestones: number;
    overdueMilestones: number;
    overdueCriticalMilestones: number;
    averageDelayDays: number;
    maxDelayDays: number;
    hasData: boolean;
  }> => {
    return apiClient.get(ENDPOINTS.PROGRESS.GET_BY_TIMELINE(committedTimelineId));
  },

  /**
   * Get user's progress events
   */
  getUserEvents: async (
    milestoneId?: string,
    eventType?: string,
    limit?: number
  ): Promise<ProgressEvent[]> => {
    return apiClient.get<ProgressEvent[]>(`${ENDPOINTS.PROGRESS.BASE}/events`, {
      milestoneId,
      eventType,
      limit,
    });
  },
};

export default progressService;
