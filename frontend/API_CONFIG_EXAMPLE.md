# API Configuration - Quick Examples

## 1. Basic Configuration Access

```typescript
// src/config/env.ts is automatically loaded
import { env } from '@/config';

console.log(env.apiBaseUrl);        // http://localhost:8000
console.log(env.apiTimeout);       // 30000
console.log(env.isDevelopment);    // true (in dev mode)
```

## 2. Using API Endpoints in Services

```typescript
// src/services/assessment.service.ts
import { api } from '@/api';
import { ENDPOINTS } from '@/api/endpoints';

export const assessmentService = {
  // ✅ Correct: Use centralized endpoint
  getLatest: async () => {
    return api.get(ENDPOINTS.ASSESSMENTS.GET_LATEST);
  },

  // ✅ Correct: Use endpoint builder
  getById: async (id: string) => {
    return api.get(ENDPOINTS.ASSESSMENTS.GET_BY_ID(id));
  },

  // ✅ Correct: POST with data
  submit: async (data: SubmitRequest) => {
    return api.post(ENDPOINTS.ASSESSMENTS.SUBMIT, data);
  },
};
```

## 3. Using in State Management

```typescript
// state/slices/assessment.slice.ts
import { create } from 'zustand';
import { assessmentService } from '@/services/assessment.service';

export const useAssessmentStore = create((set) => ({
  data: null,
  loading: false,
  error: null,

  fetchLatest: async () => {
    set({ loading: true, error: null });
    try {
      // Service uses ENDPOINTS internally - no hardcoded URLs!
      const data = await assessmentService.getLatest();
      set({ data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
}));
```

## 4. Using in Components (via State)

```typescript
// components/AssessmentView.tsx
import { useAssessmentState } from '@/state/hooks/useAssessment';

export const AssessmentView = () => {
  const { data, loading, fetchLatest } = useAssessmentState();

  useEffect(() => {
    fetchLatest(); // Uses state → service → API (all configured!)
  }, [fetchLatest]);

  if (loading) return <Spinner />;
  return <div>{/* render data */}</div>;
};
```

## 5. Environment Setup

### Create `.env` file:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_ENABLE_DEBUG=true
```

### Different environments:
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000

# .env.production
VITE_API_BASE_URL=https://api.yourdomain.com
```

## 6. Complete Flow Example

```
Component
  ↓ uses
State Hook (useAssessmentState)
  ↓ uses
State Store (useAssessmentStore)
  ↓ uses
Service (assessmentService.getLatest)
  ↓ uses
API Client (api.get)
  ↓ uses
Endpoint (ENDPOINTS.ASSESSMENTS.GET_LATEST)
  ↓ uses
Config (env.apiBaseUrl)
  ↓ uses
Environment Variable (VITE_API_BASE_URL)
```

## Key Points

✅ **Single Source of Truth**: `src/config/env.ts`  
✅ **Centralized Endpoints**: `src/api/endpoints.ts`  
✅ **No Hardcoded URLs**: All URLs come from environment variables  
✅ **Type Safe**: Full TypeScript support  
✅ **Environment Aware**: Different configs for dev/prod/staging
