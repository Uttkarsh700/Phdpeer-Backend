/**
 * Frontend State Guards
 * 
 * Enforces business rules based on backend state only.
 * These guards check the global state store that mirrors backend state.
 * 
 * Rules:
 * - No timeline generation without baseline
 * - No commit without draft
 * - No progress without committed timeline
 * - No analytics without committed timeline
 */

import { useGlobalStateStore, type GlobalState } from '@/store/global-state';

/**
 * Guard violation error
 */
export class GuardViolationError extends Error {
  constructor(
    message: string,
    public readonly guardName: string,
    public readonly currentState: Partial<GlobalState>
  ) {
    super(message);
    this.name = 'GuardViolationError';
    Object.setPrototypeOf(this, GuardViolationError.prototype);
  }
}

/**
 * Check if baseline exists before timeline generation
 * 
 * Rule: No timeline generation without baseline
 * 
 * @param state - Global state from store
 * @throws GuardViolationError if baseline does not exist
 */
export function guardTimelineGenerationRequiresBaseline(state: GlobalState): void {
  if (state.baselineStatus !== 'EXISTS') {
    throw new GuardViolationError(
      'Cannot generate timeline: Baseline is required. Please create a baseline first.',
      'guardTimelineGenerationRequiresBaseline',
      { baselineStatus: state.baselineStatus }
    );
  }
}

/**
 * Check if draft timeline exists before commit
 * 
 * Rule: No commit without draft
 * 
 * @param state - Global state from store
 * @throws GuardViolationError if draft timeline does not exist
 */
export function guardCommitRequiresDraft(state: GlobalState): void {
  if (state.timelineStatus !== 'DRAFT') {
    throw new GuardViolationError(
      'Cannot commit timeline: Draft timeline is required. Please generate a draft timeline first.',
      'guardCommitRequiresDraft',
      { timelineStatus: state.timelineStatus }
    );
  }
}

/**
 * Check if committed timeline exists before progress tracking
 * 
 * Rule: No progress without committed timeline
 * 
 * @param state - Global state from store
 * @throws GuardViolationError if committed timeline does not exist
 */
export function guardProgressRequiresCommittedTimeline(state: GlobalState): void {
  if (state.timelineStatus !== 'COMMITTED') {
    throw new GuardViolationError(
      'Cannot track progress: Committed timeline is required. Please commit a timeline first.',
      'guardProgressRequiresCommittedTimeline',
      { timelineStatus: state.timelineStatus }
    );
  }
}

/**
 * Check if committed timeline exists before analytics
 * 
 * Rule: No analytics without committed timeline
 * 
 * @param state - Global state from store
 * @throws GuardViolationError if committed timeline does not exist
 */
export function guardAnalyticsRequiresCommittedTimeline(state: GlobalState): void {
  if (state.timelineStatus !== 'COMMITTED') {
    throw new GuardViolationError(
      'Cannot load analytics: Committed timeline is required. Please commit a timeline first.',
      'guardAnalyticsRequiresCommittedTimeline',
      { timelineStatus: state.timelineStatus }
    );
  }
}

/**
 * React hook to get current state and check guards
 * 
 * Usage:
 * ```tsx
 * const { state, checkGuard } = useStateGuards();
 * 
 * const handleGenerate = () => {
 *   try {
 *     checkGuard(guardTimelineGenerationRequiresBaseline);
 *     // Proceed with generation
 *   } catch (error) {
 *     if (error instanceof GuardViolationError) {
 *       toast.error(error.message);
 *     }
 *   }
 * };
 * ```
 */
export function useStateGuards() {
  const state = useGlobalStateStore();
  
  const checkGuard = (guardFn: (state: GlobalState) => void) => {
    guardFn(state);
  };
  
  return {
    state,
    checkGuard,
  };
}

/**
 * Helper to check multiple guards
 * 
 * @param guards - Array of guard functions
 * @param state - Global state
 * @throws GuardViolationError if any guard fails
 */
export function checkGuards(
  guards: Array<(state: GlobalState) => void>,
  state: GlobalState
): void {
  for (const guard of guards) {
    guard(state);
  }
}
