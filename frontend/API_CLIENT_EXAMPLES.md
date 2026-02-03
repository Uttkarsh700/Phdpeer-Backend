# API Client - Quick Examples

## Basic Usage

```typescript
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';

// GET request
const assessment = await apiClient.get<AssessmentSummary>(
  ENDPOINTS.ASSESSMENTS.GET_LATEST
);

// POST request (idempotency key auto-generated)
const result = await apiClient.post<ResponseType>(
  ENDPOINTS.ASSESSMENTS.SUBMIT,
  { responses: [...] }
);

// POST with custom idempotency key
const result = await apiClient.post<ResponseType>(
  ENDPOINTS.ASSESSMENTS.SUBMIT,
  data,
  { idempotencyKey: 'my-unique-key' }
);
```

## Error Handling

```typescript
import { apiClient, ApiClientError } from '@/api/client';

try {
  const data = await apiClient.get(ENDPOINTS.ASSESSMENTS.GET_LATEST);
} catch (error) {
  if (error instanceof ApiClientError) {
    if (error.isNetworkError) {
      // Handle network issues
    } else if (error.isServerError) {
      // Handle server errors (5xx)
    } else if (error.isClientError) {
      // Handle client errors (4xx)
    }
    console.error(error.message);
    console.error(error.code);
    console.error(error.status);
  }
}
```

## File Upload

```typescript
const result = await apiClient.upload<{ documentId: string }>(
  ENDPOINTS.DOCUMENTS.UPLOAD,
  file,
  {
    onProgress: (progress) => {
      console.log(`Upload: ${progress}%`);
    },
  }
);
```

## Service Pattern

```typescript
import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';

export const myService = {
  getAll: async () => {
    return apiClient.get<Item[]>(ENDPOINTS.MY_RESOURCE.BASE);
  },
  
  getById: async (id: string) => {
    return apiClient.get<Item>(ENDPOINTS.MY_RESOURCE.GET_BY_ID(id));
  },
  
  create: async (data: CreateRequest) => {
    return apiClient.post<{ id: string }>(ENDPOINTS.MY_RESOURCE.CREATE, data);
  },
};
```
