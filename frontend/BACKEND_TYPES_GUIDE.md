# Backend Response Types Guide

## Overview

This document describes the TypeScript interfaces for backend API responses. **All interfaces match the backend exactly** - field names use `snake_case` as returned by FastAPI, and no fields are inferred or computed.

## Key Principles

1. ✅ **Backend is source of truth** - Interfaces match backend models/schemas exactly
2. ✅ **No field inference** - Only fields that exist in backend responses
3. ✅ **No computed fields** - All fields come directly from backend
4. ✅ **Snake_case naming** - Matches FastAPI response format
5. ✅ **Null handling** - Optional fields use `| null` to match backend

## Interfaces

### Baseline

**Source:** `backend/app/schemas/baseline.py::BaselineResponse`  
**Model:** `backend/app/models/baseline.py::Baseline`

```typescript
interface Baseline {
  id: string;
  user_id: string;
  document_artifact_id: string | null;
  program_name: string;
  institution: string;
  field_of_study: string;
  start_date: string; // ISO date (YYYY-MM-DD)
  expected_end_date: string | null;
  total_duration_months: number | null;
  requirements_summary: string | null;
  research_area: string | null;
  advisor_info: string | null;
  funding_status: string | null;
  notes: string | null;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

### DraftTimeline

**Source:** `backend/app/models/draft_timeline.py::DraftTimeline`

```typescript
interface DraftTimeline {
  id: string;
  user_id: string;
  baseline_id: string;
  title: string;
  description: string | null;
  version_number: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

### CommittedTimeline

**Source:** `backend/app/models/committed_timeline.py::CommittedTimeline`

```typescript
interface CommittedTimeline {
  id: string;
  user_id: string;
  baseline_id: string | null;
  draft_timeline_id: string | null;
  title: string;
  description: string | null;
  committed_date: string; // ISO date (YYYY-MM-DD)
  target_completion_date: string | null;
  notes: string | null;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

### ProgressEvent

**Source:** `backend/app/models/progress_event.py::ProgressEvent`

```typescript
interface ProgressEvent {
  id: string;
  user_id: string;
  milestone_id: string | null;
  event_type: string;
  title: string;
  description: string | null;
  event_date: string; // ISO date (YYYY-MM-DD)
  impact_level: string | null;
  tags: string | null;
  notes: string | null;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

### JourneyAssessment

**Source:** `backend/app/models/journey_assessment.py::JourneyAssessment`

```typescript
interface JourneyAssessment {
  id: string;
  user_id: string;
  assessment_date: string; // ISO date (YYYY-MM-DD)
  assessment_type: string;
  overall_progress_rating: number | null; // 1-10
  research_quality_rating: number | null; // 1-10
  timeline_adherence_rating: number | null; // 1-10
  strengths: string | null;
  challenges: string | null;
  action_items: string | null;
  advisor_feedback: string | null;
  notes: string | null;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

### AnalyticsSummary

**Source:** `backend/app/services/analytics_engine.py::AnalyticsSummary`  
**Response Format:** `backend/app/orchestrators/analytics_orchestrator.py::_build_dashboard_json_from_summary`

```typescript
interface AnalyticsSummary {
  snapshot_id: string;
  generated_at: string; // ISO datetime
  user_id: string;
  timeline_id: string;
  timeline_status: string; // "on_track" | "delayed" | "completed"
  milestones: {
    completion_percentage: number; // 0-100
    total: number;
    completed: number;
    pending: number;
  };
  delays: {
    total_delays: number;
    overdue_milestones: number;
    overdue_critical_milestones: number;
    average_delay_days: number;
    max_delay_days: number;
  };
  journey_health: {
    latest_score: number | null; // 0-100
    dimensions: Record<string, number>; // dimension_name -> score (0-100)
  };
  longitudinal_summary: {
    timeline_committed_date: string | null;
    target_completion_date: string | null;
    timeline_duration_days: number | null;
    elapsed_days: number | null;
    duration_progress_percentage: number | null; // 0-100
    total_progress_events: number;
    event_counts_by_type: Record<string, number>;
    first_milestone_completion_date: string | null;
    last_milestone_completion_date: string | null;
    latest_assessment: {
      assessment_date: string;
      assessment_type: string;
      overall_rating: number | null;
    } | null;
  };
}
```

## Usage

### Import Types

```typescript
import type {
  Baseline,
  DraftTimeline,
  CommittedTimeline,
  ProgressEvent,
  JourneyAssessment,
  AnalyticsSummary,
} from '@/types/api';
```

### Type API Responses

```typescript
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';

// GET request with typed response
const baseline: Baseline = await apiClient.get<Baseline>(
  ENDPOINTS.BASELINES.GET_BY_ID(id)
);

// Array response
const timelines: CommittedTimeline[] = await apiClient.get<CommittedTimeline[]>(
  ENDPOINTS.TIMELINES.LIST
);
```

### Handle Nullable Fields

```typescript
const baseline: Baseline = await apiClient.get<Baseline>(...);

// Check for null before using
if (baseline.expected_end_date) {
  const endDate = new Date(baseline.expected_end_date);
}

// Or use optional chaining
const duration = baseline.total_duration_months ?? 0;
```

## Date Handling

All date fields are ISO strings:
- **Date fields** (e.g., `start_date`, `committed_date`): `"YYYY-MM-DD"`
- **Datetime fields** (e.g., `created_at`, `updated_at`): ISO datetime string

```typescript
// Parse dates
const startDate = new Date(baseline.start_date);
const createdAt = new Date(baseline.created_at);
```

## Migration Notes

If you have existing code using camelCase field names, you'll need to update:

```typescript
// ❌ Old (camelCase)
const userId = baseline.userId;
const startDate = baseline.startDate;

// ✅ New (snake_case - matches backend)
const userId = baseline.user_id;
const startDate = baseline.start_date;
```

## Validation

These types represent the **exact structure** returned by the backend. If the backend changes, these interfaces must be updated to match.

**Never:**
- ❌ Add computed/derived fields
- ❌ Change field names to camelCase
- ❌ Infer fields that don't exist in backend
- ❌ Make required fields optional (or vice versa)

**Always:**
- ✅ Match backend field names exactly
- ✅ Use `| null` for nullable fields
- ✅ Use exact types from backend (string, number, boolean)
- ✅ Document source in comments
