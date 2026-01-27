/**
 * Services Index
 * 
 * Central export point for all API services.
 */

export { api, apiClient } from './api.client';
export { documentService } from './document.service';
export { baselineService } from './baseline.service';
export { timelineService } from './timeline.service';
export { progressService } from './progress.service';
export { assessmentService } from './assessment.service';

// Re-export types for convenience
export type * from '@/types/api';
