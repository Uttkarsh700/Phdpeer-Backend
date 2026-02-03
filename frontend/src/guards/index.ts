/**
 * Route Guards Module
 * 
 * Guards routes based on global state to prevent invalid navigation.
 */

export { RouteGuard } from './RouteGuard';
export {
  isRouteValidForState,
  getRouteFromState,
  ROUTE_VALIDATION_RULES,
} from './routeValidation';
