/**
 * Development Helpers
 * 
 * Utility functions for development and testing.
 */

/**
 * Get development user ID
 * 
 * TODO: Replace with actual authentication/user context
 * For now, returns a demo user ID for testing.
 */
export function getDevUserId(): string {
  // Demo user ID - replace with actual user context
  // In production, this should come from authentication context
  return '550e8400-e29b-41d4-a716-446655440000'; // Demo user UUID
}

// Default export for compatibility
export default {
  getDevUserId,
};
