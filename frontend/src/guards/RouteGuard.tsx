/**
 * Route Guard Component
 * 
 * Wraps routes to enforce business rules based on backend state.
 * Checks guards before rendering children, redirects if guard fails.
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGlobalStateStore, type GlobalState } from '@/store/global-state';
import { useToast } from '@/hooks/use-toast';
import { GuardViolationError } from './stateGuards';

/**
 * Route Guard Props
 */
interface RouteGuardProps {
  children: React.ReactNode;
  /**
   * Guard function to check before rendering
   */
  customGuard: (state: GlobalState) => void;
  /**
   * Fallback route if guard fails
   */
  fallbackRoute?: string;
  /**
   * Custom fallback message
   */
  fallbackMessage?: string;
}

/**
 * Route Guard Component
 * 
 * Checks guard function before rendering children.
 * Redirects to fallback route if guard fails.
 * 
 * Usage:
 * ```tsx
 * <RouteGuard
 *   customGuard={guardAnalyticsRequiresCommittedTimeline}
 *   fallbackRoute="/timeline"
 *   fallbackMessage="Please commit a timeline first"
 * >
 *   <Dashboard />
 * </RouteGuard>
 * ```
 */
export function RouteGuard({
  children,
  customGuard,
  fallbackRoute = '/home',
  fallbackMessage,
}: RouteGuardProps) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const baselineStatus = useGlobalStateStore((state) => state.baselineStatus);
  const timelineStatus = useGlobalStateStore((state) => state.timelineStatus);
  const doctorStatus = useGlobalStateStore((state) => state.doctorStatus);
  const analyticsStatus = useGlobalStateStore((state) => state.analyticsStatus);
  
  // Create state object for guard
  const state: GlobalState = {
    baselineStatus,
    timelineStatus,
    doctorStatus,
    analyticsStatus,
  };

  useEffect(() => {
    try {
      // Check guard
      customGuard(state);
      // Guard passed - children will render
    } catch (error) {
      // Guard failed - show message and redirect
      if (error instanceof GuardViolationError) {
        const message = fallbackMessage || error.message;
        toast({
          title: 'Access Restricted',
          description: message,
          variant: 'default',
        });
      } else {
        toast({
          title: 'Access Restricted',
          description: fallbackMessage || 'This page requires additional setup.',
          variant: 'default',
        });
      }
      
      // Redirect to fallback route
      navigate(fallbackRoute, { replace: true });
    }
  }, [customGuard, baselineStatus, timelineStatus, doctorStatus, analyticsStatus, navigate, fallbackRoute, fallbackMessage, toast]);

  // Try to check guard synchronously for immediate feedback
  try {
    customGuard(state);
    // Guard passed - render children
    return <>{children}</>;
  } catch (error) {
    // Guard failed - return null (redirect will happen in useEffect)
    return null;
  }
}

/**
 * Hook to check if a route is accessible
 * 
 * Usage:
 * ```tsx
 * const isAccessible = useRouteAccessible(guardAnalyticsRequiresCommittedTimeline);
 * ```
 */
export function useRouteAccessible(
  customGuard: (state: GlobalState) => void
): boolean {
  const store = useGlobalStateStore();
  
  // Extract just the state properties (not the actions)
  const state: GlobalState = {
    baselineStatus: store.baselineStatus,
    timelineStatus: store.timelineStatus,
    doctorStatus: store.doctorStatus,
    analyticsStatus: store.analyticsStatus,
  };
  
  try {
    customGuard(state);
    return true;
  } catch (error) {
    return false;
  }
}
