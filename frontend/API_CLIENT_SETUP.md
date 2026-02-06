# API Client Layer - Setup Complete

## ✅ Created Files

1. **`src/api/types.ts`** - Type definitions for requests, responses, and configurations
2. **`src/api/errors.ts`** - Standardized error classes (ApiError, NetworkError, ValidationError, etc.)
3. **`src/api/client.ts`** - Main API client with typed request helpers
4. **`src/api/index.ts`** - Centralized exports
5. **`src/api/README.md`** - Usage documentation
6. **`src/vite-env.d.ts`** - Updated with environment variable types

## 📋 Features Implemented

✅ **Base URL from environment variable** (`VITE_API_BASE_URL`)
✅ **Typed request helpers** (GET, POST, PUT, PATCH, DELETE)
✅ **Standard error handling** (8 error classes)
✅ **No business logic** (pure abstraction)
✅ **TypeScript support** (fully typed)
✅ **Query parameters** support
✅ **Request timeout** support
✅ **Request cancellation** (AbortSignal)
✅ **FormData** support
✅ **Automatic JSON parsing**
✅ **Authentication token** placeholder (ready for implementation)

## 🔧 Setup Required

### 1. Create `.env` file

Create `Frontend/.env` file with:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**Note**: `.env.example` was blocked from creation, but you can create `.env` manually.

### 2. Implement Authentication Token Storage

Update `src/api/client.ts`:

```typescript
// In getAuthToken() function (line ~60)
function getAuthToken(): string | null {
  // Option 1: localStorage
  return localStorage.getItem('auth_token');
  
  // Option 2: sessionStorage
  // return sessionStorage.getItem('token');
  
  // Option 3: Cookie-based (handled by credentials: 'include')
  // return null;
}

// In setAuthToken() function (line ~280)
export function setAuthToken(token: string | null): void {
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}
```

## 📖 Usage Example

```typescript
import { get, post, ApiError, NotFoundError } from '@/api';

// GET request
try {
  const response = await get<User>('/users/123');
  console.log(response.data);
} catch (error) {
  if (error instanceof NotFoundError) {
    console.error('User not found');
  }
}

// POST request
const response = await post<User, CreateUserRequest>('/users', {
  name: 'John Doe',
  email: 'john@example.com',
});
```

## 🚫 What's NOT Included

- ❌ Service layer (create separately: `src/services/`)
- ❌ Business logic (keep in services/components)
- ❌ React Query integration (can be added later)
- ❌ Request interceptors (can be added if needed)
- ❌ Response caching (use React Query for this)

## 📝 Next Steps

1. **Create `.env` file** with `VITE_API_BASE_URL`
2. **Implement token storage** in `client.ts`
3. **Create service layer** (e.g., `src/services/auth.service.ts`)
4. **Connect services to components** (replace localStorage calls)

## 📚 Documentation

See `src/api/README.md` for complete usage documentation.
