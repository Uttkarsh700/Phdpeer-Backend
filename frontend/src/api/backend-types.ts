/**
 * TypeScript interfaces matching backend models exactly.
 * 
 * These interfaces are based on the backend SQLAlchemy models and Pydantic schemas.
 * Field names match the backend exactly (snake_case for database fields).
 * 
 * All models inherit from BaseModel which provides:
 * - id: UUID
 * - created_at: datetime
 * - updated_at: datetime
 */

/**
 * Baseline model - represents initial PhD program assessment.
 * 
 * Source: backend/app/models/baseline.py
 * Schema: backend/app/schemas/baseline.py
 */
export interface Baseline {
  id: string; // UUID
  user_id: string; // UUID
  document_artifact_id: string | null; // UUID, nullable
  program_name: string;
  institution: string;
  field_of_study: string;
  start_date: string; // ISO date string (YYYY-MM-DD)
  expected_end_date: string | null; // ISO date string, nullable
  total_duration_months: number | null; // nullable
  requirements_summary: string | null; // nullable
  research_area: string | null; // nullable
  advisor_info: string | null; // nullable
  funding_status: string | null; // nullable
  notes: string | null; // nullable
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

/**
 * DraftTimeline model - represents a timeline in draft/planning state.
 * 
 * Source: backend/app/models/draft_timeline.py
 */
export interface DraftTimeline {
  id: string; // UUID
  user_id: string; // UUID
  baseline_id: string; // UUID
  title: string;
  description: string | null; // nullable
  version_number: string | null; // nullable
  is_active: boolean;
  notes: string | null; // nullable
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

/**
 * CommittedTimeline model - represents a finalized, committed timeline.
 * 
 * Source: backend/app/models/committed_timeline.py
 */
export interface CommittedTimeline {
  id: string; // UUID
  user_id: string; // UUID
  baseline_id: string | null; // UUID, nullable
  draft_timeline_id: string | null; // UUID, nullable
  title: string;
  description: string | null; // nullable
  committed_date: string; // ISO date string (YYYY-MM-DD)
  target_completion_date: string | null; // ISO date string, nullable
  notes: string | null; // nullable
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

/**
 * ProgressEvent model - tracks progress activities and updates.
 * 
 * Source: backend/app/models/progress_event.py
 */
export interface ProgressEvent {
  id: string; // UUID
  user_id: string; // UUID
  milestone_id: string | null; // UUID, nullable
  event_type: string; // e.g., "milestone_completed", "achievement", "blocker", "update"
  title: string;
  description: string | null; // nullable
  event_date: string; // ISO date string (YYYY-MM-DD)
  impact_level: string | null; // "low", "medium", "high", nullable
  tags: string | null; // comma-separated tags, nullable
  notes: string | null; // nullable
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

/**
 * JourneyAssessment model - periodic assessments of PhD progress.
 * 
 * Source: backend/app/models/journey_assessment.py
 */
export interface JourneyAssessment {
  id: string; // UUID
  user_id: string; // UUID
  assessment_date: string; // ISO date string (YYYY-MM-DD)
  assessment_type: string; // e.g., "self", "advisor", "quarterly"
  overall_progress_rating: number | null; // 1-10, nullable
  research_quality_rating: number | null; // 1-10, nullable
  timeline_adherence_rating: number | null; // 1-10, nullable
  strengths: string | null; // nullable
  challenges: string | null; // nullable
  action_items: string | null; // nullable
  advisor_feedback: string | null; // nullable
  notes: string | null; // nullable
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

/**
 * AnalyticsSummary - structured analytics summary for dashboard.
 * 
 * Source: backend/app/services/analytics_engine.py (AnalyticsSummary dataclass)
 * Response format: backend/app/orchestrators/analytics_orchestrator.py (_persist_snapshot)
 * 
 * This matches the summary_json structure stored in AnalyticsSnapshot.
 */
export interface AnalyticsSummary {
  timeline_id: string; // UUID
  user_id: string; // UUID
  generated_at: string; // ISO date string (YYYY-MM-DD)
  
  // Timeline status
  timeline_status: "on_track" | "delayed" | "completed";
  
  // Milestone metrics
  milestone_completion_percentage: number; // float
  total_milestones: number; // int
  completed_milestones: number; // int
  pending_milestones: number; // int
  
  // Delay metrics
  total_delays: number; // int
  overdue_milestones: number; // int
  overdue_critical_milestones: number; // int
  average_delay_days: number; // float
  max_delay_days: number; // int
  
  // Journey health (from latest assessment)
  latest_health_score: number | null; // 0-100, nullable
  health_dimensions: Record<string, number>; // dimension_name -> score (0-100)
  
  // Longitudinal summary
  longitudinal_summary: Record<string, unknown>; // Dict[str, Any]
}
