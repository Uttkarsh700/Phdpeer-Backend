/**
 * Global State Store
 * 
 * Lightweight Zustand store for global application state.
 * 
 * RULES:
 * - State updates ONLY from API responses
 * - No computed intelligence
 * - Easy reset on reload
 * 
 * This store mirrors backend state exactly - no derived or computed values.
 */

import { create } from 'zustand';
import type { GlobalState, BaselineStatus, TimelineStatus, DoctorStatus, AnalyticsStatus } from '../types';
import { initialGlobalState } from '../types';

/**
 * Global State Store Interface
 * 
 * Contains:
 * - State: Current global state
 * - Actions: Methods to update state from API responses
 * - Reset: Method to reset state to initial values
 */
interface GlobalStateStore extends GlobalState {
  // Actions - Update state from API responses only
  
  /**
   * Update baseline status from API response
   * 
   * Call this after:
   * - GET /api/v1/baselines (check if array has items)
   * - POST /api/v1/baselines (created baseline)
   * - DELETE /api/v1/baselines/:id (deleted baseline)
   */
  setBaselineStatus: (status: BaselineStatus) => void;

  /**
   * Update timeline status from API response
   * 
   * Call this after:
   * - GET /api/v1/timelines/draft (check if draft exists)
   * - GET /api/v1/timelines/committed (check if committed exists)
   * - POST /api/v1/timelines/draft (created draft)
   * - POST /api/v1/timelines/commit (committed timeline)
   * - DELETE /api/v1/timelines/:id (deleted timeline)
   */
  setTimelineStatus: (status: TimelineStatus) => void;

  /**
   * Update doctor/questionnaire status from API response
   * 
   * Call this after:
   * - GET /api/v1/questionnaire/draft (check is_submitted field)
   * - POST /api/v1/assessments/submit (submitted questionnaire)
   */
  setDoctorStatus: (status: DoctorStatus) => void;

  /**
   * Update analytics status from API response
   * 
   * Call this after:
   * - GET /api/v1/analytics/summary (check if committed timeline exists)
   * - POST /api/v1/timelines/commit (committed timeline makes analytics available)
   */
  setAnalyticsStatus: (status: AnalyticsStatus) => void;

  /**
   * Update entire state from API response
   * 
   * Useful when fetching all state at once (e.g., on login or app load)
   */
  setState: (state: Partial<GlobalState>) => void;

  /**
   * Reset state to initial values
   * 
   * Call this on:
   * - User logout
   * - App reload
   * - Error recovery
   */
  reset: () => void;
}

/**
 * Global State Store
 * 
 * Lightweight Zustand store with no middleware or persistence.
 * State is ephemeral and resets on page reload.
 */
export const useGlobalStateStore = create<GlobalStateStore>((set) => ({
  // Initial state
  ...initialGlobalState,

  // Actions - Update state from API responses
  
  setBaselineStatus: (status: BaselineStatus) => {
    set({ baselineStatus: status });
  },

  setTimelineStatus: (status: TimelineStatus) => {
    set({ timelineStatus: status });
  },

  setDoctorStatus: (status: DoctorStatus) => {
    set({ doctorStatus: status });
  },

  setAnalyticsStatus: (status: AnalyticsStatus) => {
    set({ analyticsStatus: status });
  },

  setState: (state: Partial<GlobalState>) => {
    set((current) => ({ ...current, ...state }));
  },

  reset: () => {
    set(initialGlobalState);
  },
}));

/**
 * Selector hooks for optimized re-renders
 * 
 * Use these instead of accessing the store directly to avoid
 * unnecessary re-renders when unrelated state changes.
 */

export const useBaselineStatus = () => useGlobalStateStore((state) => state.baselineStatus);
export const useTimelineStatus = () => useGlobalStateStore((state) => state.timelineStatus);
export const useDoctorStatus = () => useGlobalStateStore((state) => state.doctorStatus);
export const useAnalyticsStatus = () => useGlobalStateStore((state) => state.analyticsStatus);

/**
 * Action hooks for updating state
 */
export const useGlobalStateActions = () => useGlobalStateStore((state) => ({
  setBaselineStatus: state.setBaselineStatus,
  setTimelineStatus: state.setTimelineStatus,
  setDoctorStatus: state.setDoctorStatus,
  setAnalyticsStatus: state.setAnalyticsStatus,
  setState: state.setState,
  reset: state.reset,
}));
