# Frontend → Backend → Orchestrator Mapping

## Overview

This document maps frontend screens to backend endpoints and validates that all screens go through orchestrators (no bypass).

## Mapping Table

| Frontend Screen | Backend Endpoint | Orchestrator/Service | Method | Validation |
|----------------|------------------|---------------------|--------|------------|
| **Document Upload** | `POST /api/v1/documents/upload` | `DocumentService` | `upload_document()` | ✅ Uses Service |
| **Baseline Creation** | `POST /api/v1/baselines` | `BaselineOrchestrator` | `create()` | ✅ Uses Orchestrator |
| **Timeline Generation** | `POST /api/v1/timelines/draft/generate` | `TimelineOrchestrator` | `generate()` | ✅ Uses Orchestrator |
| **Timeline Commit** | `POST /api/v1/timelines/draft/{id}/commit` | `TimelineOrchestrator` | `commit()` | ✅ Uses Orchestrator |
| **Progress Tracking** | `POST /api/v1/progress/milestones/{id}/complete` | `ProgressService` | `mark_milestone_completed()` | ✅ Uses Service |
| **PhD Doctor Submit** | `POST /api/v1/doctor/submit` | `PhDDoctorOrchestrator` | `submit()` | ✅ Uses Orchestrator |
| **PhD Doctor Save Draft** | `POST /api/v1/doctor/save-draft` | `PhDDoctorOrchestrator` | `save_draft()` | ✅ Uses Orchestrator |
| **Analytics Dashboard** | `GET /api/v1/analytics/summary` | `AnalyticsOrchestrator` | `run()` | ✅ Uses Orchestrator |

## Detailed Mappings

### 1. Document Upload Screen

**Frontend Screen:** Document Upload Page  
**Backend Endpoint:** `POST /api/v1/documents/upload`  
**Orchestrator/Service:** `DocumentService`  
**Method:** `upload_document()`  
**Status:** ✅ Uses Service (not an orchestrator, but follows service pattern)

**Service Flow:**
1. Validates file type (PDF/DOCX)
2. Extracts raw text from document
3. Normalizes text (remove headers, footers, noise)
4. Detects language
5. Generates section_map using headings + heuristics
6. Saves file to storage
7. Persists DocumentArtifact with raw_text, normalized_text, section_map_json
8. Returns document ID

**Notes:**
- Document upload is a simple service operation (no complex orchestration needed)
- Creates `DocumentArtifact` record
- Returns document ID for baseline creation

### 2. Baseline Creation Screen

**Frontend Screen:** Baseline Creation Page  
**Backend Endpoint:** `POST /api/v1/baselines`  
**Orchestrator:** `BaselineOrchestrator`  
**Method:** `create()`  
**Status:** ✅ Uses Orchestrator

**Orchestrator Flow:**
1. Validates document exists (if provided)
2. Ensures no baseline already exists for user
3. Creates immutable Baseline record
4. Writes DecisionTrace (via BaseOrchestrator)

**Idempotency:** Yes (via `request_id`)

### 3. Timeline Generation Screen

**Frontend Screen:** Draft Timeline Page (Generation)  
**Backend Endpoint:** `POST /api/v1/timelines/draft/generate`  
**Orchestrator:** `TimelineOrchestrator`  
**Method:** `generate()`  
**Status:** ✅ Uses Orchestrator

**Orchestrator Flow:**
1. Validates baseline exists
2. Loads baseline document text
3. Calls `TimelineIntelligenceEngine.detect_stages()`
4. Calls `TimelineIntelligenceEngine.extract_milestones()`
5. Calls `TimelineIntelligenceEngine.estimate_durations()`
6. Calls `TimelineIntelligenceEngine.map_dependencies()`
7. Creates DraftTimeline + stages + milestones
8. Writes DecisionTrace (via BaseOrchestrator)

**Idempotency:** Yes (via `request_id`)

### 4. Timeline Commit Screen

**Frontend Screen:** Draft Timeline Page (Commit)  
**Backend Endpoint:** `POST /api/v1/timelines/draft/{id}/commit`  
**Orchestrator:** `TimelineOrchestrator`  
**Method:** `commit()`  
**Status:** ✅ Uses Orchestrator

**Orchestrator Flow:**
1. Validates draft timeline exists and belongs to user
2. Applies user edits (if any) via `apply_edits()`
3. Creates CommittedTimeline (immutable copy)
4. Copies stages and milestones to committed timeline
5. Marks draft as inactive (`is_active = False`)
6. Writes DecisionTrace (via BaseOrchestrator)

**Idempotency:** Yes (via `request_id`)

### 5. Progress Tracking Screen

**Frontend Screen:** Timeline Progress Page  
**Backend Endpoint:** `POST /api/v1/progress/milestones/{id}/complete`  
**Service:** `ProgressService`  
**Method:** `mark_milestone_completed()`  
**Status:** ✅ Uses Service

**Service Flow:**
1. Validates milestone exists and belongs to committed timeline
2. Validates milestone is not already completed
3. Sets `is_completed = True`
4. Sets `actual_completion_date`
5. Calculates delay (target_date vs actual_date)
6. Creates ProgressEvent (append-only, immutable)
7. Commits to database

**Notes:**
- ProgressService is a service (not orchestrator) because it's a simple, deterministic operation
- No complex orchestration needed
- Still follows service pattern (no direct database access from endpoints)

### 6. PhD Doctor Submit Screen

