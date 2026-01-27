# Frontend Architecture

## Overview

This is a production-ready React + Vite + TypeScript frontend with comprehensive routing and API service layer.

## Structure

```
frontend/
├── src/
│   ├── config/                 # Configuration
│   │   └── env.ts             # Environment config with validation
│   ├── types/                  # TypeScript definitions
│   │   └── api.ts             # API types & interfaces
│   ├── services/               # API service layer
│   │   ├── api.client.ts      # Axios instance with interceptors
│   │   ├── document.service.ts
│   │   ├── baseline.service.ts
│   │   ├── timeline.service.ts
│   │   ├── progress.service.ts
│   │   ├── assessment.service.ts
│   │   └── index.ts           # Service exports
│   ├── router/                 # React Router
│   │   └── index.tsx          # Route definitions (lazy loaded)
│   ├── pages/                  # Page components
│   │   ├── DashboardPage.tsx
│   │   ├── DocumentsPage.tsx
│   │   ├── BaselinesPage.tsx
│   │   ├── TimelinesPage.tsx
│   │   ├── ProgressPage.tsx
│   │   ├── HealthDashboardPage.tsx
│   │   └── ...                # (17 pages total)
│   ├── components/             # Reusable components (empty)
│   ├── hooks/                  # Custom hooks (empty)
│   ├── store/                  # State management (empty)
│   ├── utils/                  # Utilities (empty)
│   ├── App.tsx                 # Root component
│   └── main.tsx                # Entry point
├── .env                        # Environment variables
├── .env.example                # Environment template
├── package.json
├── vite.config.ts             # Vite config with path aliases
├── tsconfig.json              # TypeScript config with path aliases
└── README.md

## Key Features

### 1. Environment Configuration (`config/env.ts`)

Type-safe environment configuration with validation:

```typescript
import { env } from '@/config/env';

console.log(env.apiBaseUrl);     // Typed access
console.log(env.isDevelopment);  // Boolean flags
```

**Environment Variables:**
- `VITE_API_BASE_URL` (required)
- `VITE_APP_NAME` (optional)
- `VITE_API_TIMEOUT` (optional)
- `VITE_ENABLE_ANALYTICS` (optional)
- `VITE_ENABLE_DEBUG` (optional)

### 2. API Client (`services/api.client.ts`)

Configured Axios instance with:
- **Request interceptor**: Adds auth tokens automatically
- **Response interceptor**: Handles errors consistently
- **Development logging**: Automatic request/response logs
- **Error transformation**: Consistent error format

```typescript
import { api } from '@/services';

// Simple API calls
const data = await api.get<User>('/api/v1/users/me');
const result = await api.post<CreateResponse>('/api/v1/documents', formData);

// File upload with progress
const { documentId } = await api.upload(
  '/api/v1/documents/upload',
  file,
  (progress) => console.log(`${progress}%`)
);
```

### 3. Service Layer

Organized by domain with typed requests/responses:

**Document Service**
```typescript
import { documentService } from '@/services';

const { documentId } = await documentService.upload(file, title, description);
const doc = await documentService.getById(documentId);
const docs = await documentService.getUserDocuments();
```

**Baseline Service**
```typescript
import { baselineService } from '@/services';

const { baselineId } = await baselineService.create({
  programName: 'PhD in CS',
  institution: 'MIT',
  fieldOfStudy: 'Machine Learning',
  startDate: '2024-09-01',
});
```

**Timeline Service**
```typescript
import { timelineService } from '@/services';

// Create draft
const { draftTimelineId } = await timelineService.createDraft({
  baselineId: '123',
  title: 'My PhD Timeline',
});

// Get with details
const details = await timelineService.getDraftWithDetails(draftTimelineId);

// Commit
const { committedTimelineId } = await timelineService.commit({
  draftTimelineId,
  title: 'Final Timeline v1.0',
});
```

**Progress Service**
```typescript
import { progressService } from '@/services';

// Mark milestone complete
await progressService.completeMilestone(milestoneId, '2024-01-27', 'Done!');

// Get progress
const progress = await progressService.getTimelineProgress(timelineId);
console.log(`${progress.completionPercentage}% complete`);
```

**Assessment Service**
```typescript
import { assessmentService } from '@/services';

// Submit questionnaire
const summary = await assessmentService.submitQuestionnaire({
  responses: [
    { dimension: 'RESEARCH_PROGRESS', questionId: 'rp1', responseValue: 4 },
    { dimension: 'MENTAL_WELLBEING', questionId: 'mw1', responseValue: 3 },
  ],
  assessmentType: 'self_assessment',
});

console.log(summary.overallStatus); // 'good', 'fair', etc.
console.log(summary.recommendations);
```

### 4. Type Safety (`types/api.ts`)

Comprehensive TypeScript types for all entities:

- User, DocumentArtifact, Baseline
- DraftTimeline, CommittedTimeline, TimelineStage, TimelineMilestone
- ProgressEvent, JourneyAssessment
- Request/Response types
- ApiError, ApiResponse, PaginatedResponse

### 5. Routing (`router/index.tsx`)

React Router with lazy loading for code splitting:

**Routes:**
- `/` → Redirects to dashboard
- `/dashboard` → Main dashboard
- `/documents` → Document management
  - `/documents/upload` → Upload form
  - `/documents/:documentId` → Document details
- `/baselines` → Baseline management
  - `/baselines/create` → Create baseline
  - `/baselines/:baselineId` → Baseline details
- `/timelines` → Timeline management
  - `/timelines/draft/:draftId` → Draft timeline view
  - `/timelines/committed/:committedId` → Committed timeline view
- `/progress` → Progress tracking
  - `/progress/timeline/:timelineId` → Timeline progress
- `/health` → Journey health
  - `/health/assessment` → Take assessment
  - `/health/history` → Assessment history
  - `/health/:assessmentId` → Assessment details

**Lazy Loading:**
```typescript
{
  path: 'documents',
  children: [
    {
      index: true,
      lazy: () => import('@/pages/DocumentsPage'),
    },
  ],
}
```

### 6. Path Aliases

Import with `@/` prefix for clean paths:

```typescript
// Instead of:
import { api } from '../../../services/api.client';

// Use:
import { api } from '@/services';
import { User } from '@/types/api';
import { env } from '@/config/env';
```

## Getting Started

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Development Server

```bash
npm run dev
```

Application runs at: http://localhost:3000

### 4. Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## Error Handling

All API errors are automatically transformed:

```typescript
try {
  await documentService.upload(file);
} catch (error) {
  // Error is typed as ApiError
  console.error(error.message);  // User-friendly message
  console.error(error.code);     // Error code
  console.error(error.details);  // Raw error details
}
```

## Authentication

The API client automatically adds auth tokens from localStorage:

```typescript
// After login, store token
localStorage.setItem('auth_token', token);

// All subsequent requests include:
// Authorization: Bearer <token>
```

## Next Steps

1. **UI Components**: Build component library
2. **State Management**: Add Zustand stores
3. **Forms**: Implement form validation (React Hook Form)
4. **Authentication**: Add auth flow and protected routes
5. **Error Boundaries**: Add error boundary components
6. **Loading States**: Add loading indicators
7. **Notifications**: Add toast notifications

## Development Tips

- Use `npm run type-check` to check TypeScript errors
- Use `npm run lint` to check code style
- All pages use lazy loading for optimal performance
- API responses are automatically logged in development mode
- Environment validation runs on app startup
