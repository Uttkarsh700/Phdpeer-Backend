/**
 * Timeline Service
 * 
 * Handles timeline creation, commitment, and management API calls.
 */

import { api } from './api.client';
import type {
  DraftTimeline,
  CommittedTimeline,
  TimelineStage,
  TimelineMilestone,
  CreateTimelineRequest,
  CommitTimelineRequest,
} from '@/types/api';

export const timelineService = {
  /**
   * Create draft timeline from baseline
   */
  createDraft: async (data: CreateTimelineRequest): Promise<{ draftTimelineId: string }> => {
    return api.post('/api/v1/timelines/draft', data);
  },

  /**
   * Get draft timeline by ID
   */
  getDraft: async (draftTimelineId: string): Promise<DraftTimeline> => {
    return api.get(`/api/v1/timelines/draft/${draftTimelineId}`);
  },

  /**
   * Get draft timeline with stages and milestones
   */
  getDraftWithDetails: async (draftTimelineId: string): Promise<{
    timeline: DraftTimeline;
    baseline: any;
    stages: Array<{
      stage: TimelineStage;
      milestones: TimelineMilestone[];
    }>;
    totalStages: number;
    totalMilestones: number;
  }> => {
    return api.get(`/api/v1/timelines/draft/${draftTimelineId}/details`);
  },

  /**
   * Get user's draft timelines
   */
  getUserDrafts: async (baselineId?: string, activeOnly?: boolean): Promise<DraftTimeline[]> => {
    return api.get('/api/v1/timelines/drafts', { baselineId, activeOnly });
  },

  /**
   * Commit draft timeline
   */
  commit: async (data: CommitTimelineRequest): Promise<{ committedTimelineId: string }> => {
    return api.post('/api/v1/timelines/commit', data);
  },

  /**
   * Get committed timeline by ID
   */
  getCommitted: async (committedTimelineId: string): Promise<CommittedTimeline> => {
    return api.get(`/api/v1/timelines/committed/${committedTimelineId}`);
  },

  /**
   * Get committed timeline with stages and milestones
   */
  getCommittedWithDetails: async (committedTimelineId: string): Promise<{
    timeline: CommittedTimeline;
    baseline: any;
    draftTimeline: any;
    stages: Array<{
      stage: TimelineStage;
      milestones: TimelineMilestone[];
    }>;
    totalStages: number;
    totalMilestones: number;
  }> => {
    return api.get(`/api/v1/timelines/committed/${committedTimelineId}/details`);
  },

  /**
   * Get user's committed timelines
   */
  getUserCommitted: async (baselineId?: string): Promise<CommittedTimeline[]> => {
    return api.get('/api/v1/timelines/committed', { baselineId });
  },

  /**
   * Check if draft timeline is committed
   */
  isCommitted: async (draftTimelineId: string): Promise<{ isCommitted: boolean }> => {
    return api.get(`/api/v1/timelines/draft/${draftTimelineId}/is-committed`);
  },
};

export default timelineService;
