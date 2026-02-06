/**
 * Navigation Guard Hook
 * 
 * Provides utilities for checking route accessibility before navigation.
 * Useful for disabling buttons/links that lead to inaccessible routes.
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGlobalStateStore } from '@/store/global-state';
import { 
  guardTimelineGenerationRequiresBaseline,
  guardCommitRequiresDraft,
  guardProgressRequiresCommittedTimeline,
  guardAnalyticsRequiresCommittedTimeline,
  GuardViolationError,
} from './stateGuards';
import { useToast } from '@/hooks/use-toast';

/**
 * Route requirements mapping for navigation
 */
const NAVIGATION_GUARDS: Record<string, (state: ReturnType<typeof useGlobalStateStore>) => void> = {
  '/timelines/generate': guardTimelineGenerationRequiresBaseline,
  '/timelines/commit': guardCommitRequiresDraft,
  '/timelines/progress': guardProgressRequiresCommittedTimeline,
  '/dashboard': guardAnalyticsRequiresCommittedTimeline,
  '/analytics': guardAnalyticsRequiresCommittedTimeline,
};

/**
 * Get guard for a route path
 */
function getGuardForRoute(pathname: string): ((state: ReturnType<typeof useGlobalStateStore>) => void) | null {
  // Check exact match
  if (NAVIGATION_GUARDS[pathname]) {
    return NAVIGATION_GUARDS[pathname];
  }
  
  // Check pattern matches (for dynamic routes)
  for (const [pattern, guard] of Object.entries(NAVIGATION_GUARDS)) {
    const regexPattern = pattern.replace(/:[^/]+/g, '[^/]+');
    const regex = new RegExp(`^${regexPattern}$`);
    if (regex.test(pathname)) {
      return guard;
    }
  }
  
  return null;
}

/**
 * Navigation Guard Hook
 * 
 * Provides safe navigation that checks route accessibility.
 * 
 * Usage:
 * ```tsx
 * const { navigateSafely, isRouteAccessible } = useNavigationGuard();
 * 
 * <Button 
 *   disabled={!isRouteAccessible('/dashboard')}
 *   onClick={() => navigateSafely('/dashboard')}
 * >
 *   View Dashboard
 * </Button>
 * ```
 */
export function useNavigationGuard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const state = useGlobalStateStore();
  
  /**
   * Check if a route is accessible
   */
  const isRouteAccessible = useCallback((pathname: string): boolean => {
    try {
      const guard = getGuardForRoute(pathname);
      if (guard) {
        guard(state);
      }
      return true;
    } catch (error) {
      return false;
    }
  }, [state]);
  
  /**
   * Navigate to a route safely
   * Checks accessibility first and shows toast if route is not accessible
   */
  const navigateSafely = useCallback((pathname: string, options?: { replace?: boolean }) => {
    try {
      const guard = getGuardForRoute(pathname);
      if (guard) {
        guard(state);
      }
      
      // Route is accessible - navigate
      navigate(pathname, options);
      return true;
    } catch (error) {
      // Route is not accessible - show toast
      if (error instanceof GuardViolationError) {
        toast({
          title: 'Navigation Blocked',
          description: error.message,
          variant: 'default',
        });
      } else {
        toast({
          title: 'Navigation Blocked',
          description: 'This page requires additional setup.',
          variant: 'default',
        });
      }
      return false;
    }
  }, [navigate, toast, state]);
  
  return {
    isRouteAccessible,
    navigateSafely,
  };
}
