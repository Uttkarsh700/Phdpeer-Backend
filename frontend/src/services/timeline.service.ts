/**
 * Timeline Service
 * 
 * Handles timeline creation, commitment, and management API calls.
 * 
 * IMPORTANT: All API calls go through @/api/client (apiClient)
 */

import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import type {
  DraftTimeline,
  CommittedTimeline,
  TimelineStage,
  TimelineMilestone,
  CreateTimelineRequest,
  CommitTimelineRequest,
} from '@/types/api';
import type { TimelineGenerationResponse } from '@/types/timeline';

export const timelineService = {
  /**
   * Generate draft timeline from baseline
   * 
   * Triggers timeline generation via POST /api/v1/timelines/draft/generate
   * Returns complete timeline with stages and milestones.
   */
  generate: async (data: {
    baselineId: string;
    title?: string;
    description?: string;
    versionNumber?: string;
  }): Promise<TimelineGenerationResponse> => {
    return apiClient.post<TimelineGenerationResponse>(
      `${ENDPOINTS.TIMELINES.DRAFT}/generate`,
      data
    );
  },

  /**
   * Create draft timeline from baseline
   */
  createDraft: async (data: CreateTimelineRequest): Promise<{ draftTimelineId: string }> => {
    return apiClient.post<{ draftTimelineId: string }>(ENDPOINTS.TIMELINES.DRAFT, data);
  },

  /**
   * Get draft timeline by ID
   */
  getDraft: async (draftTimelineId: string): Promise<DraftTimeline> => {
    return apiClient.get<DraftTimeline>(ENDPOINTS.TIMELINES.GET_DRAFT(draftTimelineId));
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
    return apiClient.get(`${ENDPOINTS.TIMELINES.GET_DRAFT(draftTimelineId)}/details`);
  },

  /**
   * Get user's draft timelines
   */
  getUserDrafts: async (baselineId?: string, activeOnly?: boolean): Promise<DraftTimeline[]> => {
    return apiClient.get<DraftTimeline[]>(ENDPOINTS.TIMELINES.DRAFT, {
      baselineId,
      activeOnly,
    });
  },

  /**
   * Commit draft timeline
   * 
   * Calls POST /api/v1/timelines/draft/:id/commit
   * Returns the committed timeline ID from the response.
   * 
   * Note: Frontend does not validate business rules - passes data through to backend.
   */
  commit: async (data: CommitTimelineRequest): Promise<{ committedTimelineId: string }> => {
    // Backend expects request_id for idempotency - generate one if not provided
    const requestId = data.requestId || crypto.randomUUID();
    
    const response = await apiClient.post<{
      committed_timeline?: { id: string };
      committedTimelineId?: string;
    }>(
      ENDPOINTS.TIMELINES.COMMIT(data.draftTimelineId),
      { 
        request_id: requestId,
        title: data.title, 
        description: data.description,
      }
    );
    
    // Extract committed timeline ID from response
    // Backend may return it as committed_timeline.id or committedTimelineId
    const committedTimelineId = response.committed_timeline?.id || response.committedTimelineId;
    if (!committedTimelineId) {
      throw new Error('Commit response missing committed timeline ID');
    }
    
    return { committedTimelineId };
  },

  /**
   * Get committed timeline by ID
   */
  getCommitted: async (committedTimelineId: string): Promise<CommittedTimeline> => {
    return apiClient.get<CommittedTimeline>(ENDPOINTS.TIMELINES.GET_COMMITTED(committedTimelineId));
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
    return apiClient.get(`${ENDPOINTS.TIMELINES.GET_COMMITTED(committedTimelineId)}/details`);
  },

  /**
   * Get user's committed timelines
   */
  getUserCommitted: async (baselineId?: string): Promise<CommittedTimeline[]> => {
    return apiClient.get<CommittedTimeline[]>(ENDPOINTS.TIMELINES.LIST, { baselineId });
  },

  /**
   * Check if draft timeline is committed
   */
  isCommitted: async (draftTimelineId: string): Promise<{ isCommitted: boolean }> => {
    return apiClient.get<{ isCommitted: boolean }>(
      `${ENDPOINTS.TIMELINES.GET_DRAFT(draftTimelineId)}/is-committed`
    );
  },
};

export default timelineService;
