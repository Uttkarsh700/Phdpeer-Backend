# Frontend Logic Removal - Complete

## Summary

Removed all frontend logic that:
- Infers system state
- Computes progress
- Decides what should happen next

Replaced with backend-driven state checks using global state store.

## Changes Made

### 1. WellBeingCheckIn.tsx

**Removed:**
- Mock milestone completion data (hardcoded `75%`)
- Mock delay calculations (hardcoded `12 days`)
- Mock supervisor response time (hardcoded `3 days`)
- Mock meeting cadence (hardcoded `14 days`)
- Mock opportunities added (hardcoded `8`)

**Replaced with:**
- TODO comments indicating backend data should come from `AnalyticsSummary`
- Placeholder values set to `0` until backend integration
- Comments explaining backend should provide all data

### 2. SignalsTab.tsx

**Removed:**
- Frontend decision-making: `autoData.milestoneCompletion >= 70 ? "Resource" : "Demand"`
- Frontend decision-making: `autoData.avgDelay <= 7 ? "Resource" : "Demand"`
- Frontend decision-making: `autoData.supervisorResponseTime <= 3 ? "Resource" : "Demand"`
- Frontend decision-making: `meetingCadence <= 14 ? "Resource" : "Demand"`
- Frontend decision-making: `opportunitiesAdded >= 5 ? "Resource" : "Demand"`

**Replaced with:**
- TODO comments indicating status should come from backend
- Placeholder badges with "Status" text
- Comments explaining backend should provide status indicators

### 3. RecommendationsTab.tsx

**Removed:**
- Frontend decision-making: `if (rci < 60)` - determines recommendations based on score
- Frontend decision-making: `else if (rci >= 60 && rci < 80)` - determines recommendations
- Frontend decision-making: `else` - determines recommendations for high scores
- All hardcoded action lists based on RCI thresholds

**Replaced with:**
- TODO comments indicating recommendations should come from `JourneyAssessment`
- Empty recommendations function that returns placeholder data
- Comments explaining backend should provide all recommendations

## Backend-Driven State Checks

All state checks now use the global state store:

```typescript
import { useGlobalStateStore } from '@/store';

// Check baseline status (backend-driven)
const baselineStatus = useGlobalStateStore((state) => state.baselineStatus);
const hasBaseline = baselineStatus === 'EXISTS'; // Backend-driven, not computed

// Check timeline status (backend-driven)
const timelineStatus = useGlobalStateStore((state) => state.timelineStatus);
const canGenerateTimeline = baselineStatus === 'EXISTS' && timelineStatus === 'NONE';
const canCommitTimeline = timelineStatus === 'DRAFT';

// Check analytics availability (backend-driven)
const analyticsStatus = useGlobalStateStore((state) => state.analyticsStatus);
const canViewAnalytics = analyticsStatus === 'AVAILABLE';
```

## Progress Data

All progress data must come from backend:

```typescript
// From AnalyticsSummary (backend-provided)
const analyticsSummary = await get<AnalyticsSummary>('/analytics/summary');
const progress = analyticsSummary.milestone_completion_percentage; // Backend-calculated
const completed = analyticsSummary.completed_milestones; // Backend-provided
const total = analyticsSummary.total_milestones; // Backend-provided
```

## Recommendations

All recommendations must come from backend:

```typescript
// From JourneyAssessment (backend-provided)
const assessment = await get<JourneyAssessment>('/doctor/latest');
const recommendations = assessment.action_items; // Backend-generated
const strengths = assessment.strengths; // Backend-provided
const challenges = assessment.challenges; // Backend-provided
```

## Status Indicators

All status indicators must come from backend:

```typescript
// From AnalyticsSummary (backend-provided)
const analyticsSummary = await get<AnalyticsSummary>('/analytics/summary');
// Backend should provide status indicators, not frontend thresholds
```

## Rules Enforced

1. ✅ **No frontend state inference** - Use global state store only
2. ✅ **No frontend progress calculations** - Use backend-provided progress
3. ✅ **No frontend decision-making** - Use backend-provided recommendations
4. ✅ **No frontend thresholds** - Backend provides status indicators
5. ✅ **Backend is source of truth** - All state comes from backend responses

## Next Steps

When integrating with backend:

1. Replace mock data in `WellBeingCheckIn.tsx` with `AnalyticsSummary` data
2. Replace status badges in `SignalsTab.tsx` with backend-provided status indicators
3. Replace recommendations function in `RecommendationsTab.tsx` with `JourneyAssessment.action_items`
4. Use global state store for all state checks
5. Remove all TODO comments once backend integration is complete
