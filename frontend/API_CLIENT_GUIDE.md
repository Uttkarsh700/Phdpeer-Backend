# API Client Guide

## Overview

The centralized API client (`@/api/client`) is the **SINGLE POINT OF ENTRY** for all backend API calls. All services MUST use this client - no direct `fetch` or `axios` calls are allowed.

## Features

✅ **Typed Request/Response Helpers** - Full TypeScript support  
✅ **Standard Error Handling** - Consistent error format with `ApiClientError`  
✅ **Idempotency Support** - Automatic idempotency keys for POST requests  
✅ **No Domain Logic** - Pure API client, no business logic  
✅ **Automatic Auth** - Adds authentication tokens from localStorage  
✅ **Request/Response Logging** - Development mode logging  

## Basic Usage

### Import the Client

```typescript
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
```

### GET Request

```typescript
// Simple GET
const data = await apiClient.get<MyDataType>(ENDPOINTS.ASSESSMENTS.GET_LATEST);

// GET with query parameters
const items = await apiClient.get<Item[]>(ENDPOINTS.DOCUMENTS.LIST, {
  skip: 0,
  limit: 10,
});
```

### POST Request

```typescript
// POST with data (idempotency key auto-generated)
const result = await apiClient.post<ResponseType>(
  ENDPOINTS.ASSESSMENTS.SUBMIT,
  { question1: 'answer1' }
);

// POST with custom idempotency key
const result = await apiClient.post<ResponseType>(
  ENDPOINTS.ASSESSMENTS.SUBMIT,
  data,
  { idempotencyKey: 'my-custom-key' }
);
```

### PUT/PATCH/DELETE

```typescript
// PUT request
const updated = await apiClient.put<ItemType>(
  ENDPOINTS.BASELINES.UPDATE(id),
  { name: 'New Name' }
);

// PATCH request
const patched = await apiClient.patch<ItemType>(
  ENDPOINTS.BASELINES.UPDATE(id),
  { notes: 'Updated notes' }
);

// DELETE request
await apiClient.delete<void>(ENDPOINTS.DOCUMENTS.DELETE(id));
```

### File Upload

```typescript
const result = await apiClient.upload<{ documentId: string }>(
  ENDPOINTS.DOCUMENTS.UPLOAD,
  file,
  {
    onProgress: (progress) => {
      console.log(`Upload: ${progress}%`);
    },
    fieldName: 'file', // optional, defaults to 'file'
  }
);
```

## Request Options

All methods accept an optional `ApiRequestOptions` parameter:

```typescript
interface ApiRequestOptions {
  // Idempotency key (auto-generated for POST if not provided)
  idempotencyKey?: string;
  
  // Custom headers
  headers?: Record<string, string>;
  
  // Skip authentication token
  skipAuth?: boolean;
  
  // Retry configuration (future feature)
  retry?: {
    attempts: number;
    delay: number;
  };
  
  // All standard AxiosRequestConfig options
  timeout?: number;
  // ... etc
}
```

### Examples

```typescript
// Custom headers
await apiClient.post('/endpoint', data, {
  headers: {
    'X-Custom-Header': 'value',
  },
});

// Skip authentication (for public endpoints)
await apiClient.get('/public/endpoint', undefined, {
  skipAuth: true,
});

// Custom idempotency key
await apiClient.post('/endpoint', data, {
  idempotencyKey: 'my-unique-key-123',
});
```

## Error Handling

All errors are thrown as `ApiClientError` instances with rich error information:

```typescript
import { ApiClientError } from '@/api/client';

try {
  const data = await apiClient.get(ENDPOINTS.ASSESSMENTS.GET_LATEST);
} catch (error) {
  if (error instanceof ApiClientError) {
    console.error('Error Code:', error.code);
    console.error('Status:', error.status);
    console.error('Message:', error.message);
    console.error('Details:', error.details);
    
    // Error type flags
    if (error.isNetworkError) {
      // Handle network error
    }
    if (error.isTimeoutError) {
      // Handle timeout
    }
    if (error.isServerError) {
      // Handle server error (5xx)
    }
    if (error.isClientError) {
      // Handle client error (4xx)
    }
  }
}
```

### Error Properties

