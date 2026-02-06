# Backend Types Migration Summary

## Status: ✅ Backend Types Already Defined

The backend contract types are already defined in `frontend/src/api/backend-types.ts` and match the backend models exactly.

## Backend Types Available

All backend types are exported from `frontend/src/api/index.ts`:

- `Baseline` - from `backend/app/models/baseline.py`
- `DraftTimeline` - from `backend/app/models/draft_timeline.py`
- `CommittedTimeline` - from `backend/app/models/committed_timeline.py`
- `ProgressEvent` - from `backend/app/models/progress_event.py`
- `JourneyAssessment` - from `backend/app/models/journey_assessment.py`
- `AnalyticsSummary` - from `backend/app/services/analytics_engine.py`

## Usage

```typescript
import type { 
  Baseline, 
  DraftTimeline, 
  CommittedTimeline, 
  ProgressEvent, 
  JourneyAssessment, 
  AnalyticsSummary 
} from '@/api';
```

## Notes

- All field names match backend exactly (snake_case)
- No derived or computed fields
- All nullable fields properly typed as `| null`
- Dates are ISO date strings (`YYYY-MM-DD`)
- Datetimes are ISO datetime strings
- UUIDs are strings

## Non-Backend Types (UI-Specific)

These are UI-specific types and do NOT need to be replaced:

- `TimelineEvent` in `ResearchTimeline.tsx` - UI display type
- `TimelineEvent` in `TimelineIntegrationModal.tsx` - UI display type
- `WritingBaseline` in `writingEvolutionTypes.ts` - Different feature (writing evolution, not PhD timeline)

These are fine to keep as they are UI-specific and don't duplicate backend models.
