# Frontend Project Structure Proposal

## Overview

This document proposes a state-driven React + TypeScript project structure that enforces clear separation of concerns, with no business logic in components and no direct fetch calls inside components.

## Proposed Directory Structure

```
frontend/
├── src/
│   ├── pages/              # Page-level components (route handlers)
│   ├── components/         # Reusable UI components (presentational only)
│   ├── api/               # API client and endpoint definitions
│   ├── state/             # State management (stores, slices, hooks)
│   ├── guards/            # Route guards and permission checks
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Pure utility functions
│   ├── hooks/             # Custom React hooks (state-related)
│   ├── config/            # Configuration files
│   ├── layouts/           # Layout components
│   └── router/            # Routing configuration
```

## Folder Responsibilities

### 📄 `pages/`
**Responsibility:** Page-level components that represent routes in your application.

- **What goes here:**
  - Components that correspond to specific routes
  - Page-level composition logic (combining components, guards, state hooks)
  - Route-specific layout decisions

- **What does NOT go here:**
  - Business logic (moved to state/ or hooks/)
  - API calls (moved to api/ and accessed via state/)
  - Reusable UI components (moved to components/)

- **Example:**
  ```typescript
  // pages/DashboardPage.tsx
  import { useDashboardState } from '@/state/dashboard';
  import { DashboardGuard } from '@/guards/DashboardGuard';
  import { DashboardView } from '@/components/dashboard/DashboardView';

  export const DashboardPage = () => {
    const { data, loading, error } = useDashboardState();
    
    return (
      <DashboardGuard>
        <DashboardView data={data} loading={loading} error={error} />
      </DashboardGuard>
    );
  };
  ```

---

### 🧩 `components/`
**Responsibility:** Reusable, presentational UI components with no business logic.

- **What goes here:**
  - Pure presentational components
  - UI-only components (buttons, cards, forms, modals)
  - Components that receive data via props and emit events via callbacks
  - Styled components and UI primitives

- **What does NOT go here:**
  - Business logic or data transformations
  - Direct API calls or fetch statements
  - State management (use props and callbacks instead)
  - Route-specific logic

- **Example:**
  ```typescript
  // components/dashboard/DashboardView.tsx
  interface DashboardViewProps {
    data: DashboardData | null;
    loading: boolean;
    error: string | null;
    onRefresh?: () => void;
  }

  export const DashboardView = ({ data, loading, error, onRefresh }: DashboardViewProps) => {
    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage message={error} />;
    if (!data) return <EmptyState />;

    return (
      <div>
        <DashboardHeader onRefresh={onRefresh} />
        <DashboardContent data={data} />
      </div>
    );
  };
  ```

---

### 🌐 `api/`
**Responsibility:** All API communication and endpoint definitions.

- **What goes here:**
  - API client configuration (axios, fetch wrapper, etc.)
  - Endpoint definitions and request/response types
  - API service functions (pure functions that make HTTP calls)
  - Request/response interceptors
  - API error handling utilities

- **What does NOT go here:**
  - State management logic
  - Component-specific logic
  - Business logic transformations

- **Structure:**
  ```
  api/
  ├── client.ts           # API client instance (axios/fetch wrapper)
  ├── endpoints.ts        # Endpoint URL constants
  ├── types.ts            # API request/response types
  ├── interceptors.ts     # Request/response interceptors
  └── services/           # Service modules by domain
      ├── auth.service.ts
      ├── dashboard.service.ts
      └── assessment.service.ts
  ```

- **Example:**
  ```typescript
  // api/services/dashboard.service.ts
  import { apiClient } from '../client';
  import { DASHBOARD_ENDPOINTS } from '../endpoints';
  import type { DashboardResponse, DashboardRequest } from '../types';

  export const dashboardService = {
    getDashboard: async (params: DashboardRequest): Promise<DashboardResponse> => {
      const response = await apiClient.get<DashboardResponse>(
        DASHBOARD_ENDPOINTS.GET_DASHBOARD,
        { params }
      );
      return response.data;
    },
    
    updateDashboard: async (id: string, data: Partial<DashboardRequest>): Promise<DashboardResponse> => {
      const response = await apiClient.put<DashboardResponse>(
        DASHBOARD_ENDPOINTS.UPDATE_DASHBOARD(id),
        data
      );
      return response.data;
    },
  };
  ```

---

