# State-to-Screen Mapping - Quick Reference

## Import

```typescript
import { getScreenFromState, getRouteFromState } from '@/state/navigation';
```

## Basic Usage

```typescript
const state = useGlobalStateStore();
const route = getRouteFromState(state);
navigate(route);
```

## Mapping Rules

| State Condition | Screen | Route |
|----------------|--------|-------|
| No baseline | `upload` | `/documents/upload` |
| Baseline exists | `timeline-generation` | `/timelines` |
| Draft timeline | `draft-timeline` | `/timelines` |
| Committed timeline | `progress-tracking` | `/progress` |
| Doctor submitted | `health-summary` | `/health` |
| Analytics available | `dashboard` | `/dashboard` |

## Priority Order

1. Dashboard (analytics available)
2. Health Summary (doctor submitted)
3. Progress Tracking (committed timeline)
4. Draft Timeline (draft timeline)
5. Timeline Generation (baseline exists)
6. Upload (no baseline)

## Example

```typescript
// Get route from state
const route = getRouteFromState(state);

// Navigate
navigate(route);

// Or get screen type
const screen = getScreenFromState(state);
```
