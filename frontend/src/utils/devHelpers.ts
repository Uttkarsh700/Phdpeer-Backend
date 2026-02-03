/**
 * Development Helpers
 * 
 * Utility functions for development and testing.
 * These should not be used in production.
 */

/**
 * Demo user IDs from seed_demo_data.py
 * These are the UUIDs created by the seed script for development
 */
const DEMO_USER_IDS = {
  // Sarah Chen - Early-stage PhD (has committed timeline)
  SARAH: '11111111-1111-1111-1111-111111111111',
  // Marcus Johnson - Mid-stage PhD (has committed timeline)
  MARCUS: '22222222-2222-2222-2222-222222222222',
  // Elena Rodriguez - Late-stage PhD (has committed timeline)
  ELENA: '33333333-3333-3333-3333-333333333333',
} as const;

/**
 * Get or create a development user ID
 * 
 * For development: tries to get user_id from localStorage,
 * or uses a demo user ID from seed script if none exists.
 * 
 * In production, this should come from authentication context.
 */
export function getDevUserId(): string | null {
  // Try to get from localStorage first
  const storedUserId = localStorage.getItem('user_id') || 
                       localStorage.getItem('current_user_id') ||
                       localStorage.getItem('userId');
  
  if (storedUserId) {
    return storedUserId;
  }
  
  // For development: use a demo user ID from seed script
  // Default to Sarah Chen (early-stage PhD with committed timeline)
  if (import.meta.env.DEV) {
    const defaultUserId = DEMO_USER_IDS.SARAH;
    localStorage.setItem('user_id', defaultUserId);
    console.warn('[DEV] Using demo user ID (Sarah Chen):', defaultUserId);
    console.warn('[DEV] This user has a committed timeline and can view analytics');
    console.warn('[DEV] To use a different user, set it in localStorage:');
    console.warn('[DEV]   - Sarah (early-stage):', DEMO_USER_IDS.SARAH);
    console.warn('[DEV]   - Marcus (mid-stage):', DEMO_USER_IDS.MARCUS);
    console.warn('[DEV]   - Elena (late-stage):', DEMO_USER_IDS.ELENA);
    console.warn('[DEV]   Example: localStorage.setItem("user_id", "' + DEMO_USER_IDS.MARCUS + '")');
    return defaultUserId;
  }
  
  return null;
}

/**
 * Check if we're in development mode
 */
export function isDevelopment(): boolean {
  return import.meta.env.DEV;
}