```typescript
class ApiClientError {
  message: string;           // User-friendly error message
  code: string;              // Error code (HTTP status or custom)
  status?: number;           // HTTP status code
  details?: any;             // Additional error details
  originalError?: AxiosError; // Original Axios error
  isNetworkError: boolean;   // True if network error
  isTimeoutError: boolean;   // True if timeout
  isServerError: boolean;    // True if 5xx error
  isClientError: boolean;   // True if 4xx error
}
```

## Idempotency

POST requests automatically include an `Idempotency-Key` header to ensure idempotent operations. The key is auto-generated (UUID v4) but can be customized:

```typescript
// Auto-generated key
await apiClient.post('/endpoint', data);

// Custom key (useful for retries)
const idempotencyKey = 'my-unique-key';
await apiClient.post('/endpoint', data, { idempotencyKey });
```

## Service Pattern

All services should follow this pattern:

```typescript
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import type { MyType, CreateRequest } from '@/types/api';

export const myService = {
  /**
   * Get all items
   */
  getAll: async (): Promise<MyType[]> => {
    return apiClient.get<MyType[]>(ENDPOINTS.MY_RESOURCE.BASE);
  },

  /**
   * Get item by ID
   */
  getById: async (id: string): Promise<MyType> => {
    return apiClient.get<MyType>(ENDPOINTS.MY_RESOURCE.GET_BY_ID(id));
  },

  /**
   * Create item
   */
  create: async (data: CreateRequest): Promise<{ id: string }> => {
    return apiClient.post<{ id: string }>(ENDPOINTS.MY_RESOURCE.CREATE, data);
  },

  /**
   * Update item
   */
  update: async (id: string, data: Partial<CreateRequest>): Promise<MyType> => {
    return apiClient.put<MyType>(ENDPOINTS.MY_RESOURCE.UPDATE(id), data);
  },

  /**
   * Delete item
   */
  delete: async (id: string): Promise<void> => {
    return apiClient.delete<void>(ENDPOINTS.MY_RESOURCE.DELETE(id));
  },
};
```

## Type Safety

The client is fully typed. Always specify the response type:

```typescript
// ✅ Good: Explicit type
const assessment: AssessmentSummary = await apiClient.get<AssessmentSummary>(
  ENDPOINTS.ASSESSMENTS.GET_LATEST
);

// ❌ Bad: No type (returns 'any')
const assessment = await apiClient.get(ENDPOINTS.ASSESSMENTS.GET_LATEST);
```

## Best Practices

### ✅ DO

1. **Always use `apiClient`** - Never use `fetch` or direct `axios` calls
2. **Use `ENDPOINTS` constants** - Never hardcode API paths
3. **Specify response types** - Use TypeScript generics
4. **Handle errors properly** - Use `ApiClientError` type checking
5. **Use idempotency keys** - For critical POST operations

### ❌ DON'T

1. **Don't use `fetch` directly** - Always use `apiClient`
2. **Don't hardcode URLs** - Use `ENDPOINTS` constants
3. **Don't skip error handling** - Always wrap in try/catch
4. **Don't put business logic in services** - Services are thin wrappers
5. **Don't access `localStorage` directly** - Auth is handled automatically

## Migration from Old Client

If you have code using the old `api` from `./api.client`:

```typescript
// Old (deprecated)
import { api } from './api.client';
const data = await api.get('/api/v1/endpoint');

// New (correct)
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
const data = await apiClient.get<DataType>(ENDPOINTS.MY_ENDPOINT);
```

The old `api` export is still available for backward compatibility but will be removed in a future version.

## Advanced Usage

### Raw Request (for edge cases)

```typescript
const response = await apiClient.request<MyType>({
  method: 'POST',
  url: '/custom/endpoint',
  data: { custom: 'data' },
  headers: { 'X-Custom': 'header' },
});

// Response includes full response object
console.log(response.status);
console.log(response.data);
console.log(response.headers);
```

### Custom Axios Config

All standard Axios configuration options are supported:

```typescript
await apiClient.get('/endpoint', params, {
  timeout: 5000,
  headers: { 'X-Custom': 'value' },
  // ... any other AxiosRequestConfig options
});
```

## Summary

- ✅ **Single entry point**: All API calls go through `apiClient`
- ✅ **Type safe**: Full TypeScript support with generics
- ✅ **Error handling**: Standardized `ApiClientError` class
- ✅ **Idempotency**: Automatic keys for POST requests
- ✅ **No domain logic**: Pure API client, business logic in state layer
- ✅ **Centralized**: All endpoints in `@/api/endpoints`
