/**
 * Protected Route Component
 * 
 * Wrapper for routes that require specific backend state.
 * Provides a simpler API than RouteGuard for common use cases.
 */

import { RouteGuard } from './RouteGuard';
import { 
  guardTimelineGenerationRequiresBaseline,
  guardCommitRequiresDraft,
  guardProgressRequiresCommittedTimeline,
  guardAnalyticsRequiresCommittedTimeline,
} from './stateGuards';

/**
 * Protected Route Props
 */
interface ProtectedRouteProps {
  children: React.ReactNode;
  /**
   * Type of protection required
   */
  requires: 'baseline' | 'draft' | 'committed' | 'analytics';
  /**
   * Fallback route if requirement not met
   */
  fallbackRoute?: string;
  /**
   * Custom fallback message
   */
  fallbackMessage?: string;
}

/**
 * Guard function mapping
 */
const GUARD_FUNCTIONS = {
  baseline: guardTimelineGenerationRequiresBaseline,
  draft: guardCommitRequiresDraft,
  committed: guardProgressRequiresCommittedTimeline,
  analytics: guardAnalyticsRequiresCommittedTimeline,
};

/**
 * Default fallback routes
 */
const DEFAULT_FALLBACK_ROUTES = {
  baseline: '/timeline',
  draft: '/timelines/generate',
  committed: '/timelines/generate',
  analytics: '/timelines/generate',
};

/**
 * Default fallback messages
 */
const DEFAULT_FALLBACK_MESSAGES = {
  baseline: 'Please create a baseline before accessing this page.',
  draft: 'Please generate a draft timeline before accessing this page.',
  committed: 'Please commit a timeline before accessing this page.',
  analytics: 'Please commit a timeline before viewing analytics.',
};

/**
 * Protected Route Component
 * 
 * Simple wrapper for routes that require specific state.
 * 
 * Usage:
 * ```tsx
 * <ProtectedRoute requires="baseline" fallbackRoute="/timeline">
 *   <TimelineGenerationPage />
 * </ProtectedRoute>
 * ```
 */
export function ProtectedRoute({
  children,
  requires,
  fallbackRoute,
  fallbackMessage,
}: ProtectedRouteProps) {
  const guard = GUARD_FUNCTIONS[requires];
  const defaultFallbackRoute = DEFAULT_FALLBACK_ROUTES[requires];
  const defaultFallbackMessage = DEFAULT_FALLBACK_MESSAGES[requires];
  
  return (
    <RouteGuard
      customGuard={guard}
      fallbackRoute={fallbackRoute || defaultFallbackRoute}
      fallbackMessage={fallbackMessage || defaultFallbackMessage}
    >
      {children}
    </RouteGuard>
  );
}
