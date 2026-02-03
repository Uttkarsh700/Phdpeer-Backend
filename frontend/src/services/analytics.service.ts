/**
 * Analytics Service
 * 
 * Handles analytics and dashboard API calls.
 * 
 * IMPORTANT: All API calls go through @/api/client (apiClient)
 */

import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import type { AnalyticsSummary } from '@/types/api';

export const analyticsService = {
  /**
   * Get analytics summary
   * 
   * Calls GET /analytics/summary
   * Returns dashboard-ready analytics data.
   * 
   * Note: Frontend does not calculate - all data comes from backend.
   * Backend returns wrapped response: { summary: AnalyticsSummary, ... }
   */
  getSummary: async (params?: {
    timelineId?: string;
    userId?: string;
  }): Promise<AnalyticsSummary> => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analytics.service.ts:23',message:'getSummary called',data:{hasParams:!!params,userId:params?.userId,timelineId:params?.timelineId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    // Backend requires user_id as query parameter
    // Convert userId to user_id for backend API
    const queryParams = params ? {
      ...(params.userId && { user_id: params.userId }),
      ...(params.timelineId && { timeline_id: params.timelineId }),
    } : undefined;
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analytics.service.ts:32',message:'Query params prepared',data:{queryParams,hasUserId:!!queryParams?.user_id,userIdValue:queryParams?.user_id},"timestamp":Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    
    // Backend returns: { snapshot_id, summary: AnalyticsSummary, ... }
    const response = await apiClient.get<{
      snapshot_id: string;
      summary: AnalyticsSummary;
      created_at?: string;
      from_cache?: boolean;
    }>(ENDPOINTS.ANALYTICS.SUMMARY, queryParams);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analytics.service.ts:42',message:'API response received',data:{hasResponse:!!response,hasSummary:'summary' in response,responseKeys:Object.keys(response||{})},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
    // #endregion
    
    // Extract summary from wrapped response
    return response.summary;
  },
};

export default analyticsService;
