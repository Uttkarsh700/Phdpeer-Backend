/**
 * Global Frontend State Types
 * 
 * This module defines the global state model that mirrors backend state.
 * 
 * IMPORTANT PRINCIPLES:
 * - Backend is source of truth: All state fields reflect actual backend data
 * - No computed fields: Only store what comes from backend API responses
 * - No derived flags: Do not compute status from other fields
 * - Direct mapping: Each field maps directly to backend model/response
 */

/**
 * Baseline Status
 * 
 * Represents whether a user has a baseline record in the backend.
 * 
 * Why this exists:
 * - Backend stores Baseline records in the `baselines` table
 * - Frontend needs to know if user can create timelines (requires baseline)
 * - Determines which UI flows are available (baseline creation vs timeline creation)
 * 
 * Backend source: backend/app/models/baseline.py::Baseline
 * - If user has >= 1 Baseline record: EXISTS
 * - If user has 0 Baseline records: NONE
 * 
 * Note: Backend doesn't have a "status" field - this is derived from existence.
 * However, we store it as state to avoid repeated API calls to check existence.
 */
export type BaselineStatus = 'NONE' | 'EXISTS';

/**
 * Timeline Status
 * 
 * Represents the current timeline state for a user.
 * 
 * Why this exists:
 * - Backend has two separate models: DraftTimeline and CommittedTimeline
 * - Frontend needs to know which timeline type exists to show correct UI
 * - Determines workflow: can create draft, can commit draft, can view committed
 * - Backend invariant: CommittedTimeline requires DraftTimeline (but they're separate records)
 * 
 * Backend sources:
 * - backend/app/models/draft_timeline.py::DraftTimeline (is_active field)
 * - backend/app/models/committed_timeline.py::CommittedTimeline
 * 
 * State values:
 * - NONE: User has no DraftTimeline and no CommittedTimeline
 * - DRAFT: User has >= 1 DraftTimeline (with is_active=true for active draft)
 * - COMMITTED: User has >= 1 CommittedTimeline
 * 
 * Note: User can have both DRAFT and COMMITTED simultaneously (different timelines).
 * This status represents the "current" or "latest" state.
 */
export type TimelineStatus = 'NONE' | 'DRAFT' | 'COMMITTED';

/**
 * Doctor Status (Questionnaire Status)
 * 
 * Represents the questionnaire draft/submission state.
 * 
 * Why this exists:
 * - Backend has QuestionnaireDraft model with is_submitted boolean
 * - Frontend needs to know if user can resume draft or has submitted
 * - Determines UI: show draft resume vs new questionnaire vs results
 * 
 * Backend source: backend/app/models/questionnaire_draft.py::QuestionnaireDraft
 * - is_submitted: boolean field (false = DRAFT, true = SUBMITTED)
 * 
 * State values:
 * - DRAFT: User has >= 1 QuestionnaireDraft with is_submitted=false
 * - SUBMITTED: User has >= 1 QuestionnaireDraft with is_submitted=true
 * 
 * Note: User can have multiple drafts, but this tracks the "active" or "latest" state.
 * When a draft is submitted, is_submitted becomes true and draft becomes immutable.
 */
export type DoctorStatus = 'DRAFT' | 'SUBMITTED';

/**
 * Analytics Status
 * 
 * Represents whether analytics are available for the user's timeline.
 * 
 * Why this exists:
 * - Backend requires CommittedTimeline to generate analytics
 * - Analytics are stored in AnalyticsSnapshot (can be cached)
 * - Frontend needs to know if analytics dashboard can be shown
 * - Determines if analytics API calls will succeed
 * 
 * Backend sources:
 * - backend/app/models/committed_timeline.py::CommittedTimeline (required for analytics)
 * - backend/app/models/analytics_snapshot.py::AnalyticsSnapshot (cached analytics)
 * - backend/app/utils/invariants.py::check_analytics_has_committed_timeline (invariant check)
 * 
 * State values:
 * - AVAILABLE: User has CommittedTimeline (analytics can be generated/retrieved)
 * - UNAVAILABLE: User has no CommittedTimeline (analytics cannot be generated)
 * 
 * Note: Backend invariant enforces "No analytics without committed timeline".
 * This status reflects that invariant - if no committed timeline exists, analytics are unavailable.
 */
export type AnalyticsStatus = 'AVAILABLE' | 'UNAVAILABLE';

/**
 * Global Application State
 * 
 * Mirrors the backend state for the current user.
 * All fields reflect actual backend data - no computed or derived values.
 * 
 * This state is updated when:
 * - User creates/deletes baseline
 * - User creates/commits timeline
 * - User creates/submits questionnaire draft
 * - Analytics are generated/retrieved
 * 
 * State is fetched from backend API endpoints and stored here to avoid
 * repeated API calls and provide single source of truth for UI rendering.
 */
export interface GlobalState {
  /**
   * Baseline existence status
   * 
   * Why: Determines if user can create timelines (baseline required).
   * Backend: Baseline model existence check
   */
  baselineStatus: BaselineStatus;

  /**
   * Timeline state
   * 
   * Why: Determines which timeline UI to show (draft editor vs committed viewer).
   * Backend: DraftTimeline and CommittedTimeline model existence
   */
  timelineStatus: TimelineStatus;

  /**
   * Questionnaire/Doctor status
   * 
   * Why: Determines if user can resume draft or view submitted assessment.
   * Backend: QuestionnaireDraft.is_submitted field
   */
  doctorStatus: DoctorStatus;

  /**
   * Analytics availability
   * 
   * Why: Determines if analytics dashboard can be shown.
   * Backend: CommittedTimeline existence (required for analytics)
   */
  analyticsStatus: AnalyticsStatus;
}

/**
 * Initial global state (before any backend data is loaded)
 */
export const initialGlobalState: GlobalState = {
  baselineStatus: 'NONE',
  timelineStatus: 'NONE',
  doctorStatus: 'DRAFT', // Default to DRAFT (user can start questionnaire)
  analyticsStatus: 'UNAVAILABLE',
};
