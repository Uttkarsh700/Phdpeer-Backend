# API Configuration Guide

This guide explains how to configure and use the environment-based API access system.

## Overview

The frontend uses a centralized configuration system that:
- ✅ Loads API base URL from environment variables
- ✅ Provides a single source of truth for all configuration
- ✅ Centralizes all API endpoints
- ✅ Prevents hardcoded URLs anywhere in the codebase

## Setup

### 1. Environment Variables

Create a `.env` file in the `frontend/` directory (or copy from `.env.example`):

```bash
# Required: API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Optional: API Configuration
VITE_API_TIMEOUT=30000
VITE_API_VERSION=v1

# Optional: Development Server
VITE_DEV_SERVER_PORT=3000
VITE_DEV_SERVER_PROXY_TARGET=http://localhost:8000

# Optional: Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_ANALYTICS=false
```

### 2. Environment Files by Mode

Vite supports different environment files:
- `.env` - Loaded in all cases
- `.env.local` - Loaded in all cases, ignored by git
- `.env.[mode]` - Only loaded in specified mode (e.g., `.env.development`)
- `.env.[mode].local` - Only loaded in specified mode, ignored by git

**Example: `.env.development`**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
```

**Example: `.env.production`**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
```

## Usage Examples

### 1. Accessing Configuration

```typescript
// Import the config module
import { env } from '@/config';

// Use configuration values
console.log(env.apiBaseUrl);        // http://localhost:8000
console.log(env.apiTimeout);        // 30000
console.log(env.isDevelopment);     // true (in dev mode)
console.log(env.isProduction);      // false (in dev mode)
```

### 2. Using API Endpoints

All API endpoints are centralized in `src/api/endpoints.ts`:

```typescript
// Import endpoints
import { ENDPOINTS } from '@/api/endpoints';
import { api } from '@/api';

// Use in service files
export const assessmentService = {
  getLatest: async () => {
    // ✅ Correct: Use centralized endpoint
    return api.get(ENDPOINTS.ASSESSMENTS.GET_LATEST);
  },

  getById: async (id: string) => {
    // ✅ Correct: Use endpoint builder function
    return api.get(ENDPOINTS.ASSESSMENTS.GET_BY_ID(id));
  },
};

// ❌ WRONG: Never hardcode URLs
// return api.get('/api/v1/assessments/latest'); // DON'T DO THIS!
```

### 3. Using API Client

The API client automatically uses the base URL from configuration:

```typescript
import { api, apiClient } from '@/api';

// Simple GET request
const data = await api.get<MyDataType>(ENDPOINTS.ASSESSMENTS.GET_LATEST);

// POST request with data
const result = await api.post<ResponseType>(
  ENDPOINTS.ASSESSMENTS.SUBMIT,
  { question1: 'answer1' }
);

// PUT request
const updated = await api.put<ResponseType>(
  ENDPOINTS.BASELINES.UPDATE(baselineId),
  { name: 'New Name' }
);

// DELETE request
await api.delete(ENDPOINTS.DOCUMENTS.DELETE(documentId));
```

### 4. Building Full URLs (for debugging)

If you need the full URL for debugging or external tools:

```typescript
import { getEndpointUrl } from '@/api/endpoints';

const fullUrl = getEndpointUrl(ENDPOINTS.ASSESSMENTS.GET_LATEST);
console.log(fullUrl);
// Output: http://localhost:8000/api/v1/assessments/latest
```

### 5. Using in Components (via State Management)

Components should never directly call API services. Instead, use state management:

```typescript
// ❌ WRONG: Direct API call in component
function MyComponent() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // DON'T DO THIS!
    fetch('http://localhost:8000/api/v1/assessments/latest')
      .then(res => res.json())
      .then(setData);
  }, []);
}

// ✅ CORRECT: Use state management
import { useAssessmentState } from '@/state/hooks/useAssessment';

function MyComponent() {
  const { data, loading, fetchLatest } = useAssessmentState();
  
  useEffect(() => {
    fetchLatest();
  }, [fetchLatest]);
  
  return <div>{/* render data */}</div>;
}
```

### 6. State Management Example