### 🗄️ `state/`
**Responsibility:** Centralized state management and business logic.

- **What goes here:**
  - State stores (Zustand, Redux, Jotai, etc.)
  - State slices/modules organized by domain
  - Business logic and data transformations
  - State selectors and computed values
  - Custom hooks that expose state and actions
  - State persistence logic

- **What does NOT go here:**
  - API client code (use api/ services)
  - UI components
  - Route logic

- **Structure:**
  ```
  state/
  ├── store.ts            # Root store configuration
  ├── slices/             # State slices by domain
  │   ├── auth.slice.ts
  │   ├── dashboard.slice.ts
  │   └── assessment.slice.ts
  ├── hooks/              # State hooks (re-exported from slices)
  │   ├── useAuth.ts
  │   ├── useDashboard.ts
  │   └── useAssessment.ts
  └── middleware/         # State middleware (logging, persistence)
  ```

- **Example:**
  ```typescript
  // state/slices/dashboard.slice.ts
  import { create } from 'zustand';
  import { dashboardService } from '@/api/services/dashboard.service';
  import type { DashboardData } from '@/types';

  interface DashboardState {
    data: DashboardData | null;
    loading: boolean;
    error: string | null;
    fetchDashboard: () => Promise<void>;
    updateDashboard: (updates: Partial<DashboardData>) => Promise<void>;
    reset: () => void;
  }

  export const useDashboardStore = create<DashboardState>((set, get) => ({
    data: null,
    loading: false,
    error: null,

    fetchDashboard: async () => {
      set({ loading: true, error: null });
      try {
        const data = await dashboardService.getDashboard({});
        set({ data, loading: false });
      } catch (error) {
        set({ error: error.message, loading: false });
      }
    },

    updateDashboard: async (updates) => {
      const { data } = get();
      if (!data) return;
      
      set({ loading: true });
      try {
        const updated = await dashboardService.updateDashboard(data.id, updates);
        set({ data: updated, loading: false });
      } catch (error) {
        set({ error: error.message, loading: false });
      }
    },

    reset: () => set({ data: null, loading: false, error: null }),
  }));

  // state/hooks/useDashboard.ts
  export const useDashboardState = () => {
    const store = useDashboardStore();
    return {
      data: store.data,
      loading: store.loading,
      error: store.error,
      fetchDashboard: store.fetchDashboard,
      updateDashboard: store.updateDashboard,
      reset: store.reset,
    };
  };
  ```

---

### 🛡️ `guards/`
**Responsibility:** Route protection, permission checks, and access control.

- **What goes here:**
  - Route guard components (HOCs or wrapper components)
  - Permission checking logic
  - Authentication/authorization guards
  - Redirect logic for unauthorized access
  - Role-based access control (RBAC) components

- **What does NOT go here:**
  - State management (use state/ hooks)
  - API calls (use api/ services via state/)
  - UI components (use components/)

- **Example:**
  ```typescript
  // guards/AuthGuard.tsx
  import { Navigate } from 'react-router-dom';
  import { useAuthState } from '@/state/hooks/useAuth';

  interface AuthGuardProps {
    children: React.ReactNode;
  }

  export const AuthGuard = ({ children }: AuthGuardProps) => {
    const { isAuthenticated, loading } = useAuthState();

    if (loading) return <LoadingSpinner />;
    if (!isAuthenticated) return <Navigate to="/login" replace />;

    return <>{children}</>;
  };

  // guards/RoleGuard.tsx
  import { useAuthState } from '@/state/hooks/useAuth';
  import { ForbiddenPage } from '@/pages/ForbiddenPage';

  interface RoleGuardProps {
    children: React.ReactNode;
    allowedRoles: string[];
  }

  export const RoleGuard = ({ children, allowedRoles }: RoleGuardProps) => {
    const { user } = useAuthState();
    
    if (!user || !allowedRoles.includes(user.role)) {
      return <ForbiddenPage />;
    }

    return <>{children}</>;
  };
  ```

---

### 📝 `types/`
**Responsibility:** TypeScript type definitions and interfaces.

- **What goes here:**
  - Domain models and entities
  - Shared type definitions
  - API request/response types (or reference api/types.ts)
  - Component prop types (if shared)
  - Utility types

- **Structure:**
  ```
  types/
  ├── index.ts            # Re-export all types
  ├── domain.ts           # Domain models
  ├── api.ts              # API types (or reference api/types.ts)
  └── common.ts           # Common/shared types
  ```

