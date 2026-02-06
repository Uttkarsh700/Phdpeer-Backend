# API Client Layer

Centralized API client for making HTTP requests to the backend.

## Features

- ✅ Base URL from environment variable (`VITE_API_BASE_URL`)
- ✅ Typed request helpers (GET, POST, PUT, PATCH, DELETE)
- ✅ Standard error handling with custom error classes
- ✅ Automatic JSON parsing
- ✅ Query parameter support
- ✅ Request timeout support
- ✅ Request cancellation (AbortSignal)
- ✅ FormData support
- ✅ No business logic - pure abstraction

## Setup

1. **Set environment variable** in `.env` file:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

2. **Import the client**:
   ```typescript
   import { apiClient, get, post } from '@/api';
   ```

## Usage

### Basic GET Request

```typescript
import { get } from '@/api';

// Simple GET request
const response = await get<User>('/users/123');
console.log(response.data); // User object
```

### GET with Query Parameters

```typescript
import { get } from '@/api';

const response = await get<User[]>('/users', {
  params: {
    page: 1,
    limit: 10,
    active: true,
  },
});
```

### POST Request

```typescript
import { post } from '@/api';

interface CreateUserRequest {
  name: string;
  email: string;
}

const response = await post<User, CreateUserRequest>('/users', {
  name: 'John Doe',
  email: 'john@example.com',
});
```

### PUT/PATCH Request

```typescript
import { put, patch } from '@/api';

// PUT - full update
const response = await put<User, UpdateUserRequest>('/users/123', {
  name: 'Jane Doe',
  email: 'jane@example.com',
});

// PATCH - partial update
const response = await patch<User, Partial<UpdateUserRequest>>('/users/123', {
  name: 'Jane Doe',
});
```

### DELETE Request

```typescript
import { apiClient } from '@/api';

const response = await apiClient.delete('/users/123');
```

### Error Handling

```typescript
import { get, ApiError, NotFoundError, ValidationError } from '@/api';

try {
  const response = await get<User>('/users/123');
} catch (error) {
  if (error instanceof NotFoundError) {
    console.error('User not found');
  } else if (error instanceof ValidationError) {
    console.error('Validation errors:', error.errors);
  } else if (error instanceof ApiError) {
    console.error('API error:', error.message, error.status);
  }
}
```

### Request Options

```typescript
import { get } from '@/api';

const response = await get<User>('/users/123', {
  headers: {
    'Custom-Header': 'value',
  },
  timeout: 5000, // 5 seconds
  credentials: 'include', // Include cookies
  signal: abortController.signal, // Cancellation
});
```

### FormData Support

```typescript
import { post } from '@/api';

const formData = new FormData();
formData.append('file', file);
formData.append('name', 'document.pdf');

const response = await post<UploadResponse>('/upload', formData);
```

## Error Types

- `ApiError` - Base error class
- `NetworkError` - Connection issues (status 0)
- `TimeoutError` - Request timeout (status 408)
- `ClientError` - 4xx status codes
- `ServerError` - 5xx status codes
- `ValidationError` - 422 with field errors
- `UnauthorizedError` - 401
- `ForbiddenError` - 403
- `NotFoundError` - 404

## Authentication

The client automatically includes an Authorization header if a token is available. To set the token:

```typescript
import { setAuthToken, clearAuthToken } from '@/api';

// Set token (implement based on your auth strategy)
setAuthToken('your-jwt-token');

// Clear token
clearAuthToken();
```

**Note**: The `getAuthToken()` and `setAuthToken()` functions in `client.ts` are placeholders. Implement them based on your authentication strategy (localStorage, sessionStorage, etc.).

## Type Safety

All request helpers are fully typed:

```typescript
// Response type
const response = await get<User>('/users/123');
// response.data is typed as User

// Request body type
const response = await post<User, CreateUserRequest>('/users', {
  // TypeScript will validate this matches CreateUserRequest
  name: 'John',
  email: 'john@example.com',
});
```

## Next Steps

1. **Implement authentication token storage** in `client.ts`:
   - Update `getAuthToken()` to retrieve token from storage
   - Update `setAuthToken()` to store token

2. **Create service layer** (separate from API client):
   - `src/services/auth.service.ts`
   - `src/services/collaboration.service.ts`
   - `src/services/wellness.service.ts`
   - etc.

3. **Connect services to components**:
   - Replace `localStorage` calls with service methods
   - Replace mock data with API calls