State management layer uses API services:

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
      // Service uses ENDPOINTS internally
      const data = await assessmentService.getLatest();
      set({ data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
}));
```

## Project Structure

```
frontend/
├── src/
│   ├── config/
│   │   ├── env.ts          # Environment configuration (SINGLE SOURCE OF TRUTH)
│   │   └── index.ts        # Config exports
│   ├── api/
│   │   ├── endpoints.ts    # All API endpoint definitions
│   │   └── index.ts        # API exports
│   ├── services/
│   │   ├── api.client.ts   # API client (uses env.apiBaseUrl)
│   │   └── *.service.ts    # Service files (use ENDPOINTS)
│   └── ...
├── .env                    # Environment variables
├── .env.example            # Example environment file
└── vite.config.ts          # Vite config (uses env vars for proxy)
```

## Configuration Flow

```
┌─────────────┐
│   .env      │  Environment variables
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ config/env  │  Validates & exports config
└──────┬──────┘
       │
       ├──────────┐
       │          │
       ▼          ▼
┌──────────┐  ┌─────────────┐
│ api.client│  │  endpoints  │  Uses env.apiBaseUrl
└────┬─────┘  └─────────────┘
     │
     ▼
┌─────────────┐
│  services   │  Use ENDPOINTS + api client
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   state     │  Uses services
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ components  │  Use state hooks
└─────────────┘
```

## Best Practices

### ✅ DO

1. **Always use `env` from `@/config`** for configuration values
2. **Always use `ENDPOINTS` from `@/api/endpoints`** for API paths
3. **Use environment variables** for different environments
4. **Keep endpoints centralized** in `api/endpoints.ts`
5. **Use services** for API calls, not direct fetch in components

### ❌ DON'T

1. **Never hardcode URLs** anywhere in the codebase
2. **Never use direct fetch** in components
3. **Never access `import.meta.env` directly** - use `env` config
4. **Never duplicate endpoint definitions** - use `ENDPOINTS`
5. **Never put business logic in components** - use state management

## Troubleshooting

### Issue: API calls fail with CORS errors

**Solution:** Ensure `VITE_API_BASE_URL` matches your backend server URL. In development, Vite's proxy can help:

```typescript
// vite.config.ts automatically proxies /api requests
// Make sure VITE_DEV_SERVER_PROXY_TARGET points to your backend
```

### Issue: Environment variables not loading

**Solution:** 
1. Ensure variable names start with `VITE_` prefix
2. Restart the dev server after changing `.env` files
3. Check that `.env` file is in the `frontend/` directory

### Issue: Wrong API URL in production

**Solution:** 
1. Check your production `.env` file
2. Verify `VITE_API_BASE_URL` is set correctly
3. Rebuild the application after changing environment variables

## Example: Complete Service File

```typescript
/**
 * Example Service File
 * 
 * Shows proper usage of endpoints and API client
 */

import { api } from '@/api';
import { ENDPOINTS } from '@/api/endpoints';
import type { MyDataType, CreateRequest } from '@/types/api';

export const myService = {
  /**
   * Get all items
   */
  getAll: async (): Promise<MyDataType[]> => {
    return api.get(ENDPOINTS.MY_RESOURCE.BASE);
  },

  /**
   * Get item by ID
   */
  getById: async (id: string): Promise<MyDataType> => {
    return api.get(ENDPOINTS.MY_RESOURCE.GET_BY_ID(id));
  },

  /**
   * Create new item
   */
  create: async (data: CreateRequest): Promise<MyDataType> => {
    return api.post(ENDPOINTS.MY_RESOURCE.CREATE, data);
  },

  /**
   * Update item
   */
  update: async (id: string, data: Partial<CreateRequest>): Promise<MyDataType> => {
    return api.put(ENDPOINTS.MY_RESOURCE.UPDATE(id), data);
  },

  /**
   * Delete item
   */
  delete: async (id: string): Promise<void> => {
    return api.delete(ENDPOINTS.MY_RESOURCE.DELETE(id));
  },
};
```

## Summary

- ✅ Configuration is centralized in `src/config/env.ts`
- ✅ All endpoints are defined in `src/api/endpoints.ts`
- ✅ API client automatically uses `env.apiBaseUrl`
- ✅ No hardcoded URLs anywhere in the codebase
- ✅ Easy to switch between environments via `.env` files
