/**
 * Progress Service
 * 
 * Handles progress tracking and milestone completion API calls.
 */

import { api } from './api.client';
import type { ProgressEvent } from '@/types/api';

export const progressService = {
  /**
   * Mark milestone as completed
   */
  completeMilestone: async (
    milestoneId: string,
    completionDate?: string,
    notes?: string
  ): Promise<{ eventId: string }> => {
    return api.post(`/api/v1/progress/milestones/${milestoneId}/complete`, {
      completionDate,
      notes,
    });
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
    return api.post('/api/v1/progress/events', data);
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
    return api.get(`/api/v1/progress/milestones/${milestoneId}/delay`);
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
    return api.get(`/api/v1/progress/stages/${stageId}`);
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
    return api.get(`/api/v1/progress/timelines/${committedTimelineId}`);
  },

  /**
   * Get user's progress events
   */
  getUserEvents: async (
    milestoneId?: string,
    eventType?: string,
    limit?: number
  ): Promise<ProgressEvent[]> => {
    return api.get('/api/v1/progress/events', { milestoneId, eventType, limit });
  },
};

export default progressService;
