/**
 * Global Frontend State Store
 * 
 * Mirrors backend state only - no computed flags, no intelligence.
 * State is updated when API calls succeed.
 * 
 * State Structure:
 * - baselineStatus: Status of baseline (NONE | EXISTS)
 * - timelineStatus: Status of timeline (NONE | DRAFT | COMMITTED)
 * - doctorStatus: Status of PhD Doctor assessment (NONE | DRAFT | SUBMITTED)
 * - analyticsStatus: Status of analytics (NONE | AVAILABLE)
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Baseline status - mirrors backend baseline existence
 */
export type BaselineStatus = 'NONE' | 'EXISTS';

/**
 * Timeline status - mirrors backend timeline state
 */
export type TimelineStatus = 'NONE' | 'DRAFT' | 'COMMITTED';

/**
 * Doctor status - mirrors backend PhD Doctor assessment state
 */
export type DoctorStatus = 'NONE' | 'DRAFT' | 'SUBMITTED';

/**
 * Analytics status - mirrors backend analytics availability
 */
export type AnalyticsStatus = 'NONE' | 'AVAILABLE';

/**
 * Global state interface - mirrors backend state only
 */
export interface GlobalState {
  // Baseline status
  baselineStatus: BaselineStatus;
  
  // Timeline status
  timelineStatus: TimelineStatus;
  
  // Doctor status
  doctorStatus: DoctorStatus;
  
  // Analytics status
  analyticsStatus: AnalyticsStatus;
}

/**
 * Global state actions - update state to mirror backend
 */
export interface GlobalStateActions {
  // Update baseline status (called when baseline is created/fetched)
  setBaselineStatus: (status: BaselineStatus) => void;
  
  // Update timeline status (called when timeline is generated/committed)
  setTimelineStatus: (status: TimelineStatus) => void;
  
  // Update doctor status (called when assessment is saved/submitted)
  setDoctorStatus: (status: DoctorStatus) => void;
  
  // Update analytics status (called when analytics become available)
  setAnalyticsStatus: (status: AnalyticsStatus) => void;
  
  // Reset all state (called on logout or state refresh)
  resetState: () => void;
}

/**
 * Initial state - all statuses start as NONE
 */
const initialState: GlobalState = {
  baselineStatus: 'NONE',
  timelineStatus: 'NONE',
  doctorStatus: 'NONE',
  analyticsStatus: 'NONE',
};

/**
 * Global state store using Zustand with persistence
 * 
 * State is persisted to localStorage to survive page refreshes.
 * State is updated when API calls succeed (see update locations below).
 */
export const useGlobalStateStore = create<GlobalState & GlobalStateActions>()(
  persist(
    (set) => ({
      ...initialState,
      
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
      
      resetState: () => {
        set(initialState);
      },
    }),
    {
      name: 'frensei-global-state', // localStorage key
    }
  )
);

/**
 * State Update Locations:
 * 
 * 1. baselineStatus:
 *    - Set to 'EXISTS' when:
 *      - POST /baselines succeeds (baseline created)
 *      - GET /baselines succeeds and returns a baseline
 *    - Set to 'NONE' when:
 *      - User logs out
 *      - State is reset
 * 
 * 2. timelineStatus:
 *    - Set to 'DRAFT' when:
 *      - POST /timelines/draft/generate succeeds (draft created)
 *      - GET /timelines/draft/:id succeeds (draft exists)
 *    - Set to 'COMMITTED' when:
 *      - POST /timelines/draft/:id/commit succeeds (timeline committed)
 *      - GET /timelines/committed/:id succeeds (committed timeline exists)
 *    - Set to 'NONE' when:
 *      - User logs out
 *      - State is reset
 * 
 * 3. doctorStatus:
 *    - Set to 'DRAFT' when:
 *      - POST /doctor/save-draft succeeds (draft saved)
 *      - GET /doctor/draft succeeds (draft exists)
 *    - Set to 'SUBMITTED' when:
 *      - POST /doctor/submit succeeds (assessment submitted)
 *    - Set to 'NONE' when:
 *      - User logs out
 *      - State is reset
 * 
 * 4. analyticsStatus:
 *    - Set to 'AVAILABLE' when:
 *      - Timeline is committed (analytics become available)
 *      - GET /analytics/summary succeeds (analytics exist)
 *    - Set to 'NONE' when:
 *      - User logs out
 *      - State is reset
 *      - Timeline is deleted
 */