**Frontend Screen:** Assessment Page (Submit)  
**Backend Endpoint:** `POST /api/v1/doctor/submit`  
**Orchestrator:** `PhDDoctorOrchestrator`  
**Method:** `submit()`  
**Status:** ✅ Uses Orchestrator

**Orchestrator Flow:**
1. Validates submission completeness
2. Calls `JourneyHealthEngine.assess_health()` with responses
3. Receives `JourneyHealthReport` with scores and recommendations
4. Creates JourneyAssessment record
5. Marks QuestionnaireDraft as submitted (if draft_id provided)
6. Writes DecisionTrace (via BaseOrchestrator)

**Idempotency:** Yes (via `request_id`)

**Isolation:**
- No timeline access
- No document access
- Questionnaire-only

### 7. PhD Doctor Save Draft Screen

**Frontend Screen:** Assessment Page (Auto-save)  
**Backend Endpoint:** `POST /api/v1/doctor/save-draft`  
**Orchestrator:** `PhDDoctorOrchestrator`  
**Method:** `save_draft()`  
**Status:** ✅ Uses Orchestrator

**Orchestrator Flow:**
1. Validates questionnaire version exists
2. Creates or updates QuestionnaireDraft
3. Calculates progress percentage
4. Writes DecisionTrace (via BaseOrchestrator)

**Idempotency:** Yes (via `request_id`)

### 8. Analytics Dashboard Screen

**Frontend Screen:** Dashboard Page  
**Backend Endpoint:** `GET /api/v1/analytics/summary`  
**Orchestrator:** `AnalyticsOrchestrator`  
**Method:** `run()`  
**Status:** ✅ Uses Orchestrator

**Orchestrator Flow:**
1. Endpoint validates committed timeline exists (minimal DB query for validation)
2. Calls `AnalyticsOrchestrator.run()` which:
   - Loads longitudinal data (CommittedTimeline, ProgressEvents, JourneyAssessment)
   - Calls `AnalyticsEngine.aggregate()`
   - Creates AnalyticsSnapshot (immutable)
   - Returns dashboard-ready JSON
   - Writes DecisionTrace (via BaseOrchestrator)

**Idempotency:** Yes (cached by timeline version)

**Read-Only Contract:**
- Only READS from: CommittedTimeline, ProgressEvent, JourneyAssessment
- Only WRITES to: AnalyticsSnapshot, DecisionTrace/EvidenceBundle
- NO mutations to upstream state

**Note:** Endpoint performs minimal database query for timeline validation before calling orchestrator. All business logic goes through orchestrator.

## Validation: No Screen Bypasses Orchestrator

### ✅ All Screens Use Orchestrators/Services

| Screen | Endpoint | Uses Orchestrator/Service | Status |
|--------|----------|---------------------------|--------|
| Document Upload | `POST /api/v1/documents/upload` | `DocumentService` | ✅ |
| Baseline Creation | `POST /api/v1/baselines` | `BaselineOrchestrator` | ✅ |
| Timeline Generation | `POST /api/v1/timelines/draft/generate` | `TimelineOrchestrator` | ✅ |
| Timeline Commit | `POST /api/v1/timelines/draft/{id}/commit` | `TimelineOrchestrator` | ✅ |
| Progress Tracking | `POST /api/v1/progress/milestones/{id}/complete` | `ProgressService` | ✅ |
| PhD Doctor Submit | `POST /api/v1/doctor/submit` | `PhDDoctorOrchestrator` | ✅ |
| PhD Doctor Save Draft | `POST /api/v1/doctor/save-draft` | `PhDDoctorOrchestrator` | ✅ |
| Analytics Dashboard | `GET /api/v1/analytics/summary` | `AnalyticsOrchestrator` | ✅ |

### ✅ No Direct Database Access for Business Logic

All endpoints go through:
- **Orchestrators** (for complex operations with idempotency, tracing, validation)
- **Services** (for simple, deterministic operations)

**Note:** Some endpoints perform minimal database queries for validation/lookup (e.g., checking if timeline exists) before calling orchestrators. All business logic goes through orchestrators/services.

### ✅ All Operations Are Traced

All orchestrators extend `BaseOrchestrator`, which automatically:
- Writes DecisionTrace for audit trail
- Provides idempotency via `request_id`
- Bundles evidence for explainability

## Architecture Benefits

1. **Consistency:** All operations follow the same pattern
2. **Auditability:** All operations are traced via DecisionTrace
3. **Idempotency:** All operations are idempotent via `request_id`
4. **Validation:** All operations validate prerequisites
5. **Isolation:** Operations are isolated (e.g., PhD Doctor doesn't access timeline)

## Notes

- **DocumentService** is a service (not orchestrator) because document upload is a simple operation
- **ProgressService** is a service (not orchestrator) because progress tracking is deterministic and simple
- All other operations use orchestrators for complex coordination, idempotency, and tracing

## Frontend Integration

Frontend screens should:
1. Call the mapped backend endpoint
2. Update global state store after successful API response
3. Display backend-provided data (no frontend calculations)
4. Handle backend error messages (no frontend guessing)

Example:
```typescript
// Frontend: Timeline Generation
const response = await post('/api/v1/timelines/draft/generate', {
  request_id: crypto.randomUUID(),
  baseline_id: baselineId,
  user_id: userId,
  title: 'My Timeline'
});

// Update global state
if (response.data) {
  setTimelineStatus('DRAFT');
}
```
