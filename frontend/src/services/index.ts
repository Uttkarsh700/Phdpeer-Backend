/**
 * Services Index
 * 
 * Central export point for all API services.
 * 
 * IMPORTANT: All services use the centralized API client from @/api/client
 */

// Re-export API client (for backward compatibility during migration)
export { apiClient, api, ApiClient, ApiClientError } from '@/api/client';
export type { ApiRequestOptions, ApiResponse } from '@/api/client';

// Export all services
export { documentService } from './document.service';
export { baselineService } from './baseline.service';
export { timelineService } from './timeline.service';
export { progressService } from './progress.service';
export { assessmentService } from './assessment.service';
export { analyticsService } from './analytics.service';

// Re-export types for convenience
export type * from '@/types/api';
