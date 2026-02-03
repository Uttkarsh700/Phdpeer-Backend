# API Module

This module provides centralized API endpoint definitions and utilities.

## Usage

### Using Endpoints

```typescript
import { ENDPOINTS } from '@/api/endpoints';
import { api } from '@/api';

// Simple endpoint
const data = await api.get(ENDPOINTS.ASSESSMENTS.GET_LATEST);

// Endpoint with parameter
const assessment = await api.get(ENDPOINTS.ASSESSMENTS.GET_BY_ID('123'));

// POST request
const result = await api.post(ENDPOINTS.ASSESSMENTS.SUBMIT, {
  question1: 'answer1',
});
```

### Getting Full URLs

```typescript
import { getEndpointUrl } from '@/api/endpoints';

const fullUrl = getEndpointUrl(ENDPOINTS.ASSESSMENTS.GET_LATEST);
console.log(fullUrl);
// Output: http://localhost:8000/api/v1/assessments/latest
```

## Adding New Endpoints

When adding new API endpoints, update `endpoints.ts`:

```typescript
export const ENDPOINTS = {
  // ... existing endpoints
  
  MY_NEW_RESOURCE: {
    BASE: endpoint('my-resource'),
    CREATE: endpoint('my-resource'),
    GET_BY_ID: (id: string) => endpoint('my-resource', id),
    UPDATE: (id: string) => endpoint('my-resource', id),
    DELETE: (id: string) => endpoint('my-resource', id),
  },
};
```

Then use in your service:

```typescript
import { ENDPOINTS } from '@/api/endpoints';
import { api } from '@/api';

export const myService = {
  getAll: async () => {
    return api.get(ENDPOINTS.MY_NEW_RESOURCE.BASE);
  },
  
  getById: async (id: string) => {
    return api.get(ENDPOINTS.MY_NEW_RESOURCE.GET_BY_ID(id));
  },
};
```

## Important Rules

1. ✅ **Always use `ENDPOINTS` constants** - Never hardcode API paths
2. ✅ **Keep endpoints centralized** - All endpoints must be in `endpoints.ts`
3. ✅ **Use endpoint builder functions** - For dynamic paths (e.g., `GET_BY_ID(id)`)
4. ❌ **Never hardcode URLs** - Not even in comments or tests
