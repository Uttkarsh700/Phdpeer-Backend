/**
 * State-to-Screen Mapping
 * 
 * Maps global application state to the appropriate screen/route.
 * 
 * RULES:
 * - No baseline → Upload screen
 * - Baseline exists → Timeline generation
 * - Draft timeline → Editable timeline
 * - Committed timeline → Progress tracking
 * - Doctor submitted → Health summary
 * - Analytics available → Dashboard
 * 
 * This mapping determines the default screen based on user's current state.
 */

import type { GlobalState } from '../types';

/**
 * Screen/Route identifier
 */
export type AppScreen =
  | 'upload'              // Document upload (no baseline)
  | 'timeline-generation' // Timeline generation (baseline exists, no timeline)
  | 'draft-timeline'      // Editable draft timeline
  | 'progress-tracking'   // Progress tracking (committed timeline)
  | 'health-summary'      // Health summary (doctor submitted)
  | 'dashboard';          // Analytics dashboard (analytics available)

/**
 * Route path for each screen
 */
export const SCREEN_ROUTES: Record<AppScreen, string> = {
  upload: '/documents/upload',
  'timeline-generation': '/timelines',
  'draft-timeline': '/timelines', // Will need draftId from state
  'progress-tracking': '/progress', // Will need timelineId from state
  'health-summary': '/health',
  dashboard: '/dashboard',
};

/**
 * Priority order for state-to-screen mapping
 * 
 * Higher priority screens are checked first.
 * This ensures the most relevant screen is shown.
 */
const SCREEN_PRIORITY: AppScreen[] = [
  'dashboard',           // Highest priority: Analytics available
  'health-summary',       // Doctor submitted
  'progress-tracking',   // Committed timeline
  'draft-timeline',       // Draft timeline
  'timeline-generation',  // Baseline exists
  'upload',               // Lowest priority: No baseline
];

/**
 * Map global state to the appropriate screen
 * 
 * Uses priority order to determine the most relevant screen.
 * 
 * @param state - Global application state
 * @returns The appropriate screen identifier
 * 
 * @example
 * ```typescript
 * const state = useGlobalStateStore();
 * const screen = getScreenFromState(state);
 * navigate(SCREEN_ROUTES[screen]);
 * ```
 */
export function getScreenFromState(state: GlobalState): AppScreen {
  // Check in priority order (highest to lowest)
  
  // 1. Analytics available → Dashboard
  if (state.analyticsStatus === 'AVAILABLE') {
    return 'dashboard';
  }
  
  // 2. Doctor submitted → Health summary
  if (state.doctorStatus === 'SUBMITTED') {
    return 'health-summary';
  }
  
  // 3. Committed timeline → Progress tracking
  if (state.timelineStatus === 'COMMITTED') {
    return 'progress-tracking';
  }
  
  // 4. Draft timeline → Editable timeline
  if (state.timelineStatus === 'DRAFT') {
    return 'draft-timeline';
  }
  
  // 5. Baseline exists → Timeline generation
  if (state.baselineStatus === 'EXISTS') {
    return 'timeline-generation';
  }
  
  // 6. No baseline → Upload screen
  return 'upload';
}

/**
 * Get route path for a screen
 * 
 * @param screen - Screen identifier
 * @returns Route path
 */
export function getRouteForScreen(screen: AppScreen): string {
  return SCREEN_ROUTES[screen];
}

/**
 * Get route path directly from state
 * 
 * Convenience function that combines getScreenFromState and getRouteForScreen
 * 
 * @param state - Global application state
 * @returns Route path
 * 
 * @example
 * ```typescript
 * const state = useGlobalStateStore();
 * const route = getRouteFromState(state);
 * navigate(route);
 * ```
 */
export function getRouteFromState(state: GlobalState): string {
  const screen = getScreenFromState(state);
  return getRouteForScreen(screen);
}

/**
 * Screen mapping configuration
 * 
 * Documents the mapping rules for reference
 */
export const SCREEN_MAPPING_RULES = {
  /**
   * No baseline → Upload screen
   * 
   * When: baselineStatus === 'NONE'
   * Route: /documents/upload
   * Purpose: User needs to upload a document to create a baseline
   */
  upload: {
    condition: (state: GlobalState) => state.baselineStatus === 'NONE',
    route: '/documents/upload',
    description: 'Upload document to create baseline',
  },

  /**
   * Baseline exists → Timeline generation
   * 
   * When: baselineStatus === 'EXISTS' && timelineStatus === 'NONE'
   * Route: /timelines
   * Purpose: User can generate a timeline from their baseline
   */
  'timeline-generation': {
    condition: (state: GlobalState) => 
      state.baselineStatus === 'EXISTS' && state.timelineStatus === 'NONE',
    route: '/timelines',
    description: 'Generate timeline from baseline',
  },

  /**
   * Draft timeline → Editable timeline
   * 
   * When: timelineStatus === 'DRAFT'
   * Route: /timelines/draft/:draftId
   * Purpose: User can edit their draft timeline
   */
  'draft-timeline': {
    condition: (state: GlobalState) => state.timelineStatus === 'DRAFT',
    route: '/timelines',
    description: 'Edit draft timeline',
  },

  /**
   * Committed timeline → Progress tracking
   * 
   * When: timelineStatus === 'COMMITTED'
   * Route: /progress/timeline/:timelineId
   * Purpose: User can track progress against committed timeline
   */
  'progress-tracking': {
    condition: (state: GlobalState) => state.timelineStatus === 'COMMITTED',
    route: '/progress',
    description: 'Track progress against committed timeline',
  },

  /**
   * Doctor submitted → Health summary
   * 
   * When: doctorStatus === 'SUBMITTED'
   * Route: /health
   * Purpose: User can view their health assessment results
   */
  'health-summary': {
    condition: (state: GlobalState) => state.doctorStatus === 'SUBMITTED',
    route: '/health',
    description: 'View health assessment summary',
  },

  /**
   * Analytics available → Dashboard
   * 
   * When: analyticsStatus === 'AVAILABLE'
   * Route: /dashboard
   * Purpose: User can view analytics dashboard
   */
  dashboard: {
    condition: (state: GlobalState) => state.analyticsStatus === 'AVAILABLE',
    route: '/dashboard',
    description: 'View analytics dashboard',
  },
} as const;
