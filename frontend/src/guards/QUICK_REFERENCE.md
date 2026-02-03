# Route Guards - Quick Reference

## Import

```typescript
import { RouteGuard, isRouteValidForState, getRouteFromState } from '@/guards';
```

## Basic Usage

```typescript
// Wrap route with guard
<RouteGuard>
  <DashboardPage />
</RouteGuard>
```

## Check Route Validity

```typescript
const isValid = isRouteValidForState('/dashboard', state);
if (!isValid) {
  // Redirect to valid route
  navigate(getRouteFromState(state));
}
```

## Route Validation Rules

| Route | Requires |
|-------|----------|
| `/documents/upload` | No baseline |
| `/timelines` | Baseline exists |
| `/progress` | Committed timeline |
| `/health` | Doctor submitted |
| `/dashboard` | Analytics available |

## Router Integration

```typescript
{
  path: '/',
  element: (
    <RouteGuard>
      <App />
    </RouteGuard>
  ),
}
```
