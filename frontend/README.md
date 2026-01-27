# PhD Timeline Frontend

React + Vite + TypeScript frontend for the PhD Timeline Intelligence Platform.

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **TypeScript**: Type safety
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **TailwindCSS**: Styling

## Project Structure

```
src/
├── config/             # Configuration files
│   └── env.ts          # Environment configuration
├── types/              # TypeScript type definitions
│   └── api.ts          # API types and interfaces
├── services/           # API service layer
│   ├── api.client.ts   # Configured Axios instance
│   ├── document.service.ts
│   ├── baseline.service.ts
│   ├── timeline.service.ts
│   ├── progress.service.ts
│   ├── assessment.service.ts
│   └── index.ts        # Service exports
├── router/             # React Router configuration
│   └── index.tsx       # Route definitions
├── pages/              # Page components (lazy loaded)
│   ├── DashboardPage.tsx
│   ├── DocumentsPage.tsx
│   ├── BaselinesPage.tsx
│   ├── TimelinesPage.tsx
│   ├── ProgressPage.tsx
│   ├── HealthDashboardPage.tsx
│   └── ...
├── components/         # Reusable components (to be added)
├── hooks/              # Custom hooks (to be added)
├── utils/              # Utility functions
├── App.tsx             # Root component
└── main.tsx            # Application entry point
```

## Getting Started

### Installation

```bash
npm install
```

### Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure environment variables:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=PhD Timeline Intelligence Platform
```

### Development

```bash
npm run dev
```

Application runs at: http://localhost:3000

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Architecture

### Routing

React Router with lazy loading for code splitting:

```typescript
{
  path: 'documents',
  children: [
    {
      index: true,
      lazy: () => import('@/pages/DocumentsPage'),
    },
    {
      path: ':documentId',
      lazy: () => import('@/pages/DocumentDetailPage'),
    },
  ],
}
```

### API Service Layer

Centralized API services with Axios:

```typescript
// Using a service
import { documentService } from '@/services';

const document = await documentService.getById(documentId);
```

### Type Safety

Comprehensive TypeScript types for all API interactions:

```typescript
import type { Baseline, CreateBaselineRequest } from '@/types/api';

const createBaseline = async (data: CreateBaselineRequest): Promise<Baseline> => {
  // Fully typed
};
```

### Environment Configuration

Type-safe environment configuration with validation:

```typescript
import { env } from '@/config/env';

console.log(env.apiBaseUrl); // Type-safe access
```

## Routes

### Dashboard
- `/` - Redirects to dashboard
- `/dashboard` - Main dashboard

### Documents
- `/documents` - Document list
- `/documents/upload` - Upload document
- `/documents/:documentId` - Document details

### Baselines
- `/baselines` - Baseline list
- `/baselines/create` - Create baseline
- `/baselines/:baselineId` - Baseline details

### Timelines
- `/timelines` - Timeline list
- `/timelines/draft/:draftId` - Draft timeline
- `/timelines/committed/:committedId` - Committed timeline

### Progress
- `/progress` - Progress overview
- `/progress/timeline/:timelineId` - Timeline progress

### Health Assessments
- `/health` - Health dashboard
- `/health/assessment` - Take assessment
- `/health/history` - Assessment history
- `/health/:assessmentId` - Assessment details

## API Services

### Document Service

```typescript
import { documentService } from '@/services';

// Upload document
const { documentId } = await documentService.upload(
  file,
  'Title',
  'Description',
  'type',
  (progress) => console.log(`${progress}%`)
);

// Get document
const doc = await documentService.getById(documentId);

// Get user's documents
const docs = await documentService.getUserDocuments();
```

### Baseline Service

```typescript
import { baselineService } from '@/services';

// Create baseline
const { baselineId } = await baselineService.create({
  programName: 'PhD in Computer Science',
  institution: 'University',
  fieldOfStudy: 'ML',
  startDate: '2024-09-01',
});
```

### Timeline Service

```typescript
import { timelineService } from '@/services';

// Create draft timeline
const { draftTimelineId } = await timelineService.createDraft({
  baselineId: '123',
  title: 'My Timeline',
});

// Get timeline with details
const details = await timelineService.getDraftWithDetails(draftTimelineId);

// Commit timeline
const { committedTimelineId } = await timelineService.commit({
  draftTimelineId,
  title: 'Committed Timeline',
});
```

### Progress Service

```typescript
import { progressService } from '@/services';

// Complete milestone
const { eventId } = await progressService.completeMilestone(
  milestoneId,
  '2024-01-27',
  'Completed on time'
);

// Get timeline progress
const progress = await progressService.getTimelineProgress(timelineId);
```

### Assessment Service

```typescript
import { assessmentService } from '@/services';

// Submit questionnaire
const summary = await assessmentService.submitQuestionnaire({
  responses: [
    {
      dimension: 'RESEARCH_PROGRESS',
      questionId: 'rp1',
      responseValue: 4,
    },
  ],
  assessmentType: 'self_assessment',
});

// Get latest assessment
const latest = await assessmentService.getLatest();
```

## Error Handling

API errors are automatically handled and transformed:

```typescript
try {
  await documentService.upload(file);
} catch (error) {
  // Error is typed as ApiError
  console.error(error.message);
  console.error(error.code);
}
```

## Next Steps

1. **Add UI Components**: Build reusable component library
2. **State Management**: Add Zustand stores for global state
3. **Authentication**: Implement auth flow and protected routes
4. **Forms**: Add form validation with React Hook Form
5. **UI Library**: Integrate component library (e.g., shadcn/ui)

## Development Guidelines

- All API calls go through service layer
- Use TypeScript types for all data
- Lazy load pages for code splitting
- Keep components small and focused
- Use environment config for all external values
