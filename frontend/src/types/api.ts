/**
 * API type definitions
 * 
 * Defines types for API requests and responses.
 */

// Common API response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

// Pagination
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// User types
export interface User {
  id: string;
  email: string;
  fullName: string;
  institution?: string;
  fieldOfStudy?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Document types
export interface DocumentArtifact {
  id: string;
  userId: string;
  title: string;
  description?: string;
  fileType: string;
  filePath: string;
  fileSizeBytes: number;
  documentType?: string;
  createdAt: string;
  updatedAt: string;
}

// Baseline types
/**
 * Baseline response from backend API.
 * 
 * Source: backend/app/schemas/baseline.py::BaselineResponse
 * Model: backend/app/models/baseline.py::Baseline
 * 
 * Note: Field names match backend snake_case exactly as returned by FastAPI.
 */
export interface Baseline {
  id: string;
  user_id: string;
  document_artifact_id: string | null;
  program_name: string;
  institution: string;
  field_of_study: string;
  start_date: string; // ISO date string (YYYY-MM-DD)
  expected_end_date: string | null; // ISO date string (YYYY-MM-DD) or null
  total_duration_months: number | null;
  requirements_summary: string | null;
  research_area: string | null;
  advisor_info: string | null;
  funding_status: string | null;
  notes: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

// Timeline types
/**
 * DraftTimeline response from backend API.
 * 
 * Source: backend/app/models/draft_timeline.py::DraftTimeline
 * 
 * Note: Field names match backend snake_case exactly as returned by FastAPI.
 */
export interface DraftTimeline {
  id: string;
  user_id: string;
  baseline_id: string;
  title: string;
  description: string | null;
  version_number: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

/**
 * CommittedTimeline response from backend API.
 * 
 * Source: backend/app/models/committed_timeline.py::CommittedTimeline
 * 
 * Note: Field names match backend snake_case exactly as returned by FastAPI.
 */
export interface CommittedTimeline {
  id: string;
  user_id: string;
  baseline_id: string | null;
  draft_timeline_id: string | null;
  title: string;
  description: string | null;
  committed_date: string; // ISO date string (YYYY-MM-DD)
  target_completion_date: string | null; // ISO date string (YYYY-MM-DD) or null
  notes: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface TimelineStage {
  id: string;
  draftTimelineId?: string;
  committedTimelineId?: string;
  title: string;
  description?: string;
  stageOrder: number;
  startDate?: string;
  endDate?: string;
  durationMonths?: number;
  status: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TimelineMilestone {
  id: string;
  timelineStageId: string;
  title: string;
  description?: string;
  milestoneOrder: number;
  targetDate?: string;
  actualCompletionDate?: string;
  isCompleted: boolean;
  isCritical: boolean;
  deliverableType?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// Progress types
/**
 * ProgressEvent response from backend API.
 * 
 * Source: backend/app/models/progress_event.py::ProgressEvent
 * 
 * Note: Field names match backend snake_case exactly as returned by FastAPI.
 */
export interface ProgressEvent {
  id: string;
  user_id: string;
  milestone_id: string | null;
  event_type: string;
  title: string;
  description: string | null;
  event_date: string; // ISO date string (YYYY-MM-DD)
  impact_level: string | null;
  tags: string | null;
  notes: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

// Assessment types
/**
 * JourneyAssessment response from backend API.
 * 
 * Source: backend/app/models/journey_assessment.py::JourneyAssessment
 * 
 * Note: Field names match backend snake_case exactly as returned by FastAPI.
 */
export interface JourneyAssessment {
  id: string;
  user_id: string;
  assessment_date: string; // ISO date string (YYYY-MM-DD)
  assessment_type: string;
  overall_progress_rating: number | null; // Integer 1-10 or null
  research_quality_rating: number | null; // Integer 1-10 or null
  timeline_adherence_rating: number | null; // Integer 1-10 or null
  strengths: string | null;
  challenges: string | null;
  action_items: string | null;
  advisor_feedback: string | null;
  notes: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface AssessmentSummary {
  assessmentId: string;
  overallScore: number;
  overallStatus: 'excellent' | 'good' | 'fair' | 'concerning' | 'critical';
  assessmentDate: string;
  totalResponses: number;
  dimensions: Record<string, {
    score: number;
    status: string;
    strengths: string[];
    concerns: string[];
  }>;
  criticalAreas: Array<{
    dimension: string;
    score: number;
    concerns: string[];
  }>;
  healthyAreas: Array<{
    dimension: string;
    score: number;
    strengths: string[];
  }>;
  recommendations: Array<{
    priority: 'high' | 'medium' | 'low';
    title: string;
    description: string;
    dimension: string;
    actionItems: string[];
  }>;
  summary: string;
}

/**
 * AnalyticsSummary response from backend API.
 * 
 * Source: backend/app/services/analytics_engine.py::AnalyticsSummary
 * Response format: backend/app/orchestrators/analytics_orchestrator.py::_build_dashboard_json_from_summary
 * 
 * Note: Field names match backend snake_case exactly as returned by FastAPI.
 * This is the structure returned from /api/v1/analytics/summary endpoint.
 */
export interface AnalyticsSummary {
  snapshot_id: string;
  generated_at: string; // ISO datetime string
  user_id: string;
  timeline_id: string;
  timeline_status: string; // "on_track" | "delayed" | "completed"
  milestones: {
    completion_percentage: number; // float 0-100
    total: number;
    completed: number;
    pending: number;
  };
  delays: {
    total_delays: number;
    overdue_milestones: number;
    overdue_critical_milestones: number;
    average_delay_days: number; // float
    max_delay_days: number;
  };
  journey_health: {
    latest_score: number | null; // float 0-100 or null
    dimensions: Record<string, number>; // dimension_name -> score (0-100)
  };
  longitudinal_summary: {
    timeline_committed_date: string | null; // ISO date string or null
    target_completion_date: string | null; // ISO date string or null
    timeline_duration_days: number | null;
    elapsed_days: number | null;
    duration_progress_percentage: number | null; // float 0-100 or null
    total_progress_events: number;
    event_counts_by_type: Record<string, number>;
    first_milestone_completion_date: string | null; // ISO date string or null
    last_milestone_completion_date: string | null; // ISO date string or null
    latest_assessment: {
      assessment_date: string; // ISO date string
      assessment_type: string;
      overall_rating: number | null; // Integer 1-10 or null
    } | null;
  };
}

// Request types
export interface CreateBaselineRequest {
  documentId?: string;
  programName: string;
  institution: string;
  fieldOfStudy: string;
  startDate: string;
  expectedEndDate?: string;
  totalDurationMonths?: number;
  requirementsSummary?: string;
  researchArea?: string;
  advisorInfo?: string;
  fundingStatus?: string;
  notes?: string;
}

export interface CreateTimelineRequest {
  baselineId: string;
  title?: string;
  description?: string;
  versionNumber?: string;
}

export interface CommitTimelineRequest {
  draftTimelineId: string;
  title?: string;
  description?: string;
  requestId?: string; // Optional idempotency key
}

export interface QuestionnaireResponse {
  dimension: string;
  questionId: string;
  responseValue: number;
  questionText?: string;
}

export interface SubmitQuestionnaireRequest {
  responses: QuestionnaireResponse[];
  assessmentType?: string;
  notes?: string;
}

// Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}
