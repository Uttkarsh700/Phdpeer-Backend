# Frontend Architecture Summary

## Framework & Language

- **Framework**: React 18.3.1
- **Language**: TypeScript 5.8.3
- **Build Tool**: Vite 5.4.19
- **UI Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS 3.4.17

---

## Routing Mechanism

- **Library**: React Router DOM v6.30.1
- **Configuration**: Centralized in `src/App.tsx` (no separate router file)
- **Router Type**: `BrowserRouter`
- **Route Protection**: Implemented in `src/components/layout/Layout.tsx`
  - Uses `sessionStorage` checks (`frensei_access`, `isAuthenticated`)
  - Redirects to `/auth` for protected routes if not authenticated
  - Protected routes: `/wellbeing`, `/timeline`, `/network`, `/university-dashboard`, `/collaboration-ledger`, `/dashboard`, `/writing-evolution`

**Route Structure**:
- Public: `/` (GatewayLanding), `/auth` (Auth)
- Protected (with Layout): 14 routes including `/home`, `/dashboard`, `/timeline`, `/wellbeing`, `/writing-evolution/*`, etc.
- Catch-all: `*` → NotFound

---

## State Management

### Current State
- **No Global State Management**: No Redux, Zustand, Recoil, or Context API for global state
- **Local Component State**: Extensive use of `useState` hooks in individual components
- **React Query Setup**: `QueryClient` and `QueryClientProvider` are configured in `App.tsx` but **NOT actively used** in components
- **Persistence**: Uses `localStorage` and `sessionStorage` for data persistence

### State Storage Locations
- **Authentication**: `sessionStorage.getItem("isAuthenticated")`, `sessionStorage.getItem("userId")`
- **Gateway Access**: `sessionStorage.getItem("frensei_access")`
- **Collaboration Events**: `localStorage.getItem("collaboration_events")`
- **Component State**: All managed via `useState` hooks (no shared state)

### State Management Pattern
```typescript
// Typical pattern found throughout codebase:
const [events, setEvents] = useState<CollaborationEvent[]>([]);
const [loading, setLoading] = useState(false);
const [currentUserId, setCurrentUserId] = useState<string | null>(null);

// Data fetched from localStorage, not API:
const storedEvents = localStorage.getItem("collaboration_events");
const eventsData = storedEvents ? JSON.parse(storedEvents) : [];
```

---

## API Call Locations

### Critical Finding: **NO Backend Integration**

- **No API Client**: No centralized API client (no axios, fetch wrapper, or API service layer)
- **No API Calls**: Only one `fetch()` call found in entire codebase (loading image asset: `PenguinMascot.tsx`)
- **No Service Layer**: No `src/services/` or `src/api/` directories
- **Mock Data Only**: All data operations use `localStorage`/`sessionStorage`

### TODO Comments Found
Throughout the codebase, there are numerous `// TODO: Replace with your backend API call` comments:

**Locations with TODOs**:
1. `src/pages/CollaborationLedger.tsx` - `fetchEvents()` function
2. `src/components/ledger/AddEventModal.tsx` - `handleSubmit()` function
3. `src/components/ledger/ReconstructJourneyModal.tsx` - `handleReconstruct()` function
4. `src/components/profile/ProfileWheel.tsx` - `handleAddToTimeline()` function
5. `src/components/layout/Layout.tsx` - Authentication check
6. `src/pages/CollaborationLedger.tsx` - `initializeUser()` function

**Example Pattern**:
```typescript
// TODO: Replace with your backend API call
// For now, load from localStorage or set empty array
const storedEvents = localStorage.getItem("collaboration_events");
const eventsData = storedEvents ? JSON.parse(storedEvents) : [];
```

---

## Assumptions About Backend Responses

### Current State: **No Backend Assumptions**

Since there are no actual API calls, the codebase makes **no assumptions** about backend response structures. However, based on the data structures used locally, we can infer what the frontend expects:

### Expected Data Structures

#### Collaboration Events
```typescript
interface CollaborationEvent {
  id: string;
  created_by: string;
  event_type: string;
  summary: string;
  event_date: string;
  status: 'pending' | string;
  created_at: string;
  participants?: any[];
  verifications?: any[];
}
```

#### User Authentication
- Expected: `userId` string in sessionStorage
- Expected: `isAuthenticated` boolean flag
- Expected: `frensei_access` flag for gateway access

#### Wellness Check-in
- Uses local calculation functions (`wellnessCalculations.ts`)
- No backend integration expected currently

#### Research Timeline
- Field detection from filename
- Timeline generation is **client-side only**
- No backend API for timeline generation

### Implicit Backend Expectations (from TODOs)

1. **Collaboration Events API**:
   - `GET /api/events` - Fetch user's events
   - `POST /api/events` - Create new event
   - Expected response: Array of `CollaborationEvent` objects

2. **Authentication API**:
   - `POST /api/auth/login` - User login
   - `POST /api/auth/register` - User registration
   - Expected response: User object with `userId`, `isAuthenticated` flag

3. **Journey Reconstruction API**:
   - `POST /api/journey/reconstruct` - Parse text into events
   - Expected response: `{ events: CollaborationEvent[] }` or `{ error: string }`

4. **User Management API**:
   - `GET /api/users/:userId` - Get user profile
   - `GET /api/users/:userId/members` - Get team members

---

## Key Architectural Observations

### Strengths
1. **Modern Stack**: React 18, TypeScript, Vite, Tailwind
2. **Component Library**: Well-structured shadcn/ui components
3. **Type Safety**: TypeScript interfaces defined for data structures
4. **Routing**: Clean React Router setup with route protection

### Gaps
1. **No Backend Integration**: Entirely client-side, no API layer
2. **No State Management**: No global state, all local component state
3. **No API Client**: No centralized HTTP client or error handling
4. **No Service Layer**: Business logic mixed with components
5. **React Query Unused**: Configured but not utilized
6. **No Error Handling**: No API error handling patterns
7. **No Loading States**: Limited loading state management for async operations

### Integration Points Needed

1. **API Client Layer**: Create `src/api/client.ts` or `src/services/api.ts`
2. **Service Layer**: Create `src/services/` for business logic
3. **State Management**: Consider Zustand or Context API for global state
4. **React Query Integration**: Replace localStorage calls with `useQuery`/`useMutation`
5. **Error Handling**: Implement consistent error handling for API calls
6. **Type Definitions**: Create shared types for API requests/responses

---

## Summary

The frontend is a **well-structured React application** with modern tooling, but it's currently a **frontend-only prototype** with no backend integration. All data operations use browser storage (`localStorage`/`sessionStorage`), and there are explicit TODO comments indicating where backend API calls should be added.

**Next Steps for Backend Integration**:
1. Create API client/service layer
2. Replace localStorage operations with API calls
3. Implement React Query hooks for data fetching
4. Add error handling and loading states
5. Define API contract/types for backend responses