---

### 🔧 `utils/`
**Responsibility:** Pure utility functions with no side effects.

- **What goes here:**
  - Pure functions (no side effects)
  - Formatters (date, currency, etc.)
  - Validators
  - Data transformation utilities
  - Constants

- **What does NOT go here:**
  - Functions that make API calls
  - Functions that access state directly
  - React hooks

---

### 🎣 `hooks/`
**Responsibility:** Custom React hooks that are state-related or combine multiple concerns.

- **What goes here:**
  - Custom hooks that wrap state management
  - Hooks that combine multiple state slices
  - Hooks that provide computed/derived state
  - UI-related hooks (not state management - those go in state/hooks/)

- **Note:** State management hooks should live in `state/hooks/`, while general-purpose React hooks can live here.

---

### ⚙️ `config/`
**Responsibility:** Application configuration.

- **What goes here:**
  - Environment variables
  - Feature flags
  - App constants
  - Configuration objects

---

### 🎨 `layouts/`
**Responsibility:** Layout components that wrap pages.

- **What goes here:**
  - Main layout components
  - Header/Footer components
  - Sidebar layouts
  - Page container components

---

### 🛣️ `router/`
**Responsibility:** Routing configuration.

- **What goes here:**
  - Route definitions
  - Route configuration
  - Route constants

---

## Data Flow

```
┌─────────┐
│  Page   │
└────┬────┘
     │ uses
     ▼
┌─────────┐      ┌─────────┐
│  Guard  │─────▶│  State  │
└─────────┘      │  Hook   │
                 └────┬────┘
                      │ uses
                      ▼
                 ┌─────────┐
                 │   API   │
                 │ Service │
                 └─────────┘
                      │
                      ▼
                 ┌─────────┐
                 │  API    │
                 │ Client  │
                 └─────────┘
```

## Key Principles

1. **Components are pure:** Components receive data via props and emit events via callbacks. No business logic, no API calls.

2. **State manages business logic:** All business logic, data transformations, and API orchestration happens in state management.

3. **API layer is isolated:** API services are pure functions that make HTTP calls. They don't know about state or components.

4. **Guards handle access control:** Route protection and permissions are handled by guard components that use state hooks.

5. **Pages compose everything:** Pages are thin orchestrators that combine guards, state hooks, and components.

## Example: Complete Flow

### 1. API Service (`api/services/dashboard.service.ts`)
```typescript
export const dashboardService = {
  getDashboard: async () => {
    const response = await apiClient.get('/api/dashboard');
    return response.data;
  },
};
```

### 2. State Slice (`state/slices/dashboard.slice.ts`)
```typescript
export const useDashboardStore = create((set) => ({
  data: null,
  loading: false,
  fetchDashboard: async () => {
    set({ loading: true });
    const data = await dashboardService.getDashboard();
    set({ data, loading: false });
  },
}));
```

### 3. State Hook (`state/hooks/useDashboard.ts`)
```typescript
export const useDashboardState = () => {
  const store = useDashboardStore();
  return {
    data: store.data,
    loading: store.loading,
    fetchDashboard: store.fetchDashboard,
  };
};
```

### 4. Guard (`guards/AuthGuard.tsx`)
```typescript
export const AuthGuard = ({ children }) => {
  const { isAuthenticated } = useAuthState();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};
```

### 5. Component (`components/dashboard/DashboardView.tsx`)
```typescript
export const DashboardView = ({ data, loading, onRefresh }) => {
  if (loading) return <Spinner />;
  return <div>{/* render data */}</div>;
};
```

### 6. Page (`pages/DashboardPage.tsx`)
```typescript
export const DashboardPage = () => {
  const { data, loading, fetchDashboard } = useDashboardState();
  
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return (
    <AuthGuard>
      <DashboardView data={data} loading={loading} onRefresh={fetchDashboard} />
    </AuthGuard>
  );
};
```

## Benefits

✅ **Clear separation of concerns** - Each folder has a single, well-defined responsibility  
✅ **Testability** - Business logic is isolated and easily testable  
✅ **Maintainability** - Easy to find and modify code  
✅ **Scalability** - Structure supports growth  
✅ **Type safety** - TypeScript types flow through the layers  
✅ **Reusability** - Components and utilities are easily reusable  
✅ **No coupling** - Components don't depend on API or state implementation details
