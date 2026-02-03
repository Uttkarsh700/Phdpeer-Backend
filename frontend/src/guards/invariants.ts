/**
 * Frontend Invariant Checks
 * 
 * Enforces business rules based on backend state.
 * 
 * Rules:
 * - No timeline generation without baseline
 * - No commit without draft
 * - No progress without committed timeline
 * - No analytics without committed timeline
 * 
 * Guards rely only on backend state (global state store).
 * These checks prevent invalid operations before API calls.
 */

import type { GlobalState } from '@/state/types';

/**
 * Invariant violation error
 */
export class InvariantViolationError extends Error {
  constructor(
    message: string,
    public readonly invariant: string,
    public readonly currentState: Partial<GlobalState>
  ) {
    super(message);
    this.name = 'InvariantViolationError';
  }
}

/**
 * Check: No timeline generation without baseline
 * 
 * Invariant: baselineStatus === 'EXISTS'
 * 
 * @param state - Current global state
 * @throws InvariantViolationError if baseline does not exist
 */
export function checkTimelineGenerationRequiresBaseline(state: GlobalState): void {
  if (state.baselineStatus !== 'EXISTS') {
    throw new InvariantViolationError(
      'Cannot generate timeline: Baseline is required. Please create a baseline first.',
      'timeline_generation_requires_baseline',
      { baselineStatus: state.baselineStatus }
    );
  }
}

/**
 * Check: No commit without draft
 * 
 * Invariant: timelineStatus === 'DRAFT'
 * 
 * @param state - Current global state
 * @throws InvariantViolationError if no draft timeline exists
 */
export function checkCommitRequiresDraft(state: GlobalState): void {
  if (state.timelineStatus !== 'DRAFT') {
    throw new InvariantViolationError(
      'Cannot commit timeline: Draft timeline is required. Please create a draft timeline first.',
      'commit_requires_draft',
      { timelineStatus: state.timelineStatus }
    );
  }
}

/**
 * Check: No progress without committed timeline
 * 
 * Invariant: timelineStatus === 'COMMITTED'
 * 
 * @param state - Current global state
 * @throws InvariantViolationError if no committed timeline exists
 */
export function checkProgressRequiresCommittedTimeline(state: GlobalState): void {
  if (state.timelineStatus !== 'COMMITTED') {
    throw new InvariantViolationError(
      'Cannot track progress: Committed timeline is required. Please commit a timeline first.',
      'progress_requires_committed_timeline',
      { timelineStatus: state.timelineStatus }
    );
  }
}

/**
 * Check: No analytics without committed timeline
 * 
 * Invariant: timelineStatus === 'COMMITTED' (analytics require committed timeline)
 * 
 * Note: We check timelineStatus directly, not analyticsStatus, because:
 * - analyticsStatus is a derived status that may not be updated immediately
 * - The actual invariant is "no analytics without committed timeline"
 * - timelineStatus === 'COMMITTED' is the source of truth
 * 
 * @param state - Current global state
 * @throws InvariantViolationError if no committed timeline exists
 */
export function checkAnalyticsRequiresCommittedTimeline(state: GlobalState): void {
  if (state.timelineStatus !== 'COMMITTED') {
    throw new InvariantViolationError(
      'Cannot load analytics: Committed timeline is required. Please commit a timeline first.',
      'analytics_requires_committed_timeline',
      { 
        timelineStatus: state.timelineStatus,
        analyticsStatus: state.analyticsStatus 
      }
    );
  }
}

/**
 * Invariant check result
 */
export interface InvariantCheckResult {
  /** Whether the invariant check passed */
  valid: boolean;
  /** Error message if check failed */
  error?: string;
  /** Invariant name if check failed */
  invariant?: string;
}

/**
 * Check all invariants for a given operation
 * 
 * @param operation - Operation to check
 * @param state - Current global state
 * @returns Check result
 */
export function checkInvariant(
  operation: 'timeline_generation' | 'commit' | 'progress' | 'analytics',
  state: GlobalState
): InvariantCheckResult {
  try {
    switch (operation) {
      case 'timeline_generation':
        checkTimelineGenerationRequiresBaseline(state);
        break;
      case 'commit':
        checkCommitRequiresDraft(state);
        break;
      case 'progress':
        checkProgressRequiresCommittedTimeline(state);
        break;
      case 'analytics':
        checkAnalyticsRequiresCommittedTimeline(state);
        break;
    }
    return { valid: true };
  } catch (error) {
    if (error instanceof InvariantViolationError) {
      return {
        valid: false,
        error: error.message,
        invariant: error.invariant,
      };
    }
    return {
      valid: false,
      error: 'Unknown invariant violation',
    };
  }
}
