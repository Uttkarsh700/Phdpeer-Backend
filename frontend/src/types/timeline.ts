/**
 * Timeline Generation Types
 * 
 * Types for timeline generation API responses.
 * 
 * Source: backend/app/orchestrators/timeline_orchestrator.py::_build_ui_response
 * 
 * Note: Field names match backend snake_case exactly as returned by FastAPI.
 */

/**
 * Timeline generation response
 * 
 * Complete response from POST /api/v1/timelines/draft/generate
 */
export interface TimelineGenerationResponse {
  timeline: {
    id: string;
    baseline_id: string;
    user_id: string;
    title: string;
    description: string | null;
    version_number: string | null;
    is_active: boolean;
    status: string; // "DRAFT"
    created_at: string; // ISO datetime string
  };
  stages: Array<{
    id: string;
    title: string;
    description: string | null;
    stage_order: number;
    duration_months: number | null;
    status: string;
    milestones: Array<{
      id: string;
      title: string;
      description: string | null;
      milestone_order: number;
      is_critical: boolean;
      is_completed: boolean;
      deliverable_type: string | null;
      target_date: string | null; // ISO date string or null
    }>;
  }>;
  dependencies: Array<{
    dependent_item: string;
    depends_on_item: string;
    dependency_type: string;
    confidence: number;
    reason: string;
  }>;
  durations: Array<{
    item_description: string;
    item_type: string; // "stage" | "milestone"
    duration_months_min: number;
    duration_months_max: number;
    confidence: number;
  }>;
  metadata: {
    total_stages: number;
    total_milestones: number;
    total_duration_months_min: number;
    total_duration_months_max: number;
    is_dag_valid: boolean;
    generated_at: string; // ISO datetime string
  };
}
