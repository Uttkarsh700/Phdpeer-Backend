/**
 * Route Guard Component
 * 
 * Prevents navigation to invalid screens based on global state.
 * Redirects to valid screen if current route is invalid.
 * 
 * RULES:
 * - Guards rely ONLY on global state (no API calls)
 * - Graceful fallback to valid screen
 * - Prevents navigation to invalid screens
 */

import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useGlobalStateStore } from '@/state/global';
import { getRouteFromState, isRouteValidForState } from '@/guards/routeValidation';

interface RouteGuardProps {
  children: React.ReactNode;
}

/**
 * Route Guard Component
 * 
 * Wraps routes and ensures user can only access screens valid for their current state.
 * 
 * @example
 * ```tsx
 * <RouteGuard>
 *   <DashboardPage />
 * </RouteGuard>
 * ```
 */
export function RouteGuard({ children }: RouteGuardProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const state = useGlobalStateStore();

  useEffect(() => {
    // Check if current route is valid for current state
    const isValid = isRouteValidForState(location.pathname, state);

    if (!isValid) {
      // Route is invalid - redirect to valid screen
      const validRoute = getRouteFromState(state);
      
      // Only redirect if we're not already on the valid route
      if (location.pathname !== validRoute) {
        navigate(validRoute, { replace: true });
      }
    }
  }, [location.pathname, state, navigate]);

  // Render children if route is valid
  return <>{children}</>;
}
