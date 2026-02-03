/**
 * Invariant Guard Component
 * 
 * Prevents rendering or actions when invariants are violated.
 * 
 * Usage:
 * ```tsx
 * <InvariantGuard
 *   operation="timeline_generation"
 *   fallback={<Navigate to="/documents/upload" />}
 * >
 *   <TimelineGenerationForm />
 * </InvariantGuard>
 * ```
 */

import React from 'react';
import { useGlobalStateStore } from '@/state/global';
import { checkInvariant } from '@/guards/invariants';

export interface InvariantGuardProps {
  /** Operation to check invariant for */
  operation: 'timeline_generation' | 'commit' | 'progress' | 'analytics';
  /** Children to render if invariant passes */
  children: React.ReactNode;
  /** Fallback UI to render if invariant fails */
  fallback?: React.ReactNode;
  /** Optional custom error message */
  errorMessage?: string;
}

/**
 * Invariant Guard Component
 * 
 * Checks backend state invariants before rendering children.
 * Shows fallback UI if invariant is violated.
 */
export function InvariantGuard({
  operation,
  children,
  fallback,
  errorMessage,
}: InvariantGuardProps) {
  const state = useGlobalStateStore();
  const check = checkInvariant(operation, state);

  if (!check.valid) {
    if (fallback) {
      return <>{fallback}</>;
    }

    // Default error UI
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-semibold text-yellow-800">Operation Not Available</h3>
              <p className="mt-1 text-sm text-yellow-700">
                {errorMessage || check.error}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export default InvariantGuard;
