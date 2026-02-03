/**
 * Route Validation
 * 
 * Validates if a route is accessible given the current global state.
 * 
 * RULES:
 * - No API calls - uses only global state
 * - Returns true if route is valid, false otherwise
 * - Used by RouteGuard to prevent invalid navigation
 */

import type { GlobalState } from '@/state/types';
import { SCREEN_ROUTES, getScreenFromState, getRouteFromState as getRouteFromStateMapping } from '@/state/navigation';

/**
 * Route-to-screen mapping
 * 
 * Maps route paths to their corresponding screen identifiers.
 * Used to determine which screen a route belongs to.
 */
const ROUTE_TO_SCREEN: Record<string, string> = {
  '/documents/upload': 'upload',
  '/documents': 'upload', // Documents list also requires upload capability
  '/timelines': 'timeline-generation', // Timeline generation/list
  '/timelines/draft': 'draft-timeline', // Draft timeline (with ID)
  '/timelines/committed': 'progress-tracking', // Committed timeline (with ID)
  '/progress': 'progress-tracking',
  '/progress/timeline': 'progress-tracking', // Progress with timeline ID
  '/health': 'health-summary',
  '/health/assessment': 'health-summary', // Assessment form
  '/health/history': 'health-summary', // Assessment history
  '/dashboard': 'dashboard',
};

/**
 * Check if a route path matches a screen
 * 
 * Handles parameterized routes (e.g., /timelines/draft/:draftId)
 */
function getScreenFromRoute(pathname: string): string | null {
  // Check exact matches first
  if (ROUTE_TO_SCREEN[pathname]) {
    return ROUTE_TO_SCREEN[pathname];
  }

  // Check prefix matches for parameterized routes
  for (const [route, screen] of Object.entries(ROUTE_TO_SCREEN)) {
    if (pathname.startsWith(route)) {
      return screen;
    }
  }

  return null;
}

/**
 * Check if a screen is valid for the current state
 * 
 * @param screen - Screen identifier
 * @param state - Global state
 * @returns True if screen is valid for state
 */
function isScreenValidForState(screen: string, state: GlobalState): boolean {
  switch (screen) {
    case 'upload':
      // Upload is valid when no baseline exists
      return state.baselineStatus === 'NONE';

    case 'timeline-generation':
      // Timeline generation is valid when baseline exists but no timeline
      return state.baselineStatus === 'EXISTS' && state.timelineStatus === 'NONE';

    case 'draft-timeline':
      // Draft timeline is valid when draft timeline exists
      return state.timelineStatus === 'DRAFT';

    case 'progress-tracking':
      // Progress tracking is valid when committed timeline exists
      return state.timelineStatus === 'COMMITTED';

    case 'health-summary':
      // Health summary is valid when doctor has submitted
      return state.doctorStatus === 'SUBMITTED';

    case 'dashboard':
      // Dashboard is valid when analytics are available
      return state.analyticsStatus === 'AVAILABLE';

    default:
      // Unknown screen - allow access (might be a detail page or other route)
      return true;
  }
}

/**
 * Check if a route is valid for the current global state
 * 
 * @param pathname - Current route pathname
 * @param state - Global application state
 * @returns True if route is valid for current state, false otherwise
 * 
 * @example
 * ```typescript
 * const isValid = isRouteValidForState('/dashboard', state);
 * if (!isValid) {
 *   // Redirect to valid route
 * }
 * ```
 */
export function isRouteValidForState(
  pathname: string,
  state: GlobalState
): boolean {
  // Get screen identifier from route
  const screen = getScreenFromRoute(pathname);

  // If route doesn't map to a known screen, allow access
  // (might be a detail page, 404, or other route that doesn't need state validation)
  if (!screen) {
    return true;
  }

  // Check if screen is valid for current state
  return isScreenValidForState(screen, state);
}

/**
 * Get valid route for current state
 * 
 * Convenience function that uses the state-to-screen mapping.
 * 
 * @param state - Global application state
 * @returns Valid route path for current state
 */
export function getRouteFromState(state: GlobalState): string {
  return getRouteFromStateMapping(state);
}

/**
 * Route validation rules
 * 
 * Documents which routes are valid for which states.
 */
export const ROUTE_VALIDATION_RULES = {
  '/documents/upload': {
    validWhen: (state: GlobalState) => state.baselineStatus === 'NONE',
    description: 'Upload screen requires no baseline',
  },
  '/timelines': {
    validWhen: (state: GlobalState) => 
      state.baselineStatus === 'EXISTS' && 
      (state.timelineStatus === 'NONE' || state.timelineStatus === 'DRAFT'),
    description: 'Timeline screen requires baseline, allows draft',
  },
  '/progress': {
    validWhen: (state: GlobalState) => state.timelineStatus === 'COMMITTED',
    description: 'Progress screen requires committed timeline',
  },
  '/health': {
    validWhen: (state: GlobalState) => state.doctorStatus === 'SUBMITTED',
    description: 'Health screen requires submitted questionnaire',
  },
  '/dashboard': {
    validWhen: (state: GlobalState) => state.analyticsStatus === 'AVAILABLE',
    description: 'Dashboard requires analytics available',
  },
} as const;
